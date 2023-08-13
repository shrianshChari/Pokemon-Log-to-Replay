# Pokemon-Log-to-Replay
Convert from logs from Pokemon Online and Shoddy to replays from Pokemon Showdown

### Resources:
- [Showdown Replay Encoding](https://github.com/smogon/pokemon-showdown/blob/master/sim/SIM-PROTOCOL.md)
- [Python RegEx Cheat Sheet](https://www.geeksforgeeks.org/python-regex-cheat-sheet/)

### Plans
- [x] Turn a game into a replay by hand to explore how we would convert from log to replay
- [x] Choose a language to develop with (**Python** ~~or TypeScript~~)
- [ ] Start developing (currently testing RegEx patterns)

### Patterns to be implemented:
##### Using moves
```
Stengah used U-turn!
Earthworm's Swampert used Ice Beam!

Latias is being sent back!
Nachos's Scizor used Pursuit!
```

##### Type effectiveness
```
Floppy's spamming it used Crunch!
It's super effective!
```
```
M Dragon's Metagross used Meteor Mash!
It's not very effective...
```
```
Floppy's polaroid used Earthquake!
It had no effect on M Dragon's Claydol!
```
Maybe won't keep track of Levitate, but will probably have to worry about Volt Absorb/Water Absorb/Flash Fire.

##### Direct damage
```
Neurotica lost 286 HP! (89% of its health)
Earthworm's Swampert lost 28% of its health!
```

##### Passive damage
```
The foe's Celebi was hurt by its burn!
M Dragon's Shadow is buffeted by the sandstorm!
The foe's Palkia was hurt by poison!
```
Will have to account for Toxic turns

##### Recovery
Passive recovery
```
Floppy's nice bird restored a little HP using its Leftovers!
Vicarious restored a little HP using its Black Sludge!
```
Roost
```
Salamence used Roost!

Salamence landed on the ground!

Salamence regained health!
```
Softboiled
```
The foe's Blissey used Softboiled!
The foe's Blissey regained health!
```
Recover
```
The foe's Starmie used Recover!
The foe's Starmie regained health!
```
Will probably have to do some stuff for Synthesis and Leech Seed.

##### Abilities
```
M Dragon's M Dragon intimidates Floppy's Blaziken!
intension's Sand Stream whipped up a sandstorm!
Groudon's Drought intensified the sun's rays!
The foe's Palkia is exerting its Pressure!
Blue_Star's Poison Point activates!
```

### Things to Solve
Life Orb recoil doesn't appear in the chat
```
Earthworm sent out Tyranitar!
BKC sent out Orion! (Starmie)
Earthworm's Tyranitar's Sand Stream whipped up a sandstorm!

Start of turn 1!
Orion used Hydro Pump!
It's super effective!
Earthworm's Tyranitar lost 73% of its health!

Earthworm's Tyranitar used Crunch!
It's super effective!
Orion lost 235 HP! (90% of its health)
Orion fainted!
```
> From [BKC vs Earthworm Redux](https://www.smogon.com/forums/threads/past-gen-battle-logs.3483431); the only way that Starmie dies turn 1 is if it is holding a Life Orb, otherwise it doesn't die to 90% Crunch + 6% Sandstorm.

Wish Mechanics in Gen 5
```
Jolteon's wish came true!
```
I don't have access to Gen 5 logs at the moment, so I don't know if it tells how much a Pokemon heals by with Wish. If not, Wish mechanics could produce uncertainty in the replay, and if there's one thing I want to avoid, it's misrepresenting historic battles.
