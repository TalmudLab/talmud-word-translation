import pymongo

import requests
from html.parser import HTMLParser

"""
Tools for tokenizing words (Rabbinic Hebrew, Biblical Hebrew, and Aramaic) by removing prefixes and suffixes
and adding back missing letters that were removed when building constructs.
"""


"""
The static variables used in multiple functions.
"""
conn_str = 'mongodb+srv://dov-db:RSzloZinprCNScX2@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
_verbs = _db['dicta-verbs']
_nouns = _db['dicta-nouns']


class _GetRoot(HTMLParser):
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


def remove_prefix(token):
    """
    Removes the prefix of a word. Since these are always one character,
    it simply eliminates the first letter.

    :param token: a string, containing the word whose prefix is to be removed
    :return: a string, containing the word without the prefix
    """
    return token[1:]


def hebrew_root(token):
    """
    Returns the root of a Hebrew word by searching for the token in Morfix.
    Verb are returned in their 3rd person masculine singular past tense form.

    :param token: a string, containing the Hebrew word whose root is to be found
    :return: a list, containing all of the possible roots of the word, auto-ordered by confidence by Morfix
    """
    page = requests.get('https://www.morfix.co.il/' + token)
    parser = _GetRoot()
    parser.feed(page.text)
    return parser.results


def aramaic_verb_root(token):
    """
    Returns the 3rd person masculine singular past tense version of an Aramaic verb by looking it up in the dicta list.
    The reason it returns the 3MSP conjugation of the word is that this is the word to look up in the Jastrow.

    :param token: a string, containing the word to look up.
    :return: a string, containing the 3rd person masculine singular past tense version of the verb.

    TODO: Actually return 3MSP instead of root. Use find(X) in order to return all possibilities.
    """
    v_entry = _verbs.find_one({'unvoweled': token})
    return v_entry['root']


def aramaic_noun_root(token):
    """
    Returns the root of an Aramaic noun by looking it up in the dicta list.

    :param token: a string, containing the word to look up.
    :return: a string, containing the noun root of the word.

    TODO: use find(X) in order to return all possibilities.
    """
    n_entry = _nouns.find_one({'unvoweled': token})
    return n_entry['root']