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
battle_started_pat = re.compile(r"Battle between .* and .* (started)|(is underway)!", re.IGNORECASE)
mode_pat = re.compile(r"Mode: \w*", re.IGNORECASE)
tier_pat = re.compile(r"Tier: \w*", re.IGNORECASE)
turn_start_pat = re.compile(r"Start of turn \d*!?", re.IGNORECASE)
clause_pat = re.compile(r"Rule: \S*", re.IGNORECASE)
sent_out_pat = re.compile(r".* sent out .*!( \(.*\))?")
move_used_pat = re.compile(r".* used .*!")
is_watching_pat = re.compile(r".* is watching the battle.")
stopped_watching_pat = re.compile(r".* stopped watching the battle.")
chat_pat = re.compile(r".*: .*")

battle_started_line = 0
mode_line = 0
tier_line = 0
turn_start_lines = []
clause_lines = []
sent_out_lines = []
move_used_lines = []
is_watching_lines = []
stopped_watching_lines = []
chat_lines = []

gen = 0
players = []

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
        print(converted)
        converted = f"|player|p2|{players[1].name}|ethan|"
        print(converted)

        # Eventually we want to be able to change these avatars,
        # will want to figure out an interface to do so
    if mode_pat.search(line) is not None:
        converted = f"|gametype|{line.replace('Mode: ', '', 1).lower()}"
        print(converted)
    elif tier_pat.match(line) is not None:
        tier_log = line
        gen = utils.get_gen(tier_log)
        tier = utils.get_tier(tier_log)
        converted = f"|gen|{gen}"
        print(converted)
        converted = f"|tier|[Gen {gen}] {tier}"
        print(converted)
    elif clause_pat.match(line) is not None:
        converted = line.replace('Rule: ', '|rule|')
        print(converted)
    elif turn_start_pat.match(line) is not None:
        converted = line.replace('Start of turn ', '|turn|')
        print(converted)
    elif sent_out_pat.match(line) is not None:
        if players[0].currentmon is None and players[1].currentmon is None:
            print('|start')
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
        print(f'|switch|p{playernum + 1}a: {mon.nick}|{mon.species}|{mon.hp}/100')
    elif move_used_pat.match(line) is not None:
        move_used_lines.append(line)
    elif is_watching_pat.match(line) is not None:
        converted = f"|j|{line.replace(' is watching the battle.', '')}"
        print(converted)
    elif stopped_watching_pat.match(line) is not None:
        converted = f"|l|{line.replace(' stopped watching the battle.', '')}"
        print(converted)
    elif chat_pat.match(line) is not None:
        full_msg = line.split(': ', 1)
        if (full_msg[0] == players[0].name or full_msg[0] == players[1].name):
            full_msg[0] = '☆' + full_msg[0]
        converted = f"|c|{full_msg[0]}|{full_msg[1]}"
        print(converted)


print(move_used_lines[0:5])

