import pymongo
import pandas as pd
from collections import defaultdict
from copy import deepcopy
import re
import json
from utils.deconstruct2 import remove_nikkud


"""
Static variables for PyMongo
"""
pswrd = ''
with open('pswrd.txt') as text: pswrd = text.read()
conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
nouns = _db['dicta-nouns']
jastrow = _db['dov-jastrow']


def _merge_dicts(*dicts):
    """
    Merges two or more dictionaries by concatenating as lists all of the different values under each key.

    :param dicts: any number of defaultdicts, with call param of -- lambda: [], and entries all being lists
    :return: a single defaultdict with the same call param that has merged all of the disparate dicts
    """
    all_keys = []
    for d in dicts:
        all_keys += list(d.keys())
    all_keys = list( dict.fromkeys(all_keys) )

    merged = defaultdict(lambda: [])
    for k in all_keys:
        for d in dicts:
            merged[k] += d[k]
    return merged


def _list_nest(lis):
    """
    Auxiliary function to expand lists contained within dicts, which may themselves contain sublists.

    :param lis: a list, possibly nested, possibly containing dicts
    :return: a 1-D list containing all of the same values as lis
    """
    if not lis:
        return []

    flat = []
    for item in lis:
        if type(item) == list:
            flat += _list_nest(lis)
        elif type(item) == dict:
            flat.append(_flatten_dict(item))
        else:
            flat.append(item)
    return flat


def _flatten_dict(dic):
    """
    Flattens a nested dictionary into a 1-D dict of lists, where each list has entries that had the same dict key.
    Note that this dumps any keys that have only dicts or lists of dicts as their values.

    :param dic: a nested dictionary
    :return: a flattened defaultdict
    """
    flat = defaultdict(lambda: [])

    for k in dic:
        if type(dic[k]) == dict:
            nest = _flatten_dict(dic[k])
            flat = _merge_dicts(flat, nest)
        elif type(dic[k]) == list:
            flat_list = _list_nest(dic[k])
            for item in flat_list:
                if type(item) == defaultdict:
                    flat = _merge_dicts(flat, item)
                else:
                    flat[k].append(item)
        else:
            flat[k].append(dic[k])

    return flat


def flatten_dict(dic):
    """
    Flattens a nested dictionary into a 1-D dict of lists, where each list has entries that had the same dict key.
    Note that this dumps any keys that have only dicts or lists of dicts as their values. This also destroys regular
    nested lists as values.
    (This is simply a wrapper for _flatten_dict, which returns the return value of that method as a regular dict.)

    :param dic: a nested dictionary
    :return: a flattened dictionary
    """
    return dict(_flatten_dict(dic))


def remove_html(entry):
    """
    Removes html from a Jastrow entry and returns as dict.

    :param entry: a document from MongoDB, as a dict
    :return: the same dict, but with HTML removed from all entries
    """
    entry2 = deepcopy(entry)

    obj_id = entry2.pop('_id')

    text = json.dumps(entry2)
    clean = re.sub(r'</*.+?>', ' ', text)

    as_dict = json.loads(clean)
    as_dict['_id'] = obj_id
    return as_dict


if __name__ == '__main__':
    matches = defaultdict(lambda: [])
    for r in nouns.distinct('root', {}):
        jas_heads = list(jastrow.find({'word': r}))

        if jas_heads == []:
            jas_heads = list(jastrow.find({'all_forms': r}))
        if jas_heads == []:
            jas_heads = list(jastrow.find({'unvoweled': remove_nikkud(r)}))
        if jas_heads == []:
            jas_heads = list(jastrow.find({'all_unvoweled': remove_nikkud(r)}))
        if jas_heads == []:
            matches[r] = ''
            continue

        for w in jas_heads:
            fl = flatten_dict(remove_html(w))
            if 'definition' in fl:
                definition = fl['definition']
            else:
                definition = ''
            matches[r] += [w['headword'], definition]

    all_matches = pd.DataFrame.from_dict(matches, orient='index')
    all_matches.to_csv('nouns.csv' , encoding='utf-8-sig')
