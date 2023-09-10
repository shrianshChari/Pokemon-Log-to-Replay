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

ardorin-boudouche-gen4ou - Focus Sash<br>
crashingboombang-mangonation-gen3ou - Focus Punch, Flinch<br>
highimpulse-ciele-gen3ou - Clear Body<br>
highimpulse-ciele-gen4ou - Bounce<br>
pimpmygo-Malekith-gen3ou - Non-modern Wish<br>
pimpmygo-Malekith-gen4ou - Rain Dance<br>
pasy-annoyer-gen4-nu / hvislysettaross-dolcefarniente-gen4ou - Chesto Berry / Resist Berry<br>


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

Leech Seed
```
THE DADDY KITH's Bronzong's health is sapped by leech seed.
```
Pain Split
```
NEGRITO BANANA's Rotom-W used Pain Split!
The battlers shared their pain!
```

Recoil
```
Sweepage's SoulWind is damaged by recoil!
```

Tier ambiguity
Sometimes the tier shows up just as "Overused" which causes replays to be generated with "Gen -1 OU"
Battle logs effected: boudouche-absurd-gen5ou, negritobanana-sweepage-gen5ou, nicedognicedog-alf-gen5ou

Errors
ardorin-boudouche-gen5ou and boudouche-absurd-gen4ou have whirlwind broken, `Cannot tell who the mon is.`

Better Build system for building working html files with replays
