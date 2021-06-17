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
    Removes the prefix of a word, voweled or unvoweled.

    :param token: a string, containing the word whose prefix is to be removed
    :return: a string, containing the word without the prefix
    """
    no_pref = token[1:]
    for c in token[1:]:
        if 1456 <= ord(c) <= 1479: no_pref = no_pref[1:]
        else: break
    return no_pref


def hebrew_root(token):
    """
    Returns the root of a Hebrew word by searching for the token in Morfix.
    Verb are returned in their 3rd person masculine singular past tense form.

    :param token: a string, containing the Hebrew word whose root is to be found
    :return: a list of strings, containing all of the possible roots of the word, auto-ordered by confidence by Morfix.

    TODO: Mark POS (n, v, adj, etc.), get root of verb rather than conjugated 3MSP. See advanced_hebrew_root.
    """
    page = requests.get('https://www.morfix.co.il/' + token)
    parser = _GetRoots()
    parser.feed(page.text)
    return parser.results


def advanced_hebrew_root(token):
    """
    BETA: Marks the POS of the word and returns binyan of verb options.
    This method will eventually replace hebrew_root.

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


def _is_voweled(token):
    """
    Returns True if the token has nikkud, False otherwise.
    This allows the Aramaic root methods to operate on both voweled and unvoweled words
    so they can still work on unvoweled masekhtot.

    :param token: a string of Hebrew characters with or without nikkud
    :return: True if the token has nikkud, False otherwise.
    """
    non_alph = [1456 <= ord(c) <= 1479 for c in token]
    return not all(non_alph)


def aramaic_verb_root(token):
    """
    Returns the possible roots and binyanim of an Aramaic verb by looking it up in the dicta list.

    :param token: a string, containing the unvoweled word to look up.
    :return: a list of tuple pairs, each containing a possible root of the word and corresponding binyan.
    """
    tag = 'word' if _is_voweled(token) else 'unvoweled'
    v_entries = _verbs.find({tag: token})
    unique = set([(v['root'], v['binyan']) for v in v_entries])
    return list(unique) if unique else []


def aramaic_noun_root(token):
    """
    Returns the possible roots of an Aramaic noun by looking it up in the dicta list.

    :param token: a string, containing the unvoweled word to look up
    :return: a list, containing the possible roots of the word
    """
    tag = 'word' if _is_voweled(token) else 'unvoweled'
    n_entries = _nouns.find({tag: token})
    unique = set([n['root'] for n in n_entries])
    return list(unique) if unique else []


def identify_prefix(token, lang='all'):
    """
    Identifies whether a particular token MAY have a prefix. This does not confirm whether the token
    DOES have a prefix--only if the first consonant+vowel CONSTITUTE a possible prefix. So, for example,
    it will identify anything beginning with "קָ־" as having a possible prefix, even if it is an actual word,
    such as "קָאזָא."

    :param token: the token to be checked, a string
    :param lang: the language whose prefixes are to be checked, a string: 'heb,' 'aram,' 'all' (default)
    :return: True if there MAY be an attached prefix, False otherwise

    TODO: Merge with remove_prefix, add further rules for prefixes--
    https://en.wikipedia.org/wiki/Prefixes_in_Hebrew
    https://hebrew-academy.org.il/2013/07/18/%D7%A0%D7%99%D7%A7%D7%95%D7%93-%D7%90%D7%95%D7%AA%D7%99%D7%95%D7%AA-%D7%94%D7%A9%D7%99%D7%9E%D7%95%D7%A9/
    https://github.com/Dicta-Israel-Center-for-Text-Analysis/Talmud-Bavli-with-Nikud
    """

    aram_prefixes = ['הֲ', 'דִּ', 'דְּ', 'אַ', 'קָ']
    heb_prefixes = ['שֶׁ']
    both_prefixes = ['מִ', 'מִי', 'מֵ', 'מֵי',
                     'לְ', 'לָ', 'לַ', 'לִ', 'לֵ',
                     'כֵ', 'כָ', 'כְ', 'כִ', 'כִי',
                     'כֵּ', 'כָּ', 'כְּ', 'כִּ', 'כִּי',
                     'וְ', 'וּ',
                     'הֶָ', 'הָ', 'הַ',
                     'בֵ', 'בִ', 'בַ', 'בְ',
                     'בֵּ', 'בִּ', 'בָּ', 'בְּ']

    for p in both_prefixes:
        if token[:len(p)] == p:
            return True
    if lang == 'aram' or lang == 'all':
        for p in aram_prefixes:
            if token[:len(p)] == p:
                return True
    if lang == 'heb' or lang == 'all':
        for p in heb_prefixes:
            if token[:len(p)] == p:
                return True

    return False


def detach_prefix(token, lang='all', char=1):
    """
    BETA: Improved version of identify_prefix, see "TODO."

    Given a token, identifies possible prefix(es) and returns a list of possible words corresponding to the token.
    These words are not checked first to see if they "exist"; they only need to POSSIBLY exist, given the rules of
    prefixes.

    :param token: the token to be checked, a string
    :param lang: the language whose prefixes are to be checked, a string: 'heb,' 'aram,' 'all' (default)
    :param char: DO NOT CHANGE. In the case of multiple possible prefixes, this tracks their order.
    :return: a list of strings, which are the possible corresponding words

    TODO: After deleting identify_prefix, make variables static.

    ALGORITHM:
    1) identify, detach, and index all possible prefixes
        a. moving from right to left, individually identify if the letter-vowel combination is a possible prefix
        b. if it is a possible prefix, remove it from the word, put it as the START** of an array called "prefs,"
           and continue
        c. once a letter-vowel combination is reached that cannot be a prefix, save it as "nex" and stop (do not remove)
        d. save the remaining characters of the word into an array called "roots" and as a variable called word
    2) working FORWARD through prefs, identify if the prefix is possible based on its conjugation rules
        a. pop first item in prefs and save it as "curr"
        b. identify whether it is a valid prefix based on its own rules, with the following information:
            i. the prefix itself
            ii. the next vowel-letter combination in the word, which was saved in "nex"
            iii. the index of the current prefix = len(prefs) [if there is a ו or ה, the index must be 0]
    3) Append curr to the front of word, set nex to curr.
    4) If (2) identified curr as possible, append word to roots/
    5) Repeat from (2) until len(prefs) == 0.
    6) Return roots.

    ** This is required so that the started/end rules for ו or ה can both be identified as index = 0.
    """

    possibilities = [token]

    aram_only = ['הֲ', 'דִּ', 'דְּ', 'אַ', 'קָ']
    heb_only = ['שֶׁ']
    # two letter and tzere prefixes currently commented since I don't know if they really appear (see Wiki)
    conjunction = ['וְ', 'וּ']
    inseparable_prepositions = ['לְ', 'לָ', 'לַ', 'לִ',  # 'לֵ',
                                'כָ', 'כְ', 'כִ',  # 'כִי' ,'כֵ',
                                'כָּ', 'כְּ', 'כִּ',  # 'כֵּ', 'כִּי',
                                'בִ', 'בַ', 'בְ',  # 'בֵ',
                                'בִּ', 'בָּ', 'בְּ']  # 'בֵּ',
    mem_preposition = ['מִ', 'מֵ']  # 'מִי', 'מֵי',
    definite_article = ['הֶָ', 'הָ', 'הַ']

    pref2 = False

    if char == 1:
        for p in conjunction:
            if token[:len(p)] == p:
                possibilities.append(token[len(p):])
                pref2 = True
    for p in inseparable_prepositions:
        pass
    for p in mem_preposition:
        pass
    for p in definite_article:
        pass

    if lang == 'aram' or lang == 'all':
        for p in aram_only:
            if token[:len(p)] == p:
                return True
    if lang == 'heb' or lang == 'all':
        for p in heb_only:
            if token[:len(p)] == p:
                return True

    possibilities += detach_prefix(possibilities[1], lang, char+1) if pref2 else []

    return possibilities

