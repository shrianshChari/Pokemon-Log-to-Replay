import re
import sys
import utils

if (len(sys.argv) < 2):
    print("Please supply a log to turn into a replay", file=sys.stderr)
    sys.exit(1)

log = open(sys.argv[1],encoding="utf-8")
log_data = log.read()
log_arr = log_data.split('\n')

current_player = -1
other_player = -1
gen = 0
players = []

is_phased = False
phase_hazard_list = []
moves_buffer = []
wishers = {0:'',1:''}


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
    nick = re.sub("[Tt]he foe\'s ", "", nick, re.IGNORECASE)
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
    global moves_buffer

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
    drought_pat = re.compile('(.*)\'s Drought intensified the sun\'s rays!')
    drizzle_pat = re.compile('(.*)\'s Drizzle made it rain!')

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
    sleep_pat = re.compile("(.*) fell asleep!")
    freeze_pat = re.compile("(.*) was frozen solid!")
    paralysis_pat = re.compile("(.*) is paralyzed! It may be unable to move!")

    encore_pat = re.compile("(.*) received an encore!")
    substitute_start_pat = re.compile("(.*) made a substitute!")
    substitute_end_pat = re.compile("(.*) substitute faded!")
    substitute_hit_pat = re.compile("(.*) substitute took the damage!")
    substitute_hit_inverted_pat = re.compile("The substitute took damage for (.*)")
    reflect_start_pat = re.compile('Reflect raised (.*) team defense!')
    reflect_end_pat = re.compile('(.*) reflect wore off!')
    protect_pat = re.compile('(.*) protected itself!')
    taunt_pat = re.compile("(.*) fell for the taunt!")
    taunt_end_pat = re.compile("(.*) taunt ended!")
    trick_item_pat = re.compile("(.*) obtained one (.*)!")
    trick_activate_pat = re.compile("(.*) switched items with (.*)!")
    focus_punch_pat = re.compile("(.*) is tightening its focus!")
    focus_sash_pat = re.compile("(.*) hung on using its Focus Sash!")
    resist_berry_pat = re.compile("(.*)'s (.*) weakened (.*) power!")
    status_berry_pat = re.compile("(.*) ate its (.*)!")
    bounced_pat = re.compile("(.*) sprang up!")
    status_cleared_lum_pat = re.compile("(.*) status cleared!")


    stealth_rock_dmg_pat = re.compile(r'Pointed stones dug into (.*)!')
    spikes_dmg_pat = re.compile("(.*) (was|is) hurt by spikes!")
    burn_dmg_pat = re.compile("(.*) (was|is) hurt by its burn!")
    poison_dmg_pat = re.compile("(.*) (was|is) hurt by poison!")
    sandstorm_dmg_pat = re.compile("(.*) (was|is) buffeted by the sandstorm!")
    leftovers_pat = re.compile("(.*) restored a little HP using its Leftovers!")
    black_sludge_pat = re.compile("(.*) restored a little HP using its Black Sludge!")

    fast_asleep_pat = re.compile("(.*) is fast asleep.")
    woke_up_pat = re.compile("(.*) woke up!")
    rest_heal_pat = re.compile("(.*) went to sleep and became healthy!")

    full_para_pat = re.compile("(.*) is paralyzed! It can't move!")
    frozen_solid_pat = re.compile("(.*) is frozen solid!")
    confused_pat = re.compile("(.*) became confused!")
    is_poisoned_pat = re.compile("(.*) is already poisoned.")
    is_parad_pat = re.compile("(.*) is already paralyzed.")
    # Don't have a replay where a Pokemon thaws out


    damage_dealt_pat = re.compile("[0-9.]+\% of")

    landed_pat = re.compile("(.*) landed on the ground!")
    heal_pat = re.compile("(.*) regained health!")
    wish_pat = re.compile("(.*)'s wish came true!")

    boosted_stat_one_level_pat = re.compile('(.*) rose!')
    lowered_stat_one_level_pat = re.compile('(.*) fell!')
    lowered_stat_two_level_pat = re.compile('(.*) sharply fell!')
    boosted_stat_two_level_pat = re.compile('(.*) sharply rose!')

    immune_pat = re.compile("It had no effect on (.*)!")
    immune_doesnot_pat = re.compile("It doesn't effect (.*)...")
    flash_fire_pat = re.compile('(.*) Flash Fire raised the power of its Fire-type moves!')
    miss_pat = re.compile('The attack (.*) missed!')
    miss_pat_avoid = re.compile('(.*) avoided the attack!')
    has_sub_pat = re.compile("(.*) already has a substitute.")
    flinch_pat = re.compile('(.*) flinched and couldn\'t move!')

    intim_pat = re.compile("(.*) intimidates (.*)")

    immune_no_info_pat = "It had no effect!"
    crit_pat = "A critical hit!"
    super_effective_pat = "It's super effective!"
    not_very_effective_pat = "It's not very effective..."
    # yes there is a typo, yes its intended
    failed_pat_typo = "But if failed!"
    failed_pat = "But it failed!"
    rain_start_pat = "It started to rain!"
    rain_stop_pat = "The rain stopped."




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
    elif chat_pat.match(line):
        match = chat_pat.search(line)
        if match:
            full_msg = [match.group(1), match.group(2)]
            if (full_msg[0] == players[0].name or
                    full_msg[0] == players[1].name):
                full_msg[0] = '☆' + full_msg[0]
            converted = f"|c|{full_msg[0]}|{full_msg[1]}"

    elif turn_start_pat.match(line):
        match = turn_start_pat.search(line)
        if match:
            if (players[0].currentmon is None or
                    players[1].currentmon is None):
                print('Error: unable to determine leads.', file=sys.stderr)
                sys.exit(1)
            converted = f"|turn|{match.group(1)}"

    elif sent_out_pat.match(line):
        converted = ""
        match = sent_out_pat.search(line)
        if match:
            if players[0].currentmon is None and players[1].currentmon is None:
                converted += "|start\n"
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
                source = ""
                if moves_buffer:
                    if moves_buffer[0] == "Baton Pass":
                        source = '|[from] Baton Pass'
                converted += (
                    rf'|switch|p{playernum + 1}a: {mon.nick}|'
                    rf'{mon.species}|{mon.approx_hp()}\/100{status}{source}'
                )
                if gen <= 2 and mon.status == utils.Status.TOXIC:
                    mon.status = utils.Status.POISON
                    converted += f'\n|-status|p{playernum + 1}a: {mon.nick}|psn|[silent]'

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
                    rf'{mon.species}|{mon.approx_hp()}\/100{status}'
                )
            else:
                print('Cannot tell who the mon is.', file=sys.stderr)
                sys.exit(1)
            is_phased = False
            for line in phase_hazard_list:
                converted = converted + '\n' + analyze_line(line)
            phase_hazard_list = []

    elif landed_pat.match(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f"|-singleturn|p{target_player+1}a: {target_mon.nick}|move: Roost"

    elif heal_pat.match(line):
        # TODO: Recognize Leech Seed 
        target_player = identify_player(line, heal_pat)
        target_mon = players[target_player].currentmon
        target_mon.heal(50.0)
        converted = f"|-heal|p{target_player+1}a: {target_mon.nick}|{target_mon.approx_hp()}\/100{target_mon.space_status()}"

    elif status_cleared_lum_pat.match(line):
        target = identify_player(line, status_cleared_lum_pat)
        target_mon = players[target].currentmon
        if target_mon.status != utils.Status.NONE:
            target_mon.status = utils.Status.NONE
            converted = f'|-curestatus|p{target + 1}a: {target_mon.nick}|{target_mon.status_string()}|[msg]'
        else:
            converted = f"|-end|p{target + 1}a: {target_mon.nick}|confusion"

    elif wish_pat.match(line):
        if gen == 5:
            raise Exception("Wish is not implemented for gen 5 logs.")
        target = identify_player(line, wish_pat)
        target_mon = players[target].currentmon
        target_mon.heal(50)
        converted = f"|-heal|p{target+1}a: {target_mon.nick}|{target_mon.approx_hp()}\/100{target_mon.space_status()}|[from] move: Wish|[wisher] {wishers[target]}"

    elif not_very_effective_pat == line:
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-resisted|p{target_player+1}a: {target_mon.nick}'

    elif boosted_stat_two_level_pat.match(line):
        target = identify_player(line, boosted_stat_two_level_pat)
        boosted_stat = utils.match_big_stat_to_small(line)
        converted = f'|-boost|p{target+1}a: {players[target].currentmon.nick}|{boosted_stat}|2'

    elif lowered_stat_two_level_pat.match(line):
        target = identify_player(line, lowered_stat_one_level_pat)
        boosted_stat = utils.match_big_stat_to_small(line)
        converted = f'|-unboost|p{target+1}a: {players[target].currentmon.nick}|{boosted_stat}|2'

    elif boosted_stat_one_level_pat.match(line):
        target = identify_player(line, boosted_stat_one_level_pat)
        boosted_stat = utils.match_big_stat_to_small(line)
        converted = f'|-boost|p{target+1}a: {players[target].currentmon.nick}|{boosted_stat}|1'

    elif lowered_stat_one_level_pat.match(line):
        target = identify_player(line, lowered_stat_one_level_pat)
        boosted_stat = utils.match_big_stat_to_small(line)
        converted = f'|-unboost|p{target+1}a: {players[target].currentmon.nick}|{boosted_stat}|1'

    elif crit_pat == line:
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-crit|p{target_player+1}a: {target_mon.nick}'

    elif failed_pat in line or failed_pat_typo in line or is_poisoned_pat.match(line) or has_sub_pat.match(line) \
         or is_parad_pat.match(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-fail|p{use_player+1}a: {use_mon.nick}|{move}'

    elif miss_pat.match(line) or miss_pat_avoid.match(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-miss|p{use_player+1}a: {use_mon.nick}|p{target_player+1}a: {target_mon.nick}'

    elif super_effective_pat == line:
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-supereffective|p{target_player+1}a: {target_mon.nick}'

    elif immune_pat.match(line) or immune_doesnot_pat.match(line) or immune_no_info_pat in line:
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-immune|p{target_player+1}a: {target_mon.nick}'

    elif damage_dealt_pat.search(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        opposing_player = int(not target_player)
        damage_done = damage_dealt_pat.search(line).group(0)
        target_mon.damage(float(damage_done[:-4]))
        converted = f"|-damage|p{target_player+1}a: {target_mon.nick}|{target_mon.approx_hp()}\/100{target_mon.space_status()}"

    elif protect_pat.match(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        # both the started protect and defended itself from a move use the same pattern we have to recognize it
        if use_mon == target_mon:
            converted = f'|-singleturn|p{target_player+1}a: {target_mon.nick}|Protect'
        else: 
            converted = f'|-activate|p{target_player+1}a: {target_mon.nick}|move: Protect'

    elif trick_activate_pat.match(line):
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-activate|p{use_player+1}a: {use_mon.nick}|move: Trick|[of] p{target_player+1}a: {target_mon.nick}'

    elif trick_item_pat.match(line):
        player = identify_player(line, trick_item_pat)
        mon = players[player].currentmon
        item = trick_item_pat.match(line).group(2)
        if mon and item:
            converted = f'|-item|p{player+1}a: {mon.nick}|{item}|[from] move: Trick'

    elif line == 'But there was no target...':
        move, use_player, target_player, use_mon, target_mon = moves_buffer
        converted = f'|-notarget|p{use_player + 1}a: {use_mon.nick}'

    elif intim_pat.match(line):
        user = identify_player(line, intim_pat)
        converted = f'|-ability|p{user+1}a: {players[user].currentmon.nick}|Intimidate|boost'
        # this has to be awful code but it works
        l = line_num + 1
        while 1:
            next_line = analyze_line(log_arr[l])
            # we might encounter a message unrelated to the game (only chat?) and we have to skip it
            if "|c|" in next_line:
                l += 1
            # or a drop message in which case its not clear body
            elif "-unboost" in next_line:
                break
            #otherwise assume it's clear body?
            else: 
                opponent = not user 
                opposing_mon = players[opponent].currentmon
                converted += "\n" + f'|-fail|p{opponent+1}a: {opposing_mon.nick}|unboost|[from] ability: Clear Body|[of] p{opponent+1}a: {opposing_mon.nick}'
                break



    elif flash_fire_pat.match(line):
        user = identify_player(line, flash_fire_pat)
        converted = (
            f"|-ability|p{user+1}a: {players[user].currentmon.nick}|Flash Fire|\n"
            f"|-start|p{user+1}a: {players[user].currentmon.nick}|Flash Fire|[silent]"
        )

    elif taunt_pat.match(line):
        player = identify_player(line, taunt_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|-start|p{player + 1}a: {mon.nick}|Taunt'
    elif taunt_end_pat.match(line):
        player = identify_player(line, taunt_end_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|-end|p{player + 1}a: {mon.nick}|Taunt'

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
                'Recover', 'Roost', 'Slack Off', 'Soft-Boiled', 'Softboiled',
                'Synthesis', 'Wish',
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
            if move == "Wish":
                wishers[use_player] = use_mon.nick

        # TODO: Implement damage, secondary effects, etc. of moves
        moves_buffer = (move, use_player, target_player, use_mon, target_mon)

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
                # TODO: this is a band aid fix, rapid spin might not remove internal hazards?
                if gen == 2:
                    damage = 12.5
                mon.damage(damage)
                status = mon.space_status()
                converted = (
                    rf'|-damage|p{player + 1}a: {mon.nick}|'
                    rf'{mon.approx_hp()}\/100{status}|[from] Spikes'
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
                    rf'{mon.approx_hp()}\/100{status}|[from] Stealth Rock'
                )

    elif sandstorm_dmg_pat.match(line):
        player = identify_player(line, sandstorm_dmg_pat)
        mon = players[player].currentmon
        if mon:
            mon.damage(6.25)
            status = mon.space_status()
            converted = (
                rf'|-damage|p{player + 1}a: {mon.nick}|'
                rf'{mon.approx_hp()}\/100{status}|[from] Sandstorm'
            )

    elif drought_pat.match(line):
        player = identify_player(line, drought_pat)
        mon = players[player].currentmon
        if mon:
            converted = (
                rf'|-weather|SunnyDay|[from] ability: Drought|'
                rf'[of] p{player + 1}a: {mon.nick}'
            )

    elif drizzle_pat.match(line):
        player = identify_player(line, drizzle_pat)
        mon = players[player].currentmon
        if mon:
            converted = (
                rf'|-weather|RainDance|[from] ability: Drizzle|'
                rf'[of] p{player + 1}a: {mon.nick}'
            )

    elif sandstream_pat.match(line):
        player = identify_player(line, sandstream_pat)
        mon = players[player].currentmon
        if mon:
            converted = (
                rf'|-weather|Sandstorm|[from] ability: Sand Stream|'
                rf'[of] p{player + 1}a: {mon.nick}'
            )
    elif line == rain_start_pat:
        converted = '|-weather|Rain Dance'
    elif line == rain_stop_pat: 
        converted = '|-weather|none'

    elif line == 'The sunlight is strong.':
        converted = '|-weather|SunnyDay|[upkeep]'

    elif line == 'Rain continues to fall.':
        converted = '|-weather|RainDance|[upkeep]'

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

    elif sleep_pat.match(line):
        player = identify_player(line, sleep_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.SLEEP
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif freeze_pat.match(line):
        player = identify_player(line, freeze_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.FREEZE
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif paralysis_pat.match(line):
        player = identify_player(line, paralysis_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.PARALYSIS
            converted = f'|-status|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif fast_asleep_pat.match(line):
        player = identify_player(line, fast_asleep_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|cant|p{player + 1}a: {mon.nick}|{mon.status_string()}'
    elif flinch_pat.match(line):
        player = identify_player(line, flinch_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|cant|p{player + 1}a: {mon.nick}|flinch'

    elif woke_up_pat.match(line):
        player = identify_player(line, woke_up_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.NONE
            converted = f'|-curestatus|p{player + 1}a: {mon.nick}|slp|[msg]'

    elif rest_heal_pat.match(line):
        player = identify_player(line, rest_heal_pat)
        mon = players[player].currentmon
        if mon:
            mon.status = utils.Status.SLEEP
            mon.heal(100)
            converted = (
                f'|-status|p{player + 1}a: {mon.nick}|slp|[from] move: Rest\n'
                f'|-heal|p{player + 1}a: {mon.nick}|{mon.approx_hp()}/100 slp|[silent]'
            )

    elif frozen_solid_pat.match(line):
        player = identify_player(line, frozen_solid_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|cant|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif full_para_pat.match(line):
        player = identify_player(line, full_para_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|cant|p{player + 1}a: {mon.nick}|{mon.status_string()}'

    elif encore_pat.match(line):
        player = identify_player(line, encore_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|-start|p{player + 1}a: {mon.nick}|Encore'

    elif focus_punch_pat.match(line):
        player = identify_player(line, focus_punch_pat)
        mon = players[player].currentmon
        if mon:
            converted = f'|-singleturn|p{player + 1}a: {mon.nick}|move: Focus Punch'

    elif focus_sash_pat.match(line):
        player = identify_player(line, focus_sash_pat)
        mon = players[player].currentmon
        converted = f'|-enditem|p{player + 1}a: {mon.nick}|Focus Sash'

    elif confused_pat.match(line):
        player = identify_player(line, confused_pat)
        mon = players[player].currentmon
        converted = f'|-start|p{player + 1}a: {mon.nick}|Confusion'        

    elif resist_berry_pat.match(line):
        player = identify_player(line, resist_berry_pat)
        mon = players[player].currentmon
        berry = resist_berry_pat.match(line).group(2)
        converted = (f'|-enditem|p{player + 1}a: {mon.nick}|{berry}|[eat]\n'
            f'|-enditem|p{player + 1}a: {mon.nick}|{berry}|[weaken]')

    elif status_berry_pat.match(line):
        player = identify_player(line, status_berry_pat)
        mon = players[player].currentmon
        berry = status_berry_pat.match(line).group(2)
        converted = f'|-enditem|p{player + 1}a: {mon.nick}|{berry}|[eat]'

    elif bounced_pat.match(line):
        player = identify_player(line, bounced_pat)
        mon = players[player].currentmon
        converted = (f'|move|p{player+1}a: {mon.nick}|Bounce||[still]\n'
            f'|-prepare|p{player+1}a: {mon.nick}|Bounce')
            
    elif substitute_start_pat.match(line):
        player = identify_player(line, substitute_start_pat)
        mon = players[player].currentmon
        if mon:
            mon.damage(25)
            converted = (
                f'|-start|p{player + 1}a: {mon.nick}|Substitute\n'
                f'|-damage|p{player + 1}a: {mon.nick}|{mon.approx_hp()}\/100{mon.space_status()}'
            )
    elif substitute_hit_pat.match(line):
        player = identify_player(line, substitute_hit_pat)
        mon = players[player].currentmon
        converted = f'|-activate|p{player+1}a: {mon.nick}|move: Substitute|[damage]'
    elif substitute_hit_inverted_pat.match(line):
        player = identify_player(line, substitute_hit_inverted_pat)
        mon = players[player].currentmon
        converted = f'|-activate|p{player+1}a: {mon.nick}|move: Substitute|[damage]'

    elif substitute_end_pat.match(line):
        player = identify_player(line, substitute_end_pat)
        mon = players[player].currentmon
        converted = f'|-end|p{player + 1}a: {mon.nick}|Substitute'
    elif reflect_start_pat.match(line):
        player = identify_player(line, reflect_start_pat)
        converted = f'|-sidestart|p{player+1}: {players[player].name}|Reflect'
    elif reflect_end_pat.match(line):
        player = identify_player(line, reflect_end_pat)
        converted = f'|-sideend|p{player+1}: {players[player].name}|Reflect'

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
                rf'{mon.approx_hp()}\/100{status}|[from] psn'
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
                rf'{mon.approx_hp()}\/100{status}|[from] brn'
            )

    elif leftovers_pat.match(line):
        player = identify_player(line, leftovers_pat)
        mon = players[player].currentmon
        if mon:
            mon.heal(6.25)
            status = mon.space_status()
            converted = (
                f'|-heal|p{player + 1}a: {mon.nick}|'
                rf'{mon.approx_hp()}\/100{status}|[from] item: Leftovers'
            )

    elif black_sludge_pat.match(line):
        player = identify_player(line, black_sludge_pat)
        mon = players[player].currentmon
        if mon:
            mon.heal(6.25)
            status = mon.space_status()
            converted = (
                f'|-heal|p{player + 1}a: {mon.nick}|'
                rf'{mon.approx_hp()}\/100{status}|[from] item: Black Sludge'
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
