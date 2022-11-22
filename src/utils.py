from enum import Enum
import re


def get_gen(s):
    if re.search("(rby)|(gen 1)|(1st gen)",
                 s, re.IGNORECASE) is not None:
        return 1
    elif re.search("(gsc)|[^h](gs)|(gen 2)|(2nd gen)",
                   s, re.IGNORECASE) is not None:
        return 2
    elif re.search("(adv)|(rse)|(rs)|(frlg)|(gen 3)|(3rd gen)",
                   s, re.IGNORECASE) is not None:
        return 3
    elif re.search("(dpp)|(dp)|(hgss)|(gen 4)|(4th gen)",
                   s, re.IGNORECASE) is not None:
        return 4
    elif re.search("(bw)|(bw2)|(b2w2)|(gen 5)|(5th gen)",
                   s, re.IGNORECASE) is not None:
        return 5
    else:
        return -1
        # I don't know when Smogon fully transitioned to PS.
        # I'll assume it was gen 6


def get_tier(s):
    if (re.search("ou", s, re.IGNORECASE) is not None):
        return "OU"
    if (re.search("uu", s, re.IGNORECASE) is not None):
        return "UU"
    if (re.search("nu", s, re.IGNORECASE) is not None):
        return "NU"
    if (re.search("uber", s, re.IGNORECASE) is not None):
        return "Ubers"


class Status(Enum):
    NONE = 0
    POISON = 1
    TOXIC = 2
    PARALYSIS = 3
    BURN = 4
    FREEZE = 5


class SimplePokemon():
    '''Basic representation of Pokemon\'s HP and status'''

    def __init__(self, species, nick=""):
        self.species = species
        self.nick = species if len(nick) == 0 else nick
        self.hp = 100
        self.status = Status.NONE


class SimpleTrainer():
    '''Basic representation of each trainer and their Pokemon'''

    def __init__(self, name):
        self.name = name
        self.mons = []

    def has_pokemon(self, species, nick=""):
        nick = species if len(nick) == 0 else nick
        for mon in self.mons:
            if mon.species == species and mon.nick == nick:
                return True
        return False




