import re
import string
import nltk

from utils.deconstruct import *

"""
Brute force methods for finding all possible roots of any given word,
to be deprecated or improved upon later.
"""

aram_prefixes = ['ד', 'א', 'ק']
heb_prefixes = ['ש']
both_prefixes = ['מ', 'ל', 'כ', 'ו', 'ה', 'ב']


def _is_possible(root, lang):
    heb = hebrew_root(root) if lang != 'aram' else []
    aram_v = aramaic_verb_root(root) if lang != 'heb' else []
    aram_n = aramaic_noun_root(root) if lang != 'heb' else []
    return heb + aram_v + aram_n


def remove_possible_prefixes(token, lang='all'):
    """
    Brute forces every possibility for the prefix of the token (even if it does not necessarily have one).

    :param token: the token to remove the prefixes from
    :param lang: the proposed language of the prefix--'heb,' 'aram,' or 'all' (default)
    :return: a list of possibilities for the root of the word, if it was preceded by a prefix
    """
    if lang == 'aram':
        prefixes = aram_prefixes + both_prefixes
    elif lang == 'heb':
        prefixes = heb_prefixes + both_prefixes
    else:
        prefixes = aram_prefixes + heb_prefixes + both_prefixes

    possibilities = [token]
    root = token
    while root[0] in prefixes:
        root = remove_prefix(root)
        if _is_possible(root, lang):
            possibilities.append(root)
    return possibilities
