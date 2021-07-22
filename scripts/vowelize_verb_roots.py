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
verbs = _db['dov-verbs']
jastrow = _db['dov-jastrow']


"""
All English abbreviations in Jastrow, organized by number of abbreviations in keyword (so that the longer ones are
not knocked out during replacement).
"""
# Basic abbreviations in preface
abbrevs = ['Mish. N. or Nap.',
           'a. v. fr.', 'Ab. d’R. N.', 'Curt. Griech. Etym.', 'Del. Assyr. Handw.', 'Ges. H. Dict.', 'Koh. Ar. Compl.',
           'Perl. Et. St.', 'pr. n. f.', 'pr. n. m.', 'pr. n. pl.', 'Rabb. D. S.', 'Tanḥ. ed. Bub.', 'Tosef. ed. Zuck.',
           'a. e.', 'a. fr.', 'a. l.', 'Ab. Zar.', 'Ag. Hatt.', 'Ar. Compl.', 'B. Bath.', 'b. h.', 'B. Kam.',
           'B. Mets.', 'B. N.', 'Berl. Beitr.', 'Cant. R.', 'corr. acc.', 'Darkhe Mish.', 'Del. Proleg.', 'Der. Er.',
           'Deut. R.', 'Esth. R.', 'Ex. R.', 'gen. of', 'Gen. R.', 'Hildesh. Beitr.', 'Koh. R.', 'l. c.', 'Lam. R.',
           'Lev. R.', 'M. Kat.', 'Maas. Sh.', 'marg. vers.', 'Mat. K.', 'Midr. Sam.', 'Midr. Till.', 'Mish. Pes.',
           'Ms. F.', 'Ms. H.', 'Ms. K.', 'Ms. M.', 'Ms. O.', 'Ms. R.', 'Neub. Géogr.', 'Num. R.', 'P. Sm.',
           'pers. pron.', 'Pesik. R.', 'Pesik. Zutr.', 'pr. n.', 'preced. art.', 'preced. w.', 'q. v.', 'R. Hash.',
           'R. S.', 'Ruth R.', 's. v.', 'Sef. Yets', 'Sm. Ant.', 'Targ. O.', 'Targ. Y.', 'Targ. II', 'var. lect.',
           'a.', 'Ab.', 'abbrev.', 'add.', 'adj.', 'adv.', 'Alf.', 'Am.', 'Ar.', 'Arakh.', 'art.', 'Bab.', 'Bart.',
           'beg.', 'Beitr.', 'Bekh.', 'Ber.', 'Berl.', 'Bets.', 'B’ḥuck.', 'Bicc.', 'bot.', 'B’resh.', 'B’shall.',
           'c.', 'Cant.', 'ch.', 'Ch.', 'Chron.', 'cmp.', 'comment.', 'comp.', 'contr.', 'contrad.', 'corr.',
           'corrupt.', 'Dan.', 'def.', 'Del.', 'Dem.', 'denom.', 'Deut.', 'diff.', 'differ.', 'dimin.', 'Du.', 'ed.',
           'Ed.', 'ellipt.', 'Erub.', 'esp.', 'Esth.', 'Ex.', 'expl.', 'explan.', 'Ez.', 'Fl.', 'foreg.', 'fr.',
           'freq.', 'Fr.', 'Frank.', 'Gem.', 'Gen.', 'Gitt.', 'Gloss.', 'Hab.', 'Hag.', 'Ḥag.', 'Ḥall.', 'Hif.',
           'Hithpa.', 'Hithpo.', 'Hor.', 'Hos.', 'Ḥuck.', 'Ḥull.', 'intens.', 'introd.', 'Is.', 'Isp.', 'Ithpa.',
           'Ithpe.', 'Jer.', 'Jon.', 'Jos.', 'Josh.', 'Jud.', 'K.A.T.', 'KAT', 'Kel.', 'Ker.', 'Keth.', 'Kidd.',
           'Kil.', 'Kin.', 'Koh.', 'Lam.', 'Lev.', 'Maasr.', 'Macc.', 'Maim.', 'Makhsh.', 'Mal.', 'Mass.', 'M’bo',
           'Meg.', 'Meil.', 'Mekh.', 'Men.', 'Mic.', 'Midd.', 'Midr.', 'Mikv.', 'Mish.', 'Mishp.', 'Ms.', 'Mus.',
           'Nah.', 'Naz.', 'Neg.', 'Neh.', 'Ned.', 'Nidd.', 'Nif.', 'Nithpa.', 'Num.', 'Ob.', 'Ohol.',
           'onomatop.', 'opin.', 'opp.', 'Orl.', 'oth.', 'Par.', 'Par.', 'part.', 'Pes.', 'Pesik.', 'Pfl.', 'phraseol.',
           'Pi.', 'pl.', 'Pl.', 'preced.', 'prep.', 'prob.', 'pron.', 'prop.', 'prov.', 'Prov.', 'Ps.', 'r.', 'R.',
           'Rap.', 'ref.', 'S.', 's.', 'Sabb.', 'Sam.', 'Schr.', 'Shebi.', 'Shebu.', 'Shek.', 'S’maḥ.', 'Snh.', 'Sonc.',
           'Sot.', 'sub.', 'Succ.', 'suppl.', 'Taan.', 'Talm.', 'Tam.', 'Tanḥ.', 'Targ.', 'Tem.', 'Ter.', 'Toh.',
           'Tosaf.', 'Tosef.', 'Treat.', 'Trnsf.', 'trnsp.', 'Ukts.', 'usu.', 'v.', 'Var.', 'Ven.', 'vers.', 'Vien.',
           'w.', 'Wil.', 'ws.', 'Y.', 'Yad.', 'Yalk.', 'Yeb.', 'Y’lamd.', 'Zab.', 'Zakh.', 'Zeb.', 'Zech.', 'Zeph.',
           'Zuck.', 'Zuckerm.']
# Other abbreviations, not in preface
additional_abbrevs = ['Bxt.', 'Af.', 'Pa .', 'm.', '&c.', 'pl .', 'constr.']
re_abbrevs = r'\s(' + r'|'.join([re.sub(r'../utils', r'\.', a) for a in abbrevs + additional_abbrevs]) + r')'


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


def get_defs(doc_definitions):
    """
    Gets the definitions of a word as a lit of tuples. To be used on
    the entry only after HTML is removed.

    :param doc_definitions: the 'definitions' entry of the document, as a list, preprocessed by flatten_dict
    :return: a list of tuples; each tuple contains the individual comma-separated sub-definitions from each 'definition'

    TODO: sub out 'same'/'next'/etc. -- Maybe in diff method?
    """
    defs = []
    for d in doc_definitions:
        # Make all def separators the same
        stripped = d.replace(';', ',')
        # Remove problematic/unnecessary tokens
        stripped = re.sub(re_abbrevs, '', stripped)
        stripped = re.sub(r'[IVXLMC]+[,\.\s]', '', stripped)
        stripped = re.sub(r'((\(|\[).*?(\)|\])|[^a-zA-Z,.’\-\s])', '', stripped)
        # Get definitions
        separate = stripped.split('.')[0]
        defs.append( tuple([w.lower().strip() for w in separate.split(',')]) )
    return defs


if __name__ == '__main__':
    roots = [remove_nikkud(r) for r in verbs.distinct('root', {})]

    matches = defaultdict(lambda: [])
    for r in roots:
        jas_heads = jastrow.find({'unvoweled': r})
        for w in jas_heads:
            fl = flatten_dict(remove_html(w))
            if 'definition' in fl:
                definition = fl['definition']
            else:
                definition = ''
            matches[r] += [w['headword'], definition]

    all_matches = pd.DataFrame.from_dict(matches, orient='index')
    all_matches.to_csv('verbs.csv' , encoding='utf-8-sig')
