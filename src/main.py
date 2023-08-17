import re
import sys
import utils

if (len(sys.argv) < 2):
    print("Please supply a log to turn into a replay", file=sys.stderr)
    sys.exit(1)

log = open(sys.argv[1])
log_data = log.read()
log_arr = log_data.split('\n')

current_player = -1
other_player = -1
gen = 0
players = []

is_phased = False
phase_hazard_list = []


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
        elif (nick.lower() != p1_mon.nick.lower()
                and nick.lower() == p2_mon.nick.lower()):
            # Player 1 is the current player
            current_player = 1
        else:
            print(
                'Error: indistinguishable who is who from the given information.',
                file=sys.stderr)
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
        elif (nick.lower() != p1_mon.nick.lower()
                and nick.lower() == p2_mon.nick.lower()):
            # Player 1 is the foe
            other_player = 1
        else:
            print(
                'Error: indistinguishable who is who from the given information.',
                file=sys.stderr)
            sys.exit(1)
        current_player = int(not other_player)


def identify_player(line: str, pat: re.Pattern) -> int:
    match = pat.match(line)
    player = -1
    if match:
        first_group = match.group(1)
        if ("the foe's" in first_group.lower()):
            # Find the foe
            if current_player == -1:
                nick = re.sub('the foe\'s ', '', first_group, re.IGNORECASE)
                find_foe(nick)
            player = other_player
        elif (f"{players[0].name}'s".lower() in first_group.lower()):
            player = 0
        elif (f"{players[1].name}'s".lower() in first_group.lower()):
            player = 1
        else:
            if current_player == -1:
                find_current(first_group)
            player = current_player
    return player


def analyze_line(line: str) -> str:
    global players
    global gen
    global is_phased
    global phase_hazard_list

    # Compiling regex patterns for efficiency

    battle_started_pat = re.compile(
        "Battle between (.*) and (.*) (started|is underway)!", re.IGNORECASE)
    mode_pat = re.compile(r"Mode: (\w*)", re.IGNORECASE)
    tier_pat = re.compile(r"Tier: (\w*)", re.IGNORECASE)
    turn_start_pat = re.compile(r"Start of turn (\d*)!?", re.IGNORECASE)
    clause_pat = re.compile(r"Rule: (.*)", re.IGNORECASE)
    sent_out_pat = re.compile(r"(.*) sent out (.*)!( \(.*\))?")
    extract_species_pat = re.compile(r" \((.*)\)")
    dragged_out_pat = re.compile(r"(.*) was dragged out!")
    move_used_pat = re.compile(r"(.*) used (.*)!")
    is_watching_pat = re.compile(r"(.*) is watching the battle.")
    stopped_watching_pat = re.compile(r"(.*) stopped watching the battle.")
    chat_pat = re.compile(r"(.*): (.*)")
    win_battle_pat = re.compile(r"(.*) won the battle!")
    fainted_pat = re.compile(r"(.*) fainted!")

    pursuit_pat = re.compile("(.*) is being sent back!")

    sandstream_pat = re.compile('(.*)\'s Sand Stream whipped up a sandstorm!')
    stealth_rock_set_pat = re.compile(
        'Pointed stones float in the air around (.*) team!')
    spikes_set_pat = re.compile(
        'Spikes were scattered all around the feet of (.*) team!')
    toxic_spikes_set_pat = re.compile(
        'Poison spikes were scattered all around the feet of (.*) team!')
    spin_hazards_pat = re.compile('(.*) blew away (.*)!')

    poison_pat = re.compile("(.*) was poisoned!")
    toxic_pat = re.compile("(.*) was badly poisoned!")
    burn_pat = re.compile("(.*) was burned!")

    stealth_rock_dmg_pat = re.compile(r'Pointed stones dug into (.*)!')
    spikes_dmg_pat = re.compile("(.*) (was|is) hurt by spikes!")
    burn_dmg_pat = re.compile("(.*) was hurt by its burn!")
    poison_dmg_pat = re.compile("(.*) was hurt by poison!")
    sandstorm_dmg_pat = re.compile("(.*) (was|is) buffeted by the sandstorm!")
    leftovers_pat = re.compile("(.*) restored a little HP using its Leftovers!")

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
            sent_outs = set(filter(lambda x: sent_out_pat.match(x), log_arr))
            for sent_out in sent_outs:
                match = sent_out_pat.match(sent_out)
                if match:
                    if match.group(1) == players[0].name:
                        # Player 1
                        if match.group(3):
                            species = extract_species_pat.match(match.group(3))
                            if (species):
                                players[0].add_pokemon(species.group(1),
                                                       match.group(2))
                        else:
                            players[0].add_pokemon(match.group(2))
                    else:
                        # Player 2
                        if match.group(3):
                            species = extract_species_pat.match(match.group(3))
                            if (species):
                                players[1].add_pokemon(species.group(1),
                                                       match.group(2))
                        else:
                            players[1].add_pokemon(match.group(2))
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
            if (players[0].currentmon is None or
                    players[1].currentmon is None):
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
                species = extract_species_pat.match(match.group(3))
                if species:
                    sent_out_data = [match.group(1),
                                     species.group(1),
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
                mon.toxic_turns = 0
                converted = (
                    rf'|switch|p{playernum + 1}a: {mon.nick}|'
                    rf'{mon.species}|{mon.hp}\/100{status}'
                )

    elif dragged_out_pat.match(line):
        player = identify_player(line, dragged_out_pat)
        match = dragged_out_pat.match(line)
        if match:
            nick = re.sub(".*'s ", "", match.group(1))
            mon = players[player].get_pokemon_by_nick(nick)
            if mon:
                players[player].currentmon = mon
                status = mon.space_status()
                mon.toxic_turns = 0
                converted = (
                    rf'|drag|p{player + 1}a: {mon.nick}|'
                    rf'{mon.species}|{mon.hp}\/100{status}'
                )
            else:
                print('Cannot tell who the mon is.', file=sys.stderr)
                sys.exit(1)
            is_phased = False
            for line in phase_hazard_list:
                converted = converted + '\n' + analyze_line(line)
            phase_hazard_list = []

    elif move_used_pat.match(line):
        use_player = identify_player(line, move_used_pat)
        match = move_used_pat.match(line)
        move = ''
        if match:
            target_player = -1
            move = match.group(2)
            # Deals with moves that target the user
            self_target = {
                # Setup moves
                'Acid Armor', 'Agility', 'Amnesia', 'Autotomize', 'Barrier',
                'Belly Drum', 'Bulk Up', 'Calm Mind', 'Coil', 'Cosmic Power',
                'Cotton Guard', 'Curse', 'Defend Order', 'Defense Curl',
                'Double Team', 'Dragon Dance', 'Focus Energy', 'Growth',
                'Harden', 'Hone Claws', 'Howl', 'Iron Defense', 'Light Screen',
                'Meditate', 'Minimize', 'Nasty Plot', 'Quiver Dance',
                'Reflect', 'Rock Polish', 'Sharpen', 'Shell Smash',
                'Shift Gear', 'Stockpile', 'Swords Dance', 'Tail Glow',
                'Withdraw', 'Work Up',
                # Healing moves
                'Heal Order', 'Milk Drink', 'Moonlight', 'Morning Sun', 'Rest',
                'Recover', 'Roost', 'Slack Off', 'Soft-Boiled', 'Synthesis',
                'Wish',
                # Miscellaneous
                'Assist', 'Baton Pass', 'Camouflage', 'Copycat',
                'Destiny Bond', 'Detect', 'Endure', 'Healing Wish', 'Imprison',
                'Lunar Dance', 'Magic Coat', 'Magnet Rise', 'Metronome',
                'Power Trick', 'Protect', 'Recycle', 'Refresh', 'Sleep Talk',
                'Snatch', 'Substitute',
            }
            if (move in self_target):
                target_player = use_player
            else:
                target_player = int(not use_player)
            use_mon = players[use_player].currentmon
            target_mon = players[target_player].currentmon
            if use_mon and target_mon:
                converted = (
                    f'|move|p{use_player + 1}a: {use_mon.nick}|{move}|'
                    f'p{target_player + 1}a: {target_mon.nick}'
                )

            if move in {'Whirlwind', 'Roar', 'Dragon Tail', 'Circle Throw'}:
                is_phased = True

        # TODO: Implement damage, secondary effects, etc. of moves

    elif fainted_pat.match(line):
        player = identify_player(line, fainted_pat)
        currentmon = players[player].currentmon
        if currentmon:
            converted = (
                f'|faint|p{player + 1}a: {currentmon.nick}'
            )

    elif is_watching_pat.match(line):
        match = is_watching_pat.search(line)
        if match:
            remove_brackets = re.sub('\\[.*\\]', '', match.group(1))
            converted = f"|j|{remove_brackets}"

    elif stopped_watching_pat.match(line):
        match = stopped_watching_pat.search(line)
        if match:
            remove_brackets = re.sub('\\[.*\\]', '', match.group(1))
            converted = f"|l|{remove_brackets}"

    elif chat_pat.match(line):
        match = chat_pat.search(line)
        if match:
            full_msg = [match.group(1), match.group(2)]
            if (full_msg[0] == players[0].name or
                    full_msg[0] == players[1].name):
                full_msg[0] = '☆' + full_msg[0]
            converted = f"|c|{full_msg[0]}|{full_msg[1]}"

    elif spikes_dmg_pat.match(line):
        if is_phased:
            phase_hazard_list.append(line)
        else:
            player = identify_player(line, spikes_dmg_pat)
            mon = players[player].currentmon
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
                converted = (
                    rf'|-damage|p{player + 1}a: {mon.nick}|'
                    rf'{mon.hp}\/100{status}|[from] Spikes'
                )

    elif stealth_rock_dmg_pat.match(line):
        if is_phased:
            phase_hazard_list.append(line)
        else:
            player = identify_player(line, stealth_rock_dmg_pat)
            mon = players[player].currentmon
            if mon:
                mon.damage(utils.stealth_rock_damage(mon, gen))
                status = mon.space_status()
                converted = (
                    rf'|-damage|p{player + 1}a: {mon.nick}|'
                    rf'{mon.hp}\/100{status}|[from] Stealth Rock'
                )

    elif sandstorm_dmg_pat.match(line):
        player = identify_player(line, sandstorm_dmg_pat)
        mon = players[player].currentmon
        if mon:
            mon.damage(6.25)
            status = mon.space_status()
            converted = (
                rf'|-damage|p{player + 1}a: {mon.nick}|'
                rf'{mon.hp}\/100{status}|[from] Sandstorm'
            )

    elif sandstream_pat.match(line):
        player = identify_player(line, sandstream_pat)
        mon = players[player].currentmon
        if mon:
            converted = (
                rf'|-weather|Sandstorm|[from] ability: Sand Stream|'
                rf'[of] p{player + 1}a: {mon.nick}'
            )

    elif line == 'The sandstorm rages.':
        converted = '|-weather|Sandstorm|[upkeep]'

    elif toxic_pat.match(line):
        player = identify_player(line, toxic_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.TOXIC
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif poison_pat.match(line):
        player = identify_player(line, poison_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.POISON
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif burn_pat.match(line):
        player = identify_player(line, burn_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.BURN
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif poison_dmg_pat.match(line):
        player = identify_player(line, poison_dmg_pat)
        mon = players[player].currentmon
        if mon:
            if mon.status == utils.Status.TOXIC:
                mon.toxic_turns += 1
                mon.damage(mon.toxic_turns / 16 * 100)
            elif gen == 1:
                mon.damage(6.25)
            else:
                mon.damage(12.5)
            status = mon.space_status()
            converted = (
                f'|-damage|p{player + 1}a: {mon.nick}|'
                rf'{mon.hp}\/100{status}|[from] psn'
            )

    elif burn_dmg_pat.match(line):
        player = identify_player(line, burn_dmg_pat)
        mon = players[player].currentmon
        if mon:
            if gen == 1:
                mon.damage(6.25)
            else:
                mon.damage(12.5)
            status = mon.space_status()
            converted = (
                f'|-damage|p{player + 1}a: {mon.nick}|'
                rf'{mon.hp}\/100{status}|[from] brn'
            )

    elif leftovers_pat.match(line):
        player = identify_player(line, leftovers_pat)
        mon = players[player].currentmon
        if mon:
            mon.heal(6.25)
            status = mon.space_status()
            converted = (
                f'|-heal|p{player + 1}a: {mon.nick}|'
                rf'{mon.hp}\/100{status}|[from] item: Leftovers'
            )

    elif stealth_rock_set_pat.match(line):
        player = identify_player(line, stealth_rock_set_pat)
        if player > -1:
            converted = (
                f'|-sidestart|p{player + 1}: {players[player].name}|'
                'move: Stealth Rock'
            )

    elif spikes_set_pat.match(line):
        player = identify_player(line, spikes_set_pat)
        if player > -1:
            players[player].add_spikes()
            converted = (
                f'|-sidestart|p{player + 1}: {players[player].name}|'
                'move: Spikes'
            )

    elif toxic_spikes_set_pat.match(line):
        player = identify_player(line, toxic_spikes_set_pat)
        if player > -1:
            converted = (
                f'|-sidestart|p{player + 1}: {players[player].name}|'
                'move: Toxic Spikes'
            )

    elif spin_hazards_pat.match(line):
        player = identify_player(line, spin_hazards_pat)
        mon = players[player].currentmon
        if player > -1:
            match = spin_hazards_pat.match(line)
            if match and mon:
                converted = (
                    f'|-sideend|p{player + 1}: {players[player].name}'
                    f'|{match.group(2)}|[from] move: Rapid Spin'
                    f'|[of]: p{player + 1}a: {mon.nick}'
                )

    elif win_battle_pat.match(line):
        match = win_battle_pat.search(line)
        if match:
            converted = f"|win|{match.group(1)}"

    elif pursuit_pat.match(line):
        player = identify_player(line, pursuit_pat)
        mon = players[player].currentmon
        if mon:
            status = mon.space_status()
            converted = (
                f'|-activate|p{player + 1}a: {mon.nick}|move: Pursuit'
            )
    return converted


for line_num, line in enumerate(log_arr):
    converted = analyze_line(line)
    output(converted)
