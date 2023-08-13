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

battle_started_pat = re.compile("Battle between (.*) and (.*) (started|is underway)!",
                                re.IGNORECASE)
mode_pat = re.compile(r"Mode: (\w*)", re.IGNORECASE)
tier_pat = re.compile(r"Tier: (\w*)", re.IGNORECASE)
turn_start_pat = re.compile(r"Start of turn (\d*)!?", re.IGNORECASE)
clause_pat = re.compile(r"Rule: (.*)", re.IGNORECASE)
sent_out_pat = re.compile(r"(.*) sent out (.*)!( \(.*\))?")
move_used_pat = re.compile(r"(.*) used (.*)!")
is_watching_pat = re.compile(r"(.*) is watching the battle.")
stopped_watching_pat = re.compile(r"(.*) stopped watching the battle.")
chat_pat = re.compile(r"(.*): (.*)")
win_battle_pat = re.compile(r"(.*) won the battle!")
fainted_pat = re.compile(r"(.*) fainted!")

sandstream_pat = re.compile('(.*)\'s Sand Stream whipped up a sandstorm!')
stealth_rock_set_pat = re.compile('Pointed stones float in the air around (.*)\'s team!')
spikes_set_pat = re.compile('Spikes were scattered all around the feet of (.*)\'s team!')

stealth_rock_dmg_pat = re.compile(r'Pointed stones dug into (.*)!')
spikes_dmg_pat = re.compile("(.*) (was|is) hurt by spikes!")
burn_dmg_pat = re.compile("(.*) was hurt by its burn!")
poison_dmg_pat = re.compile("(.*) was hurt by poison!")
sandstorm_dmg_pat = re.compile("(.*) (was|is) buffeted by the sandstorm!")
leftovers_pat = re.compile("(.*) restored a little HP using its Leftovers!")

current_player = -1
other_player = -1
gen = 0
players = []


# Function that defines how I output each line
# As of now I just output to standard output
# At some point I will send input to a file
def output(str):
    print(str)


def find_current(nick):
    global current_player
    global other_player

    p1_mon = players[0].currentmon
    p2_mon = players[1].currentmon
    if (p1_mon and p2_mon):
        if (nick.lower() == p1_mon.nick.lower()
                and nick.lower() != p2_mon.nick.lower()):
            # Player 0 is the current player
            current_player = 0
        elif (p2_mon and nick.lower() == p2_mon.nick.lower()
                and nick.lower() != p2_mon.nick.lower()):
            # Player 1 is the current player
            current_player = 1
        else:
            print('Error: indistinguishable who is who from the given information.', file = sys.stderr)
            sys.exit(1)
        other_player = int(not current_player)


def find_foe(nick):
    global current_player
    global other_player

    p1_mon = players[0].currentmon
    p2_mon = players[1].currentmon
    if (p1_mon and p2_mon):
        if (nick.lower() == p1_mon.nick.lower()
                and nick.lower() != p2_mon.nick.lower()):
            # Player 0 is the foe
            other_player = 0
        elif (nick.lower() == p1_mon.nick.lower()
                and nick.lower() != p2_mon.nick.lower()):
            # Player 1 is the foe
            other_player = 1
        else:
            print('Error: indistinguishable who is who from the given information.', file = sys.stderr)
            sys.exit(1)
        current_player = int(not other_player)


for line_num, line in enumerate(log_arr):
    converted = '|'
    if battle_started_pat.match(line):
        match = battle_started_pat.match(line)
        if match:
            names = [match.group(1), match.group(2)]
            players = [utils.SimpleTrainer(name) for name in names]
            # Ok, technically, if the battle starts like
            # "Battle between Jeff and Bob and Alice and Willy started!"
            # Then this code will split it on the first 'and'
            # But in my defense, it's nearly impossible to tell which usernames
            # are which
            # Is it "Jeff and Bob and Alice" vs "Willy"?
            # Is it "Jeff" vs "Bob and Alice and Willy"?
            # Is it "Jeff and Bob" vs "Alice and Willy"?
            # idk and idc
            converted = (
                f"|player|p1|{players[0].name}|red|\n"
                f"|player|p2|{players[1].name}|blue|"
            )

        # Eventually we want to be able to change these avatars,
        # will want to figure out an interface to do so
    if mode_pat.search(line):
        match = mode_pat.search(line)
        if match:
            converted = f"|gametype|{match.group(1).lower()}"

    elif tier_pat.match(line):
        tier_log = line
        gen = utils.get_gen(tier_log)
        tier = utils.get_tier(tier_log)
        converted = (
            f"|gen|{gen}\n"
            f"|tier|[Gen {gen}] {tier}"
        )

    elif clause_pat.match(line):
        match = clause_pat.search(line)
        if match:
            converted = f"|rule|{match.group(1)}"

    elif turn_start_pat.match(line):
        match = turn_start_pat.search(line)
        if match:
            if (players[0].currentmon is None or players[1].currentmon is None):
                print('Error: unable to determine leads.', file=sys.stderr)
                sys.exit(1)
            converted = f"|turn|{match.group(1)}"

    elif sent_out_pat.match(line):
        match = sent_out_pat.search(line)
        if match:
            if players[0].currentmon is None and players[1].currentmon is None:
                output('|start')
            sent_out_data = []
            if (match.group(3)):
                sent_out_data = [match.group(1),
                                 match.group(3).replace(' (', '').replace(')', ''),
                                 match.group(2)]
            else:
                sent_out_data = [match.group(1),
                                 match.group(2),
                                 match.group(2)]

            # sent_out_data will be [playername, species, nickname]

            playernum = 0 if players[0].name == sent_out_data[0] else 1
            player = players[playernum]
            if (not player.has_pokemon(sent_out_data[1], sent_out_data[2])):
                player.add_pokemon(sent_out_data[1], sent_out_data[2])
            mon = player.get_pokemon(sent_out_data[1], sent_out_data[2])
            if mon:
                player.currentmon = mon
                status = mon.space_status()
                converted = rf'|switch|p{playernum + 1}a: {mon.nick}|{mon.species}{status}|{mon.hp}\/100'

    elif move_used_pat.match(line):
        use_player = -1
        target_player = -1
        move = ''
        if ('The foe\'s' in line):
            # The Foe
            match = re.search('The foe\'s (.*) used (.*)!', line)
            if match:
                if current_player == -1:
                    find_foe(match.group(1))
                use_player = other_player
                target_player = current_player
                move = match.group(2)
        elif (f'{players[0].name.lower()}\'s' in line.lower()):
            # Player 1
            match = re.search('.* used (.*)!', line)
            if match:
                use_player = 0
                target_player = 1
                move = match.group(1)
        elif (f'{players[1].name.lower()}\'s' in line.lower()):
            # Player 2
            match = re.search('.* used (.*)!', line)
            if match:
                use_player = 1
                target_player = 0
                move = match.group(1)
        else:
            # Current player
            match = re.search('(.*) used (.*)!', line)
            if match:
                if current_player == -1:
                    find_current(match.group(1))
                use_player = current_player
                target_player = other_player
                move = match.group(2)
        use_mon = players[use_player].currentmon
        target_mon = players[target_player].currentmon
        if use_mon and target_mon:
            converted = (
                f'|move|p{use_player + 1}a: {use_mon.nick}|{move}|'
                f'p{target_player + 1}a: {target_mon.nick}'
            )

        # TODO: Implement damage, secondary effects, etc. of moves

    elif fainted_pat.match(line):
        if re.match('The foe\'s (.*) fainted!', line):
            # Foe's Pokemon fainted
            match = re.search('The foe\'s (.*) fainted!', line)
            if (match):
                if (current_player == -1):
                    find_foe(match.group(1))
                currentmon = players[other_player].currentmon
                if currentmon:
                    converted = f'|faint|p{other_player + 1}a: {currentmon.nick}'
        elif re.match(f'{players[0].name}\'s (.*) fainted!', line,
                      re.IGNORECASE):
            # Ok, p1's mon fainted
            currentmon = players[0].currentmon
            if currentmon:
                converted = f'|faint|p1a: {currentmon.nick}'
        elif re.match(f'{players[1].name}\'s (.*) fainted!', line,
                      re.IGNORECASE):
            # Ok, p2's mon fainted
            currentmon = players[1].currentmon
            if currentmon:
                converted = f'|faint|p2a: {currentmon.nick}'
        else:
            # "Our" Pokemon fainted
            match = fainted_pat.search(line)
            if match:
                if (current_player == -1):
                    find_current(match.group(1))
                currentmon = players[current_player].currentmon
                if currentmon:
                    converted = f'|faint|p{current_player + 1}a: {currentmon.nick}'

    elif is_watching_pat.match(line):
        match = is_watching_pat.search(line)
        if match:
            converted = f"|j|{match.group(1)}"

    elif stopped_watching_pat.match(line):
        match = stopped_watching_pat.search(line)
        if match:
            converted = f"|l|{match.group(1)}"

    elif chat_pat.match(line):
        match = chat_pat.search(line)
        if match:
            full_msg = [match.group(1), match.group(2)]
            if (full_msg[0] == players[0].name or full_msg[0] == players[1].name):
                full_msg[0] = '☆' + full_msg[0]
            converted = f"|c|{full_msg[0]}|{full_msg[1]}"

    elif spikes_dmg_pat.match(line):
        match = spikes_dmg_pat.search(line)
        if match:
            player = -1
            mon = None
            if ('The foe\'s' in match.group(1)):
                # the Foe
                if (current_player == -1):
                    find_foe(match.group(1).replace('The foe\'s ', ''))
                mon = players[other_player].currentmon
                player = other_player

            elif (f'{players[0]}\'s' in match.group(1)):
                # Player 1
                mon = players[0].currentmon
                player = 0
            elif (f'{players[1]}\'s' in match.group(1)):
                # Player 2
                mon = players[1].currentmon
                player = 1
            else:
                if (current_player == -1):
                    find_current(match.group(1))
                mon = players[current_player].currentmon
                player = current_player
            if mon:
                spikes = players[player].spikes
                damage = 0
                match spikes:
                    case 1:
                        damage = 12.5
                    case 2:
                        damage = 16.6
                    case 3:
                        damage = 25
                mon.damage(damage)
                status = mon.space_status()
                converted = rf'|-damage|p{player + 1}a: {mon.nick}|{mon.hp}\/100|[from] Spikes'

    elif stealth_rock_dmg_pat.match(line):
        match = stealth_rock_dmg_pat.search(line)
        if match:
            player = -1
            mon = None
            if ('the foe\'s' in match.group(1)):
                # the Foe
                if (current_player == -1):
                    find_foe(match.group(1))
                mon = players[other_player].currentmon
                player = other_player

            elif (f'{players[0].name.lower()}\'s' in match.group(1).lower()):
                # Player 1
                mon = players[0].currentmon
                player = 0
            elif (f'{players[1].name.lower()}\'s' in match.group(1).lower()):
                # Player 2
                mon = players[1].currentmon
                player = 1
            else:
                if (current_player == -1):
                    find_current(match.group(1))
                mon = players[current_player].currentmon
                player = current_player
            if mon:
                mon.damage(utils.stealth_rock_damage(mon, gen))
                status = mon.space_status()
                converted = rf'|-damage|p{player + 1}a: {mon.nick}|{mon.hp}\/100|[from] Stealth Rock'

    elif sandstorm_dmg_pat.match(line):
        match = sandstorm_dmg_pat.search(line)
        if match:
            player = -1
            mon = None
            if ('the foe\'s' in match.group(1).lower()):
                # the Foe
                if current_player == -1:
                    nick = re.sub("the foe\'s ", '', match.group(1), re.IGNORECASE)
                    find_foe(nick)
                mon = players[other_player].currentmon
                player = other_player

            elif (f'{players[0].name.lower()}\'s' in match.group(1).lower()):
                # Player 1
                mon = players[0].currentmon
                player = 0
            elif (f'{players[1].name.lower()}\'s' in match.group(1).lower()):
                # Player 2
                mon = players[1].currentmon
                player = 1
            else:
                mon = players[current_player].currentmon
                player = current_player
            if mon:
                mon.damage(6.25)
                status = mon.space_status()
                converted = rf'|-damage|p{player + 1}a: {mon.nick}|{mon.hp}\/100|[from] Sandstorm'

    elif sandstream_pat.match(line):
        match = sandstream_pat.search(line)
        if match:
            player = -1
            mon = None
            if ('the foe\'s' in match.group(1).lower()):
                if current_player == -1:
                    nick = re.sub("the foe\'s ", '', match.group(1), re.IGNORECASE)
                    find_foe(nick)
                player = other_player
                mon = players[other_player].currentmon
            elif (f'{players[0].name.lower()}\'s' in match.group(1).lower()):
                # Player 1
                mon = players[0].currentmon
                player = 0
            elif (f'{players[1].name.lower()}\'s' in match.group(1).lower()):
                # Player 2
                mon = players[1].currentmon
                player = 1
            else:
                mon = players[current_player].currentmon
                player = current_player
            if mon:
                converted = rf'|-weather|Sandstorm|[from] ability: Sand Stream|[of] p{player + 1}a: {mon.nick}'

    elif line == 'The sandstorm rages.':
        converted = '|-weather|Sandstorm|[upkeep]'

    elif leftovers_pat.match(line):
        match = leftovers_pat.match(line)
        if match:
            player = -1
            mon = None
            if ('the foe\'s' in match.group(1).lower()):
                if current_player == -1:
                    nick = re.sub("the foe\'s ", '', match.group(1), re.IGNORECASE)
                    find_foe(nick)
                player = other_player
                mon = players[other_player].currentmon
            elif (f'{players[0].name.lower()}\'s' in match.group(1).lower()):
                # Player 1
                mon = players[0].currentmon
                player = 0
            elif (f'{players[1].name.lower()}\'s' in match.group(1).lower()):
                # Player 2
                mon = players[1].currentmon
                player = 1
            else:
                mon = players[current_player].currentmon
                player = current_player
            if mon:
                mon.heal(6.25)
                status = mon.space_status()
                converted = (
                    f'|-heal|p{player + 1}a: {mon.nick}|'
                    rf'{mon.hp}\/100{status}|[from] item: Leftovers'
                )

    elif stealth_rock_set_pat.match(line):
        match = stealth_rock_set_pat.search(line)
        if match:
            player = -1
            if players[0].name == match.group(1):
                player = 0
            else:
                player = 1
            if player > -1:
                converted = f'|-sidestart|p{player + 1}: {players[player].name}|move: Stealth Rock'

    elif spikes_set_pat.match(line):
        match = spikes_set_pat.search(line)
        if match:
            player = -1
            if players[0].name == match.group(1):
                player = 0
            else:
                player = 1
            if player > -1:
                converted = f'|-sidestart|p{player + 1}: {players[player].name}|move: Spikes'

    elif win_battle_pat.match(line):
        match = win_battle_pat.search(line)
        if match:
            converted = f"|win|{match.group(1)}"

    output(converted)


