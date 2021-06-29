import re
from itertools import permutations

from utils.hebrew import *

"""
Methods to take Hebrew and Aramaic words and give other possible spellings. Namely, maleh/haser and flipped nikkud.
"""


def order_nikkud(token):
    """
    Returns the same word but with nikkud on same letter reordered when more than one appears, such as dagesh-patach
    versus patach-dagesh. This is necessary because words that look identical will not be registered as such if their
    nikkud is technically in a different order.

    :param token: a string, the token to be rearranged
    :return: a list with the reordered possibilities
    """
    if len(token) <= 1:
        return [token]

    found = re.search('[' + alphabet + ']', token[1:])
    if not found: return [token]

    letter = token[0]
    nik = token[1:found.end()]

    all_orderings = []
    for order in permutations(nik):
        #print(order)
        vowels = ''.join(order)
        first = letter + vowels
        all_orderings += [first + rest for rest in order_nikkud(token[found.end():])]

    return all_orderings


def haser_to_maleh(token):
    """
    Receives a haser token with nikkud and returns that same token in its maleh form.

    :param token: a string, the token, in haser form
    :return: a string containing the token in maleh form

    https://he.wikipedia.org/wiki/%D7%9B%D7%AA%D7%99%D7%91_%D7%9E%D7%9C%D7%90
    https://hebrew-academy.org.il/topic/hahlatot/missingvocalizationspelling/
    https://hebrew-academy.org.il/2017/06/17/%D7%9B%D7%9C%D7%9C%D7%99-%D7%94%D7%9B%D7%AA%D7%99%D7%91-%D7%94%D7%9E%D7%9C%D7%90-%D7%94%D7%9B%D7%9C%D7%9C%D7%99%D7%9D-%D7%94%D7%97%D7%93%D7%A9%D7%99%D7%9D-%D7%A1%D7%99%D7%95%D7%95%D7%9F/
    """
    pass


def maleh_to_haser(token):
    """
    Receives a maleh token with nikkud and returns that same token in its haser form.

    :param token: a string, the token, in maleh form
    :return: a string containing the token in haser form
    """
    pass


def swap_gender(noun):
    """
    Switches the gender of a noun from masculine/feminine singular/plural to the corresponding opposite.

    :param noun: string, a noun in feminine/masculine form with nikkud
    :return: string, the noun in opposite form; None if the word is not identified as a noun

    TODO: Account for whether second to last letter has dagesh(?)
    """
    # Feminine
    if noun[-4:] == shva + 'תָא':
        return noun[:-5] + long_nikkud[0] + 'א'
    elif noun[-4:] == long_nikkud[0] + 'תָא':
        return noun[:-5] + long_nikkud[1] + 'י'
    # Masculine
    elif noun[-2:] == long_nikkud[0] + 'א':
        return noun[:-3] + shva + 'תָא'
    elif noun[-2:] == long_nikkud[1] + 'י':
        return noun[:-3] + long_nikkud[0] + 'תָא'
    return None


def sub_kamatz(text):
    """
    Replaces the alternatively coded kamatz (utils.hebrew.other_kamatz) for the normal one.

    :param text: the text to substitute the weird kamatz in
    :return: the text with the weird kamatz substituted for the normal one
    """
    return re.sub(other_kamatz, long_nikkud[0], text)
