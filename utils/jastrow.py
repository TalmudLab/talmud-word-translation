import pymongo

from utils.deconstruct2 import *
from collections import Counter

"""
Tools for searching and retrieving Jastrow entries.
"""

# Static variables for PyMongo
pswrd = ''
with open('pswrd.txt') as text: pswrd = text.read()
conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
_jastrow = _db['dov-jastrow']


# Words that do not need to be processed and should map directly to specific RIDs.
static_words = {
    'מַאי': 'M00023'
    # etc.
}


def naive_lookup(word, vow=True):
    if word == '':  return []
    if vow:
        # Having a two-step process ensures that the results are ranked by whether they are the headword or another form
        heads_only = [e['headword'] for e in _jastrow.find({'word': word})]
        other_forms = [e['headword'] for e in _jastrow.find({'all_forms': word})]
    else:
        heads_only = [e['headword'] for e in _jastrow.find({'unvoweled': word})]
        other_forms = [e['headword'] for e in _jastrow.find({'all_unvoweled': word})]
    return list( dict.fromkeys(heads_only + other_forms) )


def naive_top_n(word, N=3):
    """
    An extremely naive entry searcher, intended merely as a proof-of-concept, not for practical use.
    The method uses naive lookup on different constructions of 'word' and returns the top N matching entries.
    The "top N" are ranked by category:
    1. In Jastrow directly.
    2. Top entries from dicta nouns (since there are fewer nouns than verbs)
    3. Top entries from dicta verbs
    4. Top entries from Morfix.
    5. Top entries from dicta nouns, minus nikkud.
    6. Top entries from dicta verbs, minus nikkud.
    The word is first put through respell.order_nikkud, and if more than one spelling is returned, the method returns
    the top N for each spelling. Then its possible prefixes are removed, with the ranking choosing the shortest among
    the possibilities as top rank.

    :param word: The word to search.
    :return: a list of top three Jastrow headwords.
    """
    heads = []

    deconstructed = detach_prefix(word)

    # Naive search
    for i in deconstructed:
        direct = naive_lookup(i)
        heads += direct[:(N - len(heads))]
        heads = list( dict.fromkeys(heads) )
        if len(heads) == N:
            return heads
    # Dicta noun search
    for i in deconstructed:
        aram_nouns = aramaic_noun_root(i)
        for w in aram_nouns:
            n_entries = naive_lookup(w)
            heads += n_entries[:(N - len(heads))]
            heads = list( dict.fromkeys(heads) )
            if len(heads) == N:
                return heads
    # Dicta verb search
    for i in deconstructed:
        aram_verbs = aramaic_verb_root(i)
        for w in aram_verbs:
            v_entries = naive_lookup(w[0])
            heads += v_entries[:(N - len(heads))]
            heads = list( dict.fromkeys(heads) )
            if len(heads) == N:
                return heads
    # Hebrew search
    for i in deconstructed:
        heb = hebrew_root(i)
        for w in heb:
            h_entries = naive_lookup(w[0])
            heads += h_entries[:(N - len(heads))]
            heads = list( dict.fromkeys(heads) )
            if len(heads) == N:
                return heads

    return heads


def smart_naive_search(word):
    """
    An improved, but still naive, searcher. The first step in negotiating between an intelligent context-based
    language model statistical ranker, and the naive algorithm. Like the previous, it looks up all constructions if
    necessary, but not in every case.

    :param word: The word to search.
    :return: a list of Jastrow headwords.

    NOTE: The assumptions used here are false. For example:
    אותו = him
    אותו = his letter
    But the latter will be the only return under this model.
    """

    aram_deconstructed = detach_prefix(word, lang='aram')
    njaal = naive_jas_and_aram_lookup(aram_deconstructed)
    if njaal:
        return njaal

    heb_deconstructed = detach_prefix(word, lang='heb')
    heads = []
    # Hebrew search needs to be improved upon. Morfix gives many extra, less likely words that must be left out.
    # Since the ranking is context independent but takes into account nikkud, I have arbitrarily chosen to drop
    # all except the top 3 results.
    # Given the possibility of there not being a prefix, the top results are those that appear the most in the lists.
    for i in heb_deconstructed:
        heb = hebrew_root(i)
        for w in heb:
            heads += naive_lookup(w[0])
    if heads:
        return [i[0] for i in Counter(heads).most_common(3)]

    aram_no_vowel = [remove_nikkud(w) for w in aram_deconstructed]
    njaal2 = naive_jas_and_aram_lookup(aram_no_vowel, vow=False)
    if njaal2:
        return njaal2

    return []


def naive_jas_and_aram_lookup(aram_deconstructed, vow=True):
    # Given the nikkud, if an entry (or entries) in Jastrow matches (or match) exactly, they should be returned on spot,
    # as they must be correct.
    heads = []

    for i in aram_deconstructed:
        heads += naive_lookup(i, vow)
    if heads:
        return heads

    # The same rule applies for the Dicta searches. Noun search comes first, though, because verbs can look like nouns.
    # Dicta noun search
    for i in aram_deconstructed:
        aram_nouns = aramaic_noun_root(i)
        for w in aram_nouns:
            heads += naive_lookup(w, vow)
    if heads:
        return list(dict.fromkeys(heads))
    # Dicta verb search
    for i in aram_deconstructed:
        aram_verbs = aramaic_verb_root(i)
        for w in aram_verbs:
            heads += naive_lookup(w[0], vow)
    if heads:
        return list(dict.fromkeys(heads))

    return []