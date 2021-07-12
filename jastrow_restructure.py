import pymongo
import re
from utils.hebrew import *
import time

"""
Alters the (customized) Jastrow database in the following ways, in order to make headword-finding operations easier:
1. Adds a 'word' field, containing the word from the headword, without the extraneous markings.
2. Adds an 'unvoweled' field, containing the headword without vowels.
3. Adds a 'more_forms' field, containing entries from content --> senses --> index --> grammar --> binyan_form
    - NOTE: does not preserve the 'verbal_stem' field, which can be unreliable (e.g. the 'binyan_form' field
    contains some nouns)
4. Alters the 'word', 'more_forms', 'plural_form', and 'alt_headwords' fields so that all nikkud is in the same order.
5. Adds an 'all_forms' field, containing an array that combines the fields in (4).
6. Created an 'all_unvoweled' field, containing (5) without nikkud.

NOTE: Sometimes, Jastrow shortens words that appear in the other forms (e.g. "אִידְּ׳" for "אִידְּוִיל"). These must be fixed
manually, but they are small in number. After running this script, simply aggregate all docs that have entries in the
'more_forms' field and find and replace. 
"""

jas = 0
with open('pswrd.txt') as text:
    pswrd = text.read()
    conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
    client = pymongo.MongoClient(conn_str)
    db = client['bavli']
    jas = db['dov-jastrow']


def order_nikkud(head):
    """
    Takes a Hebrew word, and orders the nikkud within that word as follows:
    1. The letter
    2. The shin/sin dot, if present
    3. The dagesh, if present
    4. All other nikkud
    It also substitutes the strange long kamatz with its regular counterpart.

    :param head: the headword
    :return: the restructured word
    """
    head = head.replace(other_kamatz, long_nikkud[0]) + '.'  # Ensures that if the last char is a vowel, the loop still
                                                             # runs one more time.
    word = ''
    nik = []
    for c in head:
        if c in alphabet or c == '.':
            if shin in nik:
                word += nik.pop(nik.index(shin))
            if sin in nik:
                word += nik.pop(nik.index(sin))
            if dagesh in nik:
                word += nik.pop(nik.index(dagesh))
            if holam in nik:
                word += nik.pop(nik.index(holam))
            if len(nik) > 0:
                word += ''.join(nik)
                nik = []
            word += c if c != '.' else ''
        else:
            nik.append(c)
    return word


def strip_nikkud(token):
    """
    Takes a Hebrew word and strips the nikkud.

    :param token: the word, a string
    :return: the word without nikkud, a string
    """
    alph_only = ''.join([c for c in token if not (1456 <= ord(c) <= 1479)])
    return alph_only


def word_only(head):
    """
    Takes a headword and strips the non-Hebrew/nikkud characters

    :param head: the headword
    :return: the headword without numbers, roman numerals, etc.
    """
    just_word = re.sub(r'[^' + alphabet + ''.join(all_nikkud) + other_kamatz + ']+', '', head)
    just_word = re.sub(r'\s+', '', just_word)
    return just_word


# After some point, the Mongo connection will time out; just re-run the script when that happens.
if __name__ == '__main__':
    docs = jas.find({'more_forms': {'$exists': False}})
    ###docs = jas.find({'renewed': {'$exists': False}})

    for d in docs:
        # (1) and (2)
        word = order_nikkud( word_only(d['headword']) )
        no_nik = strip_nikkud(word)

        jas.update_one({'rid': d['rid']},
                       {'$set':
                            {'word': word,
                             'unvoweled': no_nik}})

        # (3)
        new_forms = []
        for c in d['content']['senses']:
            if 'grammar' in c:
                new_forms += c['grammar']['binyan_form']
        new_forms = [order_nikkud(w.strip()) for w in new_forms]
        new_forms = [w for w in new_forms if w != '']

        jas.update_one({'rid': d['rid']},
                       {'$set':
                            {'more_forms': new_forms}})

        # (4)
        ordered_pl = [order_nikkud(w) for w in d['plural_form']]
        ordered_alt = [order_nikkud(w) for w in d['alt_headwords']]

        jas.update_one({'rid': d['rid']},
                       {'$set':
                            {'plural_form': ordered_pl,
                             'alt_headwords': ordered_alt}})

        # (5)
        all_forms = [word] + ordered_alt + ordered_pl + new_forms

        jas.update_one({'rid': d['rid']},
                       {'$set':
                            {'all_forms': all_forms}})

        # (6)
        all_unvoweled = [strip_nikkud(w) for w in all_forms]
        all_unvoweled = list(dict.fromkeys(all_unvoweled))

        jas.update_one({'rid': d['rid']},
                       {'$set':
                            {'all_unvoweled': all_unvoweled}})

        # Renewed tag
        ###jas.update_one({'rid': d['rid']}, {'$set': {'renewed': True}})
