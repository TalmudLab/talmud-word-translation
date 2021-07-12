from utils.hebrew import *

"""
A collection of all suffixes used in conjugating Aramaic nouns, verbs, and prepositions for a direct/indirect object,
possessive, etc.
"""

# Possessives
# (As it turns out, unnecessary, since these are already present in the dicta data set)
pos_sing_noun = list(dict.fromkeys( [
    short_nikkud[2] + 'י', short_nikkud[0] + 'אי',      # 1S
    long_nikkud[0] + 'ך' + shva,                        # 2MS
    short_nikkud[2] + 'יך' + shva,                      # 2FS
    long_nikkud[1] + 'יה' + dagesh,                     # 3MS
    short_nikkud[0] + 'ה' + dagesh,                     # 3FS
    short_nikkud[0] + 'ן', short_nikkud[2] + 'ין',      # 1P
    'כוֹן', 'כו' + dagesh,                               # 2MP
    'כִי', 'כֵין',                                        # 2FP
    'הוֹן', 'הו' + dagesh,                               # 3MP
    'הִי', 'הֵין'                                         # 3FP
] ))

pos_plur_noun = list(dict.fromkeys( [
    short_nikkud[0] + 'אי',                                                                         # 1S
    short_nikkud[0] + 'יך' + shva,                                                                  # 2MS
    short_nikkud[2] + 'יך' + shva, short_nikkud[0] + 'י' + shva + 'יכ' + short_nikkud[2] + 'י',     # 2FS
    long_nikkud[1] + 'יה' + dagesh, 'ה' + short_nikkud[2] + 'י',                                    # 3MS
    short_nikkud[0] + 'ה' + long_nikkud[0] + 'א',                                                   # 3FS
    short_nikkud[2] + 'ין',                                                                         # 1P
    short_nikkud[0] + 'י' + shva + 'יכ' + short_nikkud[2] + 'ו' + dagesh,                           # 2MP
    short_nikkud[0] + 'י' + shva + 'יכ' + short_nikkud[2] + 'י',                                    # 2FP
    short_nikkud[0] + 'י' + shva + 'יהוֹן', short_nikkud[0] + 'י' + shva + 'יהו' + dagesh,           # 3MP
    short_nikkud[0] + 'י' + shva + 'יה' + short_nikkud[2] + 'י'
] ))

all_possessives = list( dict.fromkeys(pos_sing_noun + pos_plur_noun) )


# Direct objects
obj_sing_verb = list(dict.fromkeys( [
    short_nikkud[0] + 'ן', short_nikkud[0] + 'נ' + short_nikkud[2] + 'י',               # 1S
    long_nikkud[0] + 'ך' + shva,                                                        # 2MS
    short_nikkud[2] + 'יך' + shva,                                                      # 2FS
    long_nikkud[1] + 'יה' + dagesh,                                                     # 3MS
    short_nikkud[0] + 'ה' + dagesh,                                                     # 3FS
    short_nikkud[0] + 'ן', short_nikkud[2] + 'ינ' + dagesh + short_nikkud[0] + 'ן',     # 1P
    'כוֹן',                                                                              # 2MP
    short_nikkud[2] + 'נ' + shva + 'הו' + dagesh, short_nikkud[2] + 'ינ' + dagesh + 'ו' + dagesh + 'ן',  # 3MP
    short_nikkud[2] + 'נ' + shva + 'ה' + short_nikkud[2] + 'י', short_nikkud[2] + 'ינ' + dagesh + short_nikkud[2] + 'ין'  # 3FP
] ))

obj_pl_verb = list(dict.fromkeys( [
    short_nikkud[0] + 'ן', short_nikkud[0] + 'נ' + short_nikkud[2] + 'י',               # 1S
    long_nikkud[0] + 'ך' + shva,                                                      # 2MS
    short_nikkud[2] + 'יך' + shva,                                                    # 2FS
    long_nikkud[1] + 'יה' + dagesh,                                                     # 3MS
    short_nikkud[0] + 'ה' + dagesh,                                                     # 3FS
    short_nikkud[0] + 'ן', short_nikkud[2] + 'ינ' + dagesh + short_nikkud[0] + 'ן',     # 1P
    'כוֹן',                                                                              # 2MP
    short_nikkud[2] + 'נ' + shva + 'הו' + dagesh, short_nikkud[2] + 'ינ' + dagesh + 'ו' + dagesh + 'ן',  # 3MP
    short_nikkud[2] + 'נ' + shva + 'ה' + short_nikkud[2] + 'י', short_nikkud[2] + 'ינ' + dagesh + short_nikkud[2] + 'ין'  # 3FP
] ))

all_objs = list( dict.fromkeys(obj_sing_verb + obj_pl_verb) )
