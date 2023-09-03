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
Damage via leech seed
```
THE DADDY KITH's Bronzong's health is sapped by leech seed.
```
Focus punch tightening

```
Snorlax is tightening its focus!
```

"Static" Recovery via Rest and \< gen 5 wish, healing wish
```
The healing wish came true!
THE DADDY KITH's Conkeldurr regained health!
Jirachi's wish came true!
```

##### Abilities
```
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

Baton Pass
```
The foe's Zapdos used Baton Pass!
Snorlax used Body Slam!
It's not very effective...
The foe's Tyranitar's substitute took the damage!
```

Passive recovery
```
THE DADDY KITH's Bronzong's health is sapped by leech seed.
```
Weather reliant recovery?

Better Build system for building working html files with replays
