import pymongo
import re

from utils.hebrew import *

# FOR NAIVE TOP-N #
from utils.deconstruct2 import *
from utils.respell import *
# FOR NAIVE TOP-N #

"""
Tools for searching and retrieving Jastrow entries.
"""

# Static variables for PyMongo
conn_str = 'mongodb+srv://dov-db:RSzloZinprCNScX2@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
_jastrow = _db['jastrow']


# Words that do not need to be processed and should map directly to specific RIDs.
static_words = {
    'מַאי': 'M00023'
    # etc.
}


def naive_lookup(word):
    entries = _jastrow.find({'headword': {'$regex': r'.*' + word + r'.*'}})
    valid = []
    for e in entries:
        just_head = re.sub(r'[^' + alphabet + ''.join(all_nikkud) + ']+', '', e['headword'])
        just_head = re.sub('\s+', '', just_head)
        if just_head == word:
            valid.append(e)
    return [e['headword'] for e in valid]


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
        for w in order_nikkud(i):
            direct = naive_lookup(w)
            heads += direct[:(N - len(heads))]
            heads = list(set(heads))
            if len(heads) == N:
                return heads
    # Dicta noun search
    for i in deconstructed:
        aram_nouns = aramaic_noun_root(i)
        for w in aram_nouns:
            for n in order_nikkud(w):
                n_entries = naive_lookup(n)
                heads += n_entries[:(N - len(heads))]
                heads = list(set(heads))
                if len(heads) == N:
                    return heads
    # Dicta verb search
    for i in deconstructed:
        aram_verbs = aramaic_verb_root(i)
        for w in aram_verbs:
            print(w)
            for v in order_nikkud(w[0]):
                print(v)
                v_entries = naive_lookup(v)
                heads += v_entries[:(N - len(heads))]
                heads = list(set(heads))
                if len(heads) == N:
                    return heads
    # Hebrew search
    for i in deconstructed:
        heb = hebrew_root(i)
        for w in heb:
            for h in order_nikkud(w[0]):
                h_entries = naive_lookup(h)
                heads += h_entries[:(N - len(heads))]
                heads = list(set(heads))
                if len(heads) == N:
                    return heads

    return heads
