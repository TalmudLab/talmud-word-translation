import pymongo
import re

import requests
from html.parser import HTMLParser

from collections import defaultdict

"""
Tools for tokenizing words (Rabbinic Hebrew, Biblical Hebrew, and Aramaic) by removing prefixes and suffixes
and adding back missing letters that were removed when building constructs.
"""


# Static variables for PyMongo
conn_str = 'mongodb+srv://dov-db:RSzloZinprCNScX2@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
_verbs = _db['dicta-verbs']
_nouns = _db['dicta-nouns']


class _GetRoots(HTMLParser):
    """
    Extends the HTMLParser object and handles retrieving word roots from a Morfix webpage.
    """
    def __init__(self):
        super().__init__()
        self.root = False
        self.results = []

    def handle_starttag(self, tag, attrs):
        if attrs and attrs[0][1] == 'Translation_spTop_heToen':
            self.root = True

    def handle_data(self, data):
        if self.root:
            self.results.append(re.sub('\xa0', '', data))
            self.root = False


class _AdvancedGetRoots(HTMLParser):
    """
    BETA: Returns extra information about the roots as a defaultdict, see below, "advanced_hebrew_root"
    Extends the HTMLParser object and handles retrieving word roots from a Morfix webpage.
    """
    def __init__(self):
        super().__init__()
        self.is_root = False
        self.is_pos = False
        self.root = ''
        self.results = defaultdict(lambda: [])

    def handle_starttag(self, tag, attrs):
        if attrs and attrs[0][1] == 'Translation_spTop_heToen':
            self.is_root = True
        if attrs and attrs[0][1] == 'Translation_sp2Top_heToen':
            self.is_pos = True

    def handle_data(self, data):
        if self.is_root:
            self.root = re.sub('\xa0', '', data)
            self.is_root = False
        elif self.is_pos:
            pos = re.sub('\s*.\'\s*', '', data)
            pos = re.sub('\s\s+', '', pos)
            pos = pos if pos != '' else 'other'
            self.results[pos] += [self.root]
            self.is_pos = False


def remove_prefix(token):
    """
    Removes the prefix of a word. Since these are always one character,
    it simply eliminates the first letter.

    :param token: a string, containing the unvoweled word whose prefix is to be removed
    :return: a string, containing the word without the prefix
    """
    return token[1:]


def hebrew_root(token):
    """
    Returns the root of a Hebrew word by searching for the token in Morfix.
    Verb are returned in their 3rd person masculine singular past tense form.

    :param token: a string, containing the Hebrew word whose root is to be found
    :return: a list of strings, containing all of the possible roots of the word, auto-ordered by confidence by Morfix.

    TODO: Mark POS (n, v, adj, etc.), get root of verb rather than conjugated 3MSP.
    """
    page = requests.get('https://www.morfix.co.il/' + token)
    parser = _GetRoots()
    parser.feed(page.text)
    return parser.results


def advanced_hebrew_root(token):
    """
    BETA: Marks the POS of the word and returns binyan of verb options.

    Returns the root of a Hebrew word by searching for the token in Morfix.
    Verb are returned in their 3rd person masculine singular past tense form.

    :param token: a string, containing the Hebrew word whose root is to be found
    :return: a dict of lists, whose keys are POS tags and valuess are lists containing all of the possible
             roots of the word, auto-ordered by confidence by Morfix. Verbs are formatted as tuple pairs
             like in aramaic_verb_root.

    TODO: format verbs as tuple pairs
    """
    page = requests.get('https://www.morfix.co.il/' + token)
    parser = _AdvancedGetRoots()
    parser.feed(page.text)
    return dict(parser.results)


def aramaic_verb_root(token):
    """
    Returns the root and binyan of an Aramaic verb by looking it up in the dicta list.

    :param token: a string, containing the unvoweled word to look up.
    :return: a list of tuple pairs, each containing a possible root of the word and corresponding binyan.
    """
    v_entries = _verbs.find({'unvoweled': token})
    unique = set([(v['root'], v['binyan']) for v in v_entries])
    return list(unique) if unique else []


def aramaic_noun_root(token):
    """
    Returns the root of an Aramaic noun by looking it up in the dicta list.

    :param token: a string, containing the unvoweled word to look up
    :return: a list, containing the possible roots of the word
    """
    n_entries = _nouns.find({'unvoweled': token})
    unique = set([n['root'] for n in n_entries])
    return list(unique) if unique else []
