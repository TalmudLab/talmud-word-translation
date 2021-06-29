import pymongo
import re

import requests
import json

from utils.hebrew import *

"""
Tools for tokenizing words (Rabbinic Hebrew, Biblical Hebrew, and Aramaic) by removing prefixes and suffixes
and adding back missing letters that were removed when building constructs.
"""


# Static variables for PyMongo
pswrd = ''
with open('pswrd.txt') as text: pswrd = text.read()
conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
_verbs = _db['dicta-verbs']
_nouns = _db['dicta-nouns']


def hebrew_root(token):
    """
    Returns the root of a Hebrew word by searching for the token in Morfix. Using Morfix presents the advantage that
    Morfix automatically ranks its search results by a context-free ranking, which we can incorporate. Thus, the
    order of the list of return values is already ordered by likelihood.
    The return value of hebrew_root is a list of tuples, which contain the result from the search, followed by its POS,
    and when the POS is a verb, it also includes the binyan. This is as follows:
    - non-verb: (ROOT, POS)
    - verb:     (ROOT, POS, BINYAN)
    Returning the binyan allows one to find the shoresh later.

    :param token: a string, containing the Hebrew word whose root is to be found
    :return: a list of tuples, ordered by context-free likelihood; see description above
    """
    while True:
        try:
            page = requests.get('http://services.morfix.com/translationhebrew/TranslationService/GetTranslation/' + token, timeout=1)
            break
        except requests.ReadTimeout:
            pass
    data = json.loads(json.dumps(page.json(), indent=4))

    if data['ResultType'] == 'NoResult':
        return []

    results = []
    for w in data['Words']:
        pos = w['PartOfSpeech']
        pos = 'שֵם' if 'שֵם' in pos else pos
        binyan = ''
        if "פ'" in pos:
            binyan = pos[3:]
            pos = 'פועל'
        word = w['InputLanguageMeanings'][0][0]['DisplayText']
        results += [(word, pos)] if binyan == '' else [(word, pos, binyan)]

    return results


def remove_nikkud(token):
    alph_only = ''.join([c for c in token if not (1456 <= ord(c) <= 1479)])
    return alph_only


def hebrew_shoresh(verb, binyan):
    """
    Given a Hebrew verb in some verb form, derives the shoresh of the verb.
    Does not vowelize. Use _vowelize_shoresh on return value.

    :param verb: the verb being search, in past tense form
    :param binyan: the binyan of the verb
    :return: the root of the verb, unvoweled

    TODO: Complete _vowelize_shoresh and implement. Fix for one/two letter roots, dropped consonants/vowels.

    TODO 2: Completely replace this for a function in jastrow module that searches other verb binyanim.
    """
    verb = remove_nikkud(verb)

    # Kal/Piel/Pual
    if binyan == 'קל' or binyan == 'פיעל' or binyan == 'פועל':
        return verb

    # Nifal
    elif binyan == 'נפעל':
        return verb[1:]

    # Hifil
    elif binyan == 'הפעיל':
        if len(verb) == 3:      # הזה
            return verb
        elif len(verb) == 4:      # הִתְנָה
            return verb[1:]
        elif len(verb) == 5:      # הצדיק
            return verb[1:3] + verb[-1]

    # Hufal
    elif binyan == 'הופעל':
        if len(verb) == 3:          # הֻטָּה
            return verb
        if len(verb) == 4:          # haser
            return verb[1:]
        elif len(verb) == 5:        # maleh
            return verb[2:]

    # Hitpael
    elif binyan == 'התפעל':
        return verb[2:]

    else:
        return None


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


def _vowelize_shoresh(shoresh):
    """
    BETA: Right now simply returns the 3MSP form of the verb.

    Takes an unvowelized shoresh returned from searching the Dicta verb list and vowelizes
    it so that it can be searched in Jastrow.

    :param shoresh: the three-letter shoresh string
    :return: the vowelized shoresh, a string
    """
    vwl = _verbs.find_one({'root': shoresh, 'form': 'Past Masculine Person_3 Singular', 'binyan': 'Paal'})
    return vwl['word'] if vwl else ''


def aramaic_verb_root(token):
    """
    Returns the possible roots and binyanim of an Aramaic verb by looking it up in the dicta list.

    :param token: a string, containing the unvoweled word to look up.
    :return: a list of tuple pairs, each containing a possible root of the word and corresponding binyan.
    """
    tag = 'word' if _is_voweled(token) else 'unvoweled'
    v_entries = _verbs.find({tag: token})
    unique = set([(_vowelize_shoresh(v['root']), v['binyan']) for v in v_entries])
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


def _possible_prefixes(word, nex, possible, lang, index, last=True):
    """
    The second part of the algorithm described in detach_prefix. Returns a list of all possibilities for the word,
    with or without the possible prefixes.

    :param last: ensures that a hey can only be marked as a prefix if it is the last in the series, and that vav is
                  checked even if it is the only prefix; default is True, set to False for all but first round
    :return: a list containing the (unverified) possibilities for the word with the prefixes removed.

    TODO: Correct first letter of word when altered by prefix (e.g. 'כָּתוּב' to 'וְכָתוּב'). Create rules for definite +
          inseparable prepositions. Check for possibility of prefix with dagesh.
    """
    # NOTE: index = 0 means this is the first prefix encountered, meaning it is possible for a hey to be present
    #       index = 1 means this is the last prefix encountered, meaning is is possible for a vav to be present
    if len(possible) == 0:
        return []

    curr = possible.pop()
    is_possible = False

    # BOTH LANGUAGES #
    # Conjunction
                                              # if vav is the only prefix
    if curr in conjunction and (index == 1 or (last and len(possible) == 0)):
        is_possible = True
    # Inseparable prepositions
    if curr in inseparable_prepositions:
        if shva in nex and short_nikkud[2] in curr:     # short_nikkud[2] = chirik
            is_possible = True
        elif nex == 'י' and short_nikkud[2] in curr:
            is_possible = True
        elif (reduced_nikkud[0] in nex) or (reduced_nikkud[1] in nex) or (reduced_nikkud[2] in nex):
            for i in range(len(reduced_nikkud)):
                if reduced_nikkud[i] in nex and reduced_correspondence[i] in curr:
                    is_possible = True
        elif shva in curr:
            is_possible = True
    # Mem preposition
    if curr in mem_prepositions:
        if ((gutturals[0] in nex) or (gutturals[1] in nex) or (gutturals[2] in nex) or (gutturals[3] in nex)
                or (gutturals[4] in nex) or (definite_article[0] in nex) or (definite_article[1] in nex)
                or (definite_article[2] in nex)) and curr == 'מֵ':
            is_possible = True
        elif dagesh in nex and curr == 'מִ':
            is_possible = True
    # Definite article
    if curr in definite_article and last:
        if (nex == 'הָ' or nex == 'עָ' or nex == 'חָ' or nex == 'חֳ') and curr == 'הֶ':
            is_possible = True
        elif ('ה' in nex or 'ח' in nex) and curr == 'הַ':
            is_possible = True
        elif ('ר' in nex or 'א' in nex or 'ע' in nex) and curr == 'הָ':
            is_possible = True
        elif dagesh in nex and curr == 'הַ':
            is_possible = True

    # HEBREW #
    if lang == 'heb' or lang == 'all':
        if heb_which in curr:
            if dagesh in nex:
                is_possible = True
            elif (gutturals[0] in nex) or (gutturals[1] in nex) or (gutturals[2] in nex) or (gutturals[3] in nex) \
                    or (gutturals[4] in nex):
                is_possible = True

    # ARAMAIC #
    if lang == 'aram' or lang == 'all':
        if curr == aram_on:
            if dagesh in nex:
                is_possible = True
            elif (gutturals[0] in nex) or (gutturals[1] in nex) or (gutturals[2] in nex) or (gutturals[3] in nex) \
                    or (gutturals[4] in nex):
                is_possible = True
        if curr == aram_interrogative:
            is_possible = True
        if curr in aram_which:
            is_possible = True
        if curr == aram_intense:
            is_possible = True

    possible_word = [word] if is_possible else []
    return possible_word + _possible_prefixes(curr + word, curr, possible, lang, len(possible), last=False)


def detach_prefix(token, lang='all'):
    """
    https://en.wikipedia.org/wiki/Prefixes_in_Hebrew
    https://hebrew-academy.org.il/2013/07/18/%D7%A0%D7%99%D7%A7%D7%95%D7%93-%D7%90%D7%95%D7%AA%D7%99%D7%95%D7%AA-%D7%94%D7%A9%D7%99%D7%9E%D7%95%D7%A9/
    https://github.com/Dicta-Israel-Center-for-Text-Analysis/Talmud-Bavli-with-Nikud

    Given a token, identifies possible prefix(es) and returns a list of possible words corresponding to the token.
    These words are not checked first to see if they "exist"; they only need to POSSIBLY exist, given the rules of
    prefixes. Note that this method requires the token to have nikkud.

    :param token: the token to be checked, a string
    :param lang: the language whose prefixes are to be checked, a string: 'heb,' 'aram,' 'all' (default)
    :return: a list of strings, which are the possible corresponding words

    ALGORITHM:
    [detach_prefix]
    1) identify, detach, and index all possible prefixes
        a. moving from right to left, individually identify if the letter-vowel combination is a possible prefix
        b. if it is a possible prefix, remove it from the word, append to an array called "possible,"
           and continue
        c. once a letter-vowel combination is reached that cannot be a prefix, save it as "nex" and stop (do not remove)
        d. save the remaining characters of the word into a string in an array called "roots" and as
           a variable called "word"
    [_possible_prefixes]
    2) working BACKWARD through prefs, identify if the prefix is possible based on its conjugation rules
        a. pop last item in prefs and save it as "curr"
        b. identify whether it is a valid prefix based on its own rules, with the following information:
            i. the prefix itself
            ii. the next vowel-letter combination in the word, which was saved in "nex"
            iii. the index of the current prefix = len(prefs) [with the exception of hey]
    3) If (2) identified curr as possible, append word to roots.
    4) Append curr to the front of word, set nex to curr.
    5) Repeat from (2) until len(prefs) == 0.
    6) Return roots.

    TODO: Distinguish Biblical Hebrew from Rabbinic Hebrew in lang.
    """

    word = token

    prefixes = all_prefixes if lang == 'all' else (heb_all if lang == 'heb' else aram_all)

    possible = []
    nex = ''

    done = False
    while len(word) > 1:
        for i in range(1, len(word)):
            if word[i] in alphabet:
                if word[:i] in prefixes:
                    possible.append(word[:i])
                    word = word[i:]
                else:
                    done = True
                    nex = word[:i]
                break
            elif i == len(word) - 1:
                done = True
        if done:
            break

    # If, after the possible prefixes have been removed, the first letter of word does not have nikkud, nex is set
    # to '', so this next line accounts for that.
    nex = nex if len(nex) != 0 else word[0]

    # If the first letters look like prefixes but aren't, they won't be recognized as prefixes and therefore won't be
    # returned as part of the word. This makes sure that the original token is registered as a possibility, then removes
    # it if it's duplicated.
    possibilities = [token] + _possible_prefixes(word, nex, possible, lang, len(possible))

    return possibilities


def remove_object(word):
    """
    Removes the direct object suffix of a verb or preposition.

    :param word: string, the verb or preposition
    :return: string, the verb or prepisition with the direct object suffix removed.
    """
    return
