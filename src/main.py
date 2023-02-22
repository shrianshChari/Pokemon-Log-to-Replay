import re
import sys

import utils

if (len(sys.argv) < 2):
    print("Please supply a log to turn into a replay", file=sys.stderr)
    sys.exit(1)

log = open(sys.argv[1])
log_data = log.read()
log_arr = log_data.split('\n')

# Compiling regex patterns for efficiency
battle_started_pat = re.compile(r"Battle between .* and .* (started)|(is underway)!",
                                re.IGNORECASE)
mode_pat = re.compile(r"Mode: \w*", re.IGNORECASE)
tier_pat = re.compile(r"Tier: \w*", re.IGNORECASE)
turn_start_pat = re.compile(r"Start of turn \d*!?", re.IGNORECASE)
clause_pat = re.compile(r"Rule: \S*", re.IGNORECASE)
sent_out_pat = re.compile(r".* sent out .*!( \(.*\))?")
move_used_pat = re.compile(r".* used .*!")
is_watching_pat = re.compile(r".* is watching the battle.")
stopped_watching_pat = re.compile(r".* stopped watching the battle.")
chat_pat = re.compile(r".*: .*")
win_battle = re.compile(r".* won the battle!")

move_used_lines = []

current_player = -1
gen = 0
players = []


# Function that defines how I output each line
# As of now I just output to standard output
# At some point I will send input to a file
def output(str):
    print(str)


for line_num in range(len(log_arr)):
    line = log_arr[line_num]
    if battle_started_pat.search(line) is not None:
        battle_started_log = line.replace("Battle between ", "", 1)
        battle_started_log = battle_started_log.replace(" started!", "", 1)
        battle_started_log = battle_started_log.replace(" is underway!", "", 1)

        names = battle_started_log.split(' and ', 1)
        players = [utils.SimpleTrainer(name) for name in names]
        # Ok, technically, if the battle starts like
        # "Battle between Jeff and Bob and Alice and Willy started!"
        # Then this code will split it on the first 'and'
        # But in my defense, it's nearly impossible to tell which usernames are which
        # Is it "Jeff and Bob and Alice" vs "Willy"?
        # Is it "Jeff" vs "Bob and Alice and Willy"?
        # Is it "Jeff and Bob" vs "Alice and Willy"?
        # idk and idc
        converted = f"|player|p1|{players[0].name}|ethan|"
        output(converted)
        converted = f"|player|p2|{players[1].name}|ethan|"
        output(converted)

        # Eventually we want to be able to change these avatars,
        # will want to figure out an interface to do so
    if mode_pat.search(line) is not None:
        converted = f"|gametype|{line.replace('Mode: ', '', 1).lower()}"
        output(converted)
    
    elif tier_pat.match(line) is not None:
        tier_log = line
        gen = utils.get_gen(tier_log)
        tier = utils.get_tier(tier_log)
        converted = f"|gen|{gen}"
        output(converted)
        converted = f"|tier|[Gen {gen}] {tier}"
        output(converted)
    
    elif clause_pat.match(line) is not None:
        converted = line.replace('Rule: ', '|rule|')
        output(converted)
    
    elif turn_start_pat.match(line) is not None:
        if (players[0].currentmon is None or players[1].currentmon is None):
            print('Error: unable to determine leads.', file=sys.stderr)
            sys.exit(1)
        converted = line.replace('Start of turn ', '|turn|')
        output(converted)

    elif sent_out_pat.match(line) is not None:
        if players[0].currentmon is None and players[1].currentmon is None:
            output('|start')
        sent_out_data = line.split(' sent out ', 1)
        if (re.search('! \\(.*\\)', sent_out_data[1]) is not None):
            sent_out_data[1] = sent_out_data[1].split('! (', 1)
            sent_out_data.append(sent_out_data[1][1])
            sent_out_data[1] = sent_out_data[1][0]
            sent_out_data[2] = sent_out_data[2][0:len(sent_out_data[2]) - 1]
        else:
            sent_out_data[1] = sent_out_data[1][0:len(sent_out_data[1]) - 1]
            sent_out_data.append(sent_out_data[1])

        # sent_out_data will be [playername, species, nickname]

        playernum = 0 if players[0].name == sent_out_data[0] else 1
        player = players[playernum]
        if (not player.has_pokemon(sent_out_data[1], sent_out_data[2])):
            player.add_pokemon(sent_out_data[1], sent_out_data[2])
        mon = player.get_pokemon(sent_out_data[1], sent_out_data[2])
        player.currentmon = mon
        output(f'|switch|p{playernum + 1}a: {mon.nick}|{mon.species}|{mon.hp}/100')

    elif move_used_pat.match(line) is not None:
        if (re.match('The foe\'s .* used .*!', line) is not None):
            # Have to figure out who "the foe" is
            line = line.replace('The foe\'s ', '', 1)
            line_components = line.split(' used ', 1)
            line_components[1] = line_components[1].replace("!", "")
            if (current_player == -1):
                if (line_components[0].lower() == players[0].currentmon.nick.lower()
                        and line_components[0].lower() != players[1].currentmon.nick.lower()):
                    # Player 0 is the foe, so Player 1 is the current player
                    current_player = 1
                elif (line_components[0].lower() == players[1].currentmon.nick.lower()
                        and line_components[0].lower() != players[0].currentmon.nick.lower()):
                    # Player 1 is the foe, so Player 0 is the current player
                    current_player = 0
                else:
                    print('Error: indistinguishable who is who from the given information.', file = sys.stderr)
                    sys.exit(1)
            other_player = int(not current_player)
            converted = f'|move|p{other_player + 1}a: {players[other_player].currentmon.nick}|{line_components[1]}|p{current_player + 1}a: {players[current_player].currentmon.nick}'
            output(converted)
        elif (re.match(f'{players[0].name}\'s .* used .*!', line,
                       re.IGNORECASE) is not None):
            # Ok, p1 did it
            line = re.sub(f'{players[0].name}\'s ', '', line)
            line_components = line.split(' used ', 1)
            output(line_components)
            line_components[1] = line_components[1].replace("!", "")
            converted = f'|move|p1a: {players[0].currentmon.nick}|{line_components[1]}|p2a: {players[1].currentmon.nick}'
            output(converted)
        elif (re.match(f'{players[0].name}\'s .* used .*!', line,
                       re.IGNORECASE) is not None):
            # Ok, p2 did it
            line = re.sub(f'{players[0].name}\'s ', '', line)
            line_components = line.split(' used ', 1)
            line_components[1] = line_components[1].replace("!", "")
            output(line_components)
            converted = f'|move|p2a: {players[1].currentmon.nick}|{line_components[1]}|p1a: {players[0].currentmon.nick}'
            output(converted)
        else:
            # Have to figure out who "the foe" isn't
            line = line.replace('The foe\'s ', '', 1)
            line_components = line.split(' used ', 1)
            line_components[1] = line_components[1].replace("!", "")
            if (current_player == -1):
                if (line_components[0].lower() == players[0].currentmon.nick.lower()
                        and line_components[0].lower() != players[1].currentmon.nick.lower()):
                    # Player 0 is the current player
                    current_player = 0
                elif (line_components[0].lower() == players[1].currentmon.nick.lower()
                        and line_components[0].lower() != players[0].currentmon.nick.lower()):
                    # Player 1 is the current player
                    current_player = 1
            other_player = int(not current_player)
            converted = f'|move|p{current_player + 1}a: {players[current_player].currentmon.nick}|{line_components[1]}|p{other_player + 1}a: {players[other_player].currentmon.nick}'
            output(converted)
        
        move_used_lines.append(line)
        # TODO: Implement damage, secondary effects, etc. of moves

    elif is_watching_pat.match(line) is not None:
        converted = f"|j|{line.replace(' is watching the battle.', '')}"
        output(converted)

    elif stopped_watching_pat.match(line) is not None:
        converted = f"|l|{line.replace(' stopped watching the battle.', '')}"
        output(converted)

    elif chat_pat.match(line) is not None:
        full_msg = line.split(': ', 1)
        if (full_msg[0] == players[0].name or full_msg[0] == players[1].name):
            full_msg[0] = '☆' + full_msg[0]
        converted = f"|c|{full_msg[0]}|{full_msg[1]}"
        output(converted)

    elif win_battle.match(line) is not None:
        converted = f"|win|{line.replace(' won the battle!', '')}"
        output(converted)


print(move_used_lines[0:5])

