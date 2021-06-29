import pymongo
import re

import requests
import json

from utils.hebrew import *
from utils.respell import *
from utils.deconstruct2 import *

"""
A module containing classes that deal with individual units of ideas, namely chunks, sentences, and words.
Mainly a way to consolidate and restructure deconstruct2.
"""

def _break_sentences(chunk, soft=True):
    """
    Takes a punctuated chunk of text and breaks it into individual sentences.

    :param chunk: the punctuated chunk of text, a string
    :param soft: whether to count soft breaks (colons and semicolons) as EOS markers, a bool; defalts to True
    :return: the individual sentences, a list of Sentences
    """
    punc = r'(.*?[!\.\?:;][…׳״]*)' if soft else r'(.*?(!|\.|\?)[…׳״]*)'
    pattern = re.compile(punc)
    return [Sentence(s) if s[0] != ' ' else Sentence(s[1:]) for s in pattern.split(chunk) if s != '']


class Word:
    """
    A class that contains individual words. Its default value is the word itself, and also stores the
    language of the word and the POS, if known. Methods of deconstruction can be called on it directly
    to get different spellings, orderings, etc.
    """
    def __init__(self, word, lang='u', pos='u'):
        """
        :param word: The word itself, a string
        :param lang: The language of the word, if known; a string. Defaults to 'u' according to the following code:
            - 'u' = unknown
            - 'a' = Aramaic
            - 'rh' = Rabbinic Hebrew
            - 'bh' = Biblical Hebrew
        :param pos: The POS of the word, if knownl a string. Defaults to 'u' according to the following code:
            - 'u' = unknown
            - 'v' = verb
            - 'n' = noun
            - 'j' = adjective
            - 'd' = adverb
            - 'p' = preposition
            - 'c' = conjunction
        """
        self._lang = lang
        self._pos = pos
        self._word = sub_kamatz(word)
        self.orders = order_nikkud(word)

    def __str__(self):
        return self._word

    def __getitem__(self, loc):
        return self._word[loc]

    def __len__(self):
        return len(self._word)

    def set_pos(self, pos):
        """
        Use to set the POS to a new value, if the POS is discovered or recalculated.

        :param pos: a string, the new POS (see code in __init__)
        """
        self._pos = pos

    def set_lang(self, lang):
        """
        Use to set the language to a new value, if the language is discovered or recalculated.

        :param lang: a string, the new language (see code in __init__)
        """
        self._lang = lang

    def spellings(self):
        """
        Returns the possible spellings of the word from maleh/haser form.
        TODO: complete
        """
        return

    def no_nikkud(self):
        """
        Returns the word without nikkud.
        """
        alph_only = ''.join([c for c in self._word if not (1456 <= ord(c) <= 1479)])
        return alph_only


class Sentence:
    """
    A class that contains individual sentences. It does so by acting as a collection of Words.
    """

    def __init__(self, sentence, context='g', lang='u'):
        """
        :param sentence: The sentence itself, a string, punctuated with nikkud.
        :param: context: The context of the sentence, 'g' for gemara and 'm' for mishna; defaults to 'g.'
        :param lang: The language of the sentence as a whole, if known; a string. Defaults to 'u' according to the
        following code:
            - 'u' = unknown
            - 'a' = Aramaic
            - 'rh' = Rabbinic Hebrew
            - 'bh' = Biblical Hebrew
        """
        self._lang = lang
        self._context = context
        self._original = sentence

    def __str__(self):
        return self._original

    def __getitem__(self, loc):
        return self._sentence[loc]

    def __len__(self):
        return len(self._sentence)


class Chunk:
    """
    A class that contains a full text chunk, the largest single-idea textual unit.
    """
    def __init__(self, chunk, context):
        """
        :param sentence: The sentence itself, a string, punctuated with nikkud.
        :param: context: The context of the sentence, 'g' for gemara and 'm' for mishna; defaults to 'g.'
        """
        self._context = context
        self._original = chunk

        self.sentences = _break_sentences(chunk)

    def __str__(self):
        return self._original

    def __getitem__(self, loc):
        return self._sentence[loc]

    def __len__(self):
        return len(self._sentence)