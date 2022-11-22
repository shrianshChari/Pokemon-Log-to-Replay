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
battle_started_pat = re.compile("Battle between .* and .* (started)|(is underway)!", re.IGNORECASE)
mode_pat = re.compile("Mode: \\w*", re.IGNORECASE)
tier_pat = re.compile("Tier: \\w*", re.IGNORECASE)
turn_start_pat = re.compile("Start of turn \\d*!?", re.IGNORECASE)
clause_pat = re.compile("Rule: \\S*", re.IGNORECASE)
sent_out_pat = re.compile(".* sent out .*!( \\(.*\\))?")
move_used_pat = re.compile(".* used .*!")
is_watching_pat = re.compile(".* is watching the battle.")
stopped_watching_pat = re.compile(".* stopped watching the battle.")
chat_pat = re.compile(".*: .*")

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

for line_num in range(len(log_arr)):
    line = log_arr[line_num]
    if battle_started_pat.search(line) is not None:
        battle_started_line = line_num
    if mode_pat.search(line) is not None:
        mode_line = line_num
    elif tier_pat.match(line) is not None:
        tier_line = line_num
    elif clause_pat.match(line) is not None:
        clause_lines.append(line_num)
    elif turn_start_pat.match(line) is not None:
        turn_start_lines.append(line_num)
    elif sent_out_pat.match(line) is not None:
        sent_out_lines.append(line)
    elif move_used_pat.match(line) is not None:
        move_used_lines.append(line)
    elif is_watching_pat.match(line) is not None:
        is_watching_lines.append(line)
    elif stopped_watching_pat.match(line) is not None:
        stopped_watching_lines.append(line)
    elif chat_pat.match(line) is not None:
        chat_lines.append(line)

battle_started_log = log_arr[battle_started_line].replace("Battle between ", "", 1)
battle_started_log = battle_started_log.replace(" started!", "", 1)
battle_started_log = battle_started_log.replace(" is underway!", "", 1)

players = battle_started_log.split(' and ', 1)
# Ok, technically, if the battle starts like
# "Battle between Jeff and Bob and Alice and Willy started!"
# Then this code will split it on the first 'and'
# But in my defense, it's nearly impossible to tell which usernames are which
# Is it "Jeff and Bob and Alice"?
# Is it "Bob and Alice and Willy"?
# idk and idc

print(f"Player 1: {players[0]}; Player 2: {players[1]}")

mode_log = log_arr[mode_line].replace("Mode: ", "", 1).lower()
print(mode_log)

tier_log = log_arr[tier_line]
gen = utils.get_gen(tier_log)
tier = f"[Gen {gen}] {utils.get_tier(tier_log)}"
print(tier)

clauses = [log_arr[i].replace("Rule: ", "") for i in clause_lines][1:]
print(clauses)

print(sent_out_lines[0:5])
print(move_used_lines[0:5])
print(is_watching_lines[0:5])
print(stopped_watching_lines[0:5])
print(chat_lines[0:5])


