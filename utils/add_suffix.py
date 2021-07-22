from utils.suffixes import *

sof = {
    'ך': 'כ',
    'ם': 'מ',
    'ן': 'נ',
    'ף': 'פ',
    'ץ': 'צ'
}


def add_suffix(verb):
    """
    Takes a verb conjugated in any form with nikkud and returns the verb conjugated with all possible
    direct-object suffixes.

    :param verb: a string
    :return: a lsit of strings containing the conjugated forms
    """
    part = verb
    for l in sof:
        part = part.replace(l, sof[l])

    conj = []
    for s in all_objs:
        conj.append(part + s)

    return conj