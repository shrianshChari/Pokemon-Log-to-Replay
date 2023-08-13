from enum import Enum
import pandas as pd
import re
from typing import Union


def get_gen(s: str) -> int:
    if re.search("(bw)|(bw2)|(b2w2)|(gen 5)|(5th gen)|(Black)|(White)|(5G)",
                 s, re.IGNORECASE) is not None:
        return 5
    elif re.search("(dpp)|(dp)|(hgss)|(gen 4)|(4th gen)|(Diamond)|(Pearl)|(Platinum)|(Heart[ ]?Gold)|(Soul[ ]?Silver)|(4G)",
                   s, re.IGNORECASE) is not None:
        return 4
    elif re.search("(adv)|(rse)|[^e](rs)|(frlg)|(gen 3)|(3rd gen)|(Ruby)|(Sapphire)|(Emerald)|(Fire[ ]?Red)|(Leaf[ ]?Green)|(3G)",
                   s, re.IGNORECASE) is not None:
        return 3
    elif re.search("(gsc)|[^h](gs)|(gen 2)|(2nd gen)|(Gold)|(Silver)|(Crystal)|(2G)",
                   s, re.IGNORECASE) is not None:
        return 2
    elif re.search("(rby)|(gen 1)|(1st gen)|(Red)|(Blue)|(Yellow)|(1G)",
                   s, re.IGNORECASE) is not None:
        return 1
    else:
        return -1
        # I don't know when Smogon fully transitioned to PS.
        # I'll assume it was gen 6


def get_tier(s: str) -> str:
    if re.search("ou", s, re.IGNORECASE) is not None or re.search('overused', s, re.IGNORECASE):
        return "OU"
    if re.search("uu", s, re.IGNORECASE) is not None or re.search('underused', s, re.IGNORECASE):
        return "UU"
    if re.search("nu", s, re.IGNORECASE) is not None or re.search('neverused', s, re.IGNORECASE):
        return "NU"
    if (re.search("uber", s, re.IGNORECASE) is not None):
        return "Ubers"
    # Matches none
    return "AG"



class Status(Enum):
    NONE = 0
    POISON = 1
    TOXIC = 2
    PARALYSIS = 3
    BURN = 4
    FREEZE = 5
    FAINT = 6


class SimplePokemon():
    '''Basic representation of Pokemon\'s HP and status'''

    def __init__(self, species: str, nick: str = ""):
        self.species = species
        # Handling Rotom formes
        match self.species:
            case 'Rotom-W':
                self.species = 'Rotom-Wash'
            case 'Rotom-H':
                self.species = 'Rotom-Heat'
            case 'Rotom-C':
                self.species = 'Rotom-Mow'
            case 'Rotom-F':
                self.species = 'Rotom-Frost'
            case 'Rotom-S':
                self.species = 'Rotom-Fan'
        self.nick = species if len(nick) == 0 else nick
        self.hp = 100
        self.status = Status.NONE
        self.toxic_turns = 0

    def damage(self, amt: float) -> None:
        self.hp -= amt
        if self.hp <= 0:
            self.status = Status.FAINT
            self.hp = 0

    def heal(self, amt: float) -> None:
        self.hp += amt
        if self.hp >= 100:
            self.hp = 100

    def status_string(self) -> str:
        if self.status == Status.POISON:
            return "psn"
        elif self.status == Status.TOXIC:
            return "tox"
        elif self.status == Status.PARALYSIS:
            return "par"
        elif self.status == Status.BURN:
            return "brn"
        elif self.status == Status.FREEZE:
            return "frz"
        elif self.status == Status.FAINT:
            return "fnt"
        return ""

    def space_status(self) -> str:
        if self.status == Status.NONE:
            return ""
        else:
            return " " + self.status_string()


class SimpleTrainer():
    '''Basic representation of each trainer and their Pokemon'''

    def __init__(self, name: str):
        self.name = name
        self.mons = []
        self.currentmon: SimplePokemon | None = None

        # Only need Spikes and T-Spikes bc they are the only ones
        # whose damage output is dependent on the number of layers,
        # which need to be tracked. SR is a fixed percentage.
        self.spikes = 0
        self.toxic_spikes = 0

    def has_pokemon(self, species: str, nick: str = ""):
        nick = species if len(nick) == 0 else nick
        for mon in self.mons:
            if mon.species == species and mon.nick == nick:
                return True
        return False

    def get_pokemon(self, species: str, nick: str = "") -> \
            Union[SimplePokemon, None]:
        nick = species if len(nick) == 0 else nick
        for mon in self.mons:
            if mon.species == species and mon.nick == nick:
                return mon
        return None

    def add_pokemon(self, species: str, nick: str = "") -> None:
        nick = species if len(nick) == 0 else nick
        if (not self.has_pokemon(species, nick)):
            self.mons.append(SimplePokemon(species, nick))

    def add_spikes(self) -> None:
        if (self.spikes < 3):
            self.spikes += 1

    def add_toxic_spikes(self) -> None:
        if (self.toxic_spikes < 2):
            self.toxic_spikes += 1

    def remove_hazards(self) -> None:
        self.spikes = 0
        self.toxic_spikes = 0


def stealth_rock_damage(mon: SimplePokemon, gen: int) -> float:
    df = pd.read_csv('./pokemon.csv')
    if (not mon or not mon.species):
        return 0
    col = 'sr_gen4' if gen == 4 else 'sr_gen5'
    output = 100 * df[df['battle_name'] == mon.species.lower()][col].item()
    return output
