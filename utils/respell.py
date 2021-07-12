import re
from itertools import permutations

from utils.hebrew import *

"""
Methods to take Hebrew and Aramaic words and give other possible spellings.
"""


def sub_kamatz(text):
    """
    Replaces the alternatively coded kamatz (utils.hebrew.other_kamatz) for the normal one.

    :param text: the text to substitute the weird kamatz in
    :return: the text with the weird kamatz substituted for the normal one
    """
    return re.sub(other_kamatz, long_nikkud[0], text)


def heb_plural(word):
    """
    Replaces the gemara's Hebrew plural suffix [nun] with modern Hebrew's equivalent

    :param word: the word in plural form, a string
    """
    return word[:-1] + 'ם'
