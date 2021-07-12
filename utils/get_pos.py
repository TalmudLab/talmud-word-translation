from collections import defaultdict


def _merge_dicts(*dicts):
    """
    Merges two or more dictionaries by concatenating as lists all of the different values under each key.

    :param dicts: any number of defaultdicts, with call param of -- lambda: [], and entries all being lists
    :return: a single defaultdict with the same call param that has merged all of the disparate dicts
    """
    all_keys = []
    for d in dicts:
        all_keys += list(d.keys())
    all_keys = list(set(all_keys))

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
            flat.append(flatten_dict(item))
        else:
            flat.append(item)
    return flat


def flatten_dict(dic):
    """
    Flattens a nested dictionary into a 1-D dict of lists, where each list has entries that had the same dict key.
    Note that this dumps any keys that have only dicts or lists of dicts as their values.

    :param dic: a nested dictionary
    :return: a flattened dictionary
    """
    flat = defaultdict(lambda: [])

    for k in dic:
        if type(dic[k]) == dict:
            nest = flatten_dict(dic[k])
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
