import pymongo
import pandas as pd
from collections import defaultdict
from copy import deepcopy
import re
import json


with open('pswrd.txt') as f: pswrd = f.read()
conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
jastrow = _db['dov-jastrow']


dicta_all = pd.read_csv('dicta_all_roots.csv').drop_duplicates()


"""
All English abbreviations in Jastrow, organized by number of abbreviations in keyword (so that the longer ones are
not knocked out during replacement).
"""
# Basic abbreviations in preface
# Excludes abbreviations that indicate language or POS
abbrevs = ['Mish. N. or Nap.',
           'a. v. fr.', 'Ab. d’R. N.', 'Curt. Griech. Etym.', 'Del. Assyr. Handw.', 'Ges. H. Dict.', 'Koh. Ar. Compl.',
           'Perl. Et. St.', 'Rabb. D. S.', 'Tanḥ. ed. Bub.', 'Tosef. ed. Zuck.',
           'a. e.', 'a. fr.', 'a. l.', 'Ab. Zar.', 'Ag. Hatt.', 'Ar. Compl.', 'B. Bath.', 'B. Kam.',
           'B. Mets.', 'B. N.', 'Berl. Beitr.', 'Cant. R.', 'corr. acc.', 'Darkhe Mish.', 'Del. Proleg.', 'Der. Er.',
           'Deut. R.', 'Esth. R.', 'Ex. R.', 'gen. of', 'Gen. R.', 'Hildesh. Beitr.', 'Koh. R.', 'l. c.', 'Lam. R.',
           'Lev. R.', 'M. Kat.', 'Maas. Sh.', 'marg. vers.', 'Mat. K.', 'Midr. Sam.', 'Midr. Till.', 'Mish. Pes.',
           'Ms. F.', 'Ms. H.', 'Ms. K.', 'Ms. M.', 'Ms. O.', 'Ms. R.', 'Neub. Géogr.', 'Num. R.', 'P. Sm.',
           'pers. pron.', 'Pesik. R.', 'Pesik. Zutr.', 'preced. art.', 'preced. w.', 'q. v.', 'R. Hash.',
           'R. S.', 'Ruth R.', 's. v.', 'Sef. Yets', 'Sm. Ant.', 'Targ. O.', 'Targ. Y.', 'Targ. II', 'var. lect.',
           'a.', 'Ab.', 'abbrev.', 'add.', 'Alf.', 'Am.', 'Ar.', 'Arakh.', 'Bab.', 'Bart.',
           'beg.', 'Beitr.', 'Bekh.', 'Ber.', 'Berl.', 'Bets.', 'B’ḥuck.', 'Bicc.', 'bot.', 'B’resh.', 'B’shall.',
           'Cant.', 'Chron.', 'cmp.', 'comment.', 'comp.', 'contr.', 'contrad.', 'corr.',
           'corrupt.', 'Dan.', 'def.', 'Del.', 'Dem.', 'denom.', 'Deut.', 'diff.', 'differ.', 'dimin.', 'Du.', 'ed.',
           'Ed.', 'ellipt.', 'Erub.', 'esp.', 'Esth.', 'Ex.', 'expl.', 'explan.', 'Ez.', 'Fl.', 'foreg.', 'fr.',
           'freq.', 'Fr.', 'Frank.', 'Gem.', 'Gen.', 'Gitt.', 'Gloss.', 'Hab.', 'Hag.', 'Ḥag.', 'Ḥall.',
           'Hor.', 'Hos.', 'Ḥuck.', 'Ḥull.', 'intens.', 'introd.', 'Is.',
           'Jer.', 'Jon.', 'Jos.', 'Josh.', 'Jud.', 'K.A.T.', 'KAT', 'Kel.', 'Ker.', 'Keth.', 'Kidd.',
           'Kil.', 'Kin.', 'Koh.', 'Lam.', 'Lev.', 'Maasr.', 'Macc.', 'Maim.', 'Makhsh.', 'Mal.', 'Mass.', 'M’bo',
           'Meg.', 'Meil.', 'Mekh.', 'Men.', 'Mic.', 'Midd.', 'Midr.', 'Mikv.', 'Mish.', 'Mishp.', 'Ms.', 'Mus.',
           'Nah.', 'Naz.', 'Neg.', 'Neh.', 'Ned.', 'Nidd.', 'Num.', 'Ob.', 'Ohol.',
           'onomatop.', 'opin.', 'opp.', 'Orl.', 'oth.', 'Par.', 'Par.', 'Pes.', 'Pesik.', 'Pfl.', 'phraseol.',
           'preced.', 'prob.', 'prop.', 'prov.', 'Prov.', 'Ps.', 'r.', 'R.',
           'Rap.', 'ref.', 'S.', 's.', 'Sabb.', 'Sam.', 'Schr.', 'Shebi.', 'Shebu.', 'Shek.', 'S’maḥ.', 'Snh.', 'Sonc.',
           'Sot.', 'sub.', 'Succ.', 'suppl.', 'Taan.', 'Talm.', 'Tam.', 'Tanḥ.', 'Targ.', 'Tem.', 'Ter.', 'Toh.',
           'Tosaf.', 'Tosef.', 'Treat.', 'Trnsf.', 'trnsp.', 'Ukts.', 'usu.', 'v.', 'Var.', 'Ven.', 'vers.', 'Vien.',
           'w.', 'Wil.', 'ws.', 'Y.', 'Yad.', 'Yalk.', 'Yeb.', 'Y’lamd.', 'Zab.', 'Zakh.', 'Zeb.', 'Zech.', 'Zeph.',
           'Zuck.', 'Zuckerm.']
# Other abbreviations, not in preface
additional_abbrevs = ['Bxt.', '&c.']
re_abbrevs = r'\s(' + r'|'.join([re.sub(r'../../utils', r'\.', a) for a in abbrevs + additional_abbrevs]) + r')'


def _merge_dicts(*dicts):
    """
    Merges two or more dictionaries by concatenating as lists all of the different values under each key.

    :param dicts: any number of defaultdicts, with call param of -- lambda: [], and entries all being lists
    :return: a single defaultdict with the same call param that has merged all of the disparate dicts
    """
    all_keys = []
    for d in dicts:
        all_keys += list(d.keys())
    all_keys = list(dict.fromkeys(all_keys))

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


def remove_nikkud(s):
    return ''.join([c for c in s if not (1456 <= ord(c) <= 1479)])


# Ignoring participle, which duplicates verbs
all_pos = ['Adjective', 'Adverb', 'Conj', 'Copula', 'Existential', 'Interjection', 'Interrogative',
           'Negation', 'Noun', 'Numeral', 'Preposition', 'Pronoun', 'Quantifier', 'Shel_', 'Verb']

if __name__ == '__main__':
    mappings = pd.DataFrame(columns=['root', 'pos', 'reserve']
                                     + [item for i in range(1, 11) for item in ['head %d' % i, 'def %d' % i]])

    row = 0
    for pos in all_pos:
        for c, r in dicta_all[dicta_all['pos'] == pos].iterrows():
            root = r['root']

            jas_heads = list(jastrow.find({'word': root}))

            if not jas_heads:
                jas_heads = list(jastrow.find({'all_forms': root}))
            if not jas_heads:
                jas_heads = list(jastrow.find({'unvoweled': remove_nikkud(root)}))
            if not jas_heads:
                jas_heads = list(jastrow.find({'all_unvoweled': remove_nikkud(root)}))
            if not jas_heads:
                jas_heads = []

            definitions = []
            for w in jas_heads:
                fl = flatten_dict(remove_html(w))
                if 'definition' in fl:
                    definition = fl['definition']
                else:
                    definition = ''
                definitions += [w['headword'], definition]
            definitions = definitions[:10]  # The maximum number that will be considered
            mappings.loc[row] = [root, pos, 1] + definitions + [None]*(len(mappings.columns) - 3 - len(definitions))

            row += 1
        print('Done with ' + pos)

    mappings.to_csv('dicta_mappings.csv', encoding='utf-8-sig')
