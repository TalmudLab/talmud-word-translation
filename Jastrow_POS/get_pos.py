from collections import defaultdict
from copy import deepcopy
import json
import re
import nltk
import enchant

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

"""
Automatic rules for tag_def. If these tags are present as the first word of a sub-definition, then
there can only be one possible tag for the word, so the process is automated. For example, if the sub-definition
begins with 'to' (as in, 'to go'), then the word must be a verb.
"""
auto_tag = {
    'TO': [('DEF', ('VB',))],  # TO go...
    'DT': [('DEF', ('NN',))],  # A house... <- 'a long time since' breaks this rule!!! FIX
    'NN': [('DEF', ('NN',))],  # People...
    'IN': [('DEF', ('JJ',))],  # OF stone...
    'UH': [('DEF', ('UH',))],  # OH my!
    'PDT': [('DEF', ('NN',))]  # BOTH the dogs
}

"""
A tag simplifier for tag_def. For example, past tense and present tense verbs should both map to 'VB.'
"""
simple_tags = {
    'JJR': 'JJ', 'JJS': 'JJ', 'VBD': 'JJ',  # Past tense verbs only appear in Jastrow if they act as adjectives.
    'NNS': 'NN', 'NNP': 'NN', 'NNPS': 'NN', 'VBG': 'NN',  # Gerunds only appear in Jastrow if they act as nouns. (CHECK)
    'RBR': 'RB', 'RBS': 'RB',
    'VBN': 'VB', 'VBP': 'VB', 'VBZ': 'VB',
    'PRP$': 'POS',
    'PRP': 'NN', 'WDT': 'DT', 'WP': 'NN', 'WP$': 'POS', 'WRB': 'RB' # THIS LINE IS TENTATIVE
}

"""
Dictionary to check for word ambiguity in tag_def; Jastrow uses US spelling.
"""
english_dict = enchant.Dict('en_US')
"""
Grammar and parser for the new _tag_rules method.
"""
gram = nltk.data.load('file:jas_grammar.cfg')
def_parser = nltk.ShiftReduceParser(gram)


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


def _combine_tags(tag_set):
    """
    Combines repeated tags in a tag set to simplify an expression.
    Also simplifies tags.

    :param tag_set: the set of tags, a list of Penn POS tags
    :return: the simplified tag set, combining like tags
    """
    new_set = ['']
    for t in tag_set:
        simple_t = simple_tags[t] if t in simple_tags else t
        if new_set[-1] == simple_t or simple_t == 'RP':
            pass
        elif new_set[-1] == 'RB' and simple_t == 'JJ':  # In English, ADV + ADJ = ADJ (e.g. 'slowly dying man')
            new_set[-1] = 'JJ'
        else:
            new_set.append(simple_t)
    return new_set[1:]


def _tag_rules(defs):
    """
    A new tag rule function that uses a CFG parser to simplify the tags of a sub-definition.

    :param defs: a tuple of sub-definitions
    :return: a list of tuples, each containing a probability tag (see tag_def) and a tuple of possible tags
    """
    def_tags = []

    for d in defs:
        # We can throw away the words themselves, and the (useless) particles. A period is added to mark the end of the
        # definition for the parser.
        tags = nltk.pos_tag(nltk.word_tokenize(d))
        tags = [simple_tags[t[1]] if t[1] in simple_tags else t[1] for t in tags]
        tags = [t for t in tags if t != 'RP'] + ['.']
        print(tags)

        # We now check whether their are any ambiguous words in the phrase.
        amb = 'DEF' if all([english_dict.check(t) for t in tags]) and ('FW' not in tags) else 'AMB'

        # If there's any interjection in the phrase, then it is automatically an interjection
        if 'UH' in tags:
            def_tags.append(('DEF', 'UH'))
            continue

        for tree in def_parser.parse(tags):
            print(tree)

    return ''


def _old_tag_rules(defs):
    """
    The rules for ranking tags within an individual sub-definition.

    :param defs: a tuple of sub-definitions
    :return: a list of tuples, each containing a probability tag (see tag_def) and a tuple of possible tags

    TODO: Rules for FW, LS, MD, PRP, RP, all W's; check PDT rule. Maybe just dump nonce words?
    """
    def_tags = []
    first = True

    for d in defs:
        # We can throw away the words themselves. Any ambiguous words should be marked, as NLTK automatically
        # identifies them as nouns.
        tags = nltk.pos_tag(nltk.word_tokenize(d))
        tags = [t[1] if english_dict.check(t[0]) else 'AMB' for t in tags]
        amb = 'AMB' if 'AMB' in tags else 'DEF'

        # If the first word of the definition has an automatic rule, return that tag.
        if first and len(tags) > 1 and tags[0] in auto_tag:
            return auto_tag[tags[0]]
        first = False

        # A conjunction is useless, unless the definition of the word is itself a conjunction.
        tags = [t for t in tags if t != 'CC']
        if not tags: return [('DEF', ('CC',))]

        # Same for determiners
        tags = [t for t in tags if t != 'DT']
        if not tags: return [('DEF', ('DT',))]

        # Since the conjunctions are gone, we can combine identical POSs
        tags = _combine_tags(tags)

        # If there is now only one POS, it must be the correct POS for this sub-definition. This rule comes first, as
        # the following rules are dependent on len(tags) > 1.
        if len(tags) == 1:
            result = (tags[0],)

        # If a phrase ends on a preposition, then it is an adjectival phrase (e.g. "the beginning of")
        elif tags[-1] == 'IN':
            result = ('JJ',)

        # An adjective followed by a noun is a noun, as long as the phrase does not end on a preposition
        elif tags[0] == 'JJ' and tags[1] == 'NN':
            result = ('NN',)

        # But a plain adjective is just an adjective. However, if the next word is ambiguous, it may be a noun.
        elif tags[0] == 'JJ' and tags[1] != 'AMB':
            result = ('JJ',)

        # An adverb followed by a verb is a verb
        elif tags[0] == 'RB' and tags[1] == 'VB':
            result = ('VB',)

        # But a plain adjective is just an adjective. However, if the next word is ambiguous, it may be a verb.
        elif tags[0] == 'RB' and tags[1] != 'AMB':
            result = ('RB',)

        # A possessive is necessarily followed by a noun phrase
        elif 'POS' in tags:
            result = ('NN',)

        # A cardinal must be followed by a noun phrase if not alone
        elif tags[0] == 'CD':
            result = ('NN',)

        else:
            result = tuple(tags)

        def_tags.append((amb, result))

    return def_tags


def _best_tag(tags):
    """
    Given a set of possible Aramaic word POS tags, picks the most likely one.

    :param tags: the output of _tag_rules
    :return: a single tuple, containing a probability tag and the most probable tag (see tag_def docs)
    """
    tags = [t for t in tags if t[0] != 'AMB'] if any([t[0] == 'DEF' for t in tags]) else tags
    prob_tag = tags[0][0]
    tags = [t for t in tags if len(t[1]) == 1] if any([len(t[1]) == 1 for t in tags]) else tags

    count = defaultdict(lambda: 0)
    for t in tags:
        for option in t[1]:
            count[option] += 1
    ranked = sorted(count.items(), key=lambda item: item[1], reverse=True)

    return prob_tag, ranked[0][0]



def tag_def(defs):
    """
    Tags a single definition entry for a particular document, i.e. a tuple containing the individual sub-definitions
    contained in each 'definition' entry of a word. This involves the following steps:
        1. Returning 'UN' (unidentified) if the set of sub-definitions is empty.
        2. Looping through each sub-definition and tagging it.
        3. Using a set of rules to come up with a single POS tag for the whole phrase. (E.g. 'green tree' = ADJ N -> N)
        4. When a single tag cannot be confirmed by the built-in rules, returning the top possibility and the tag 'AMB'
           (ambiguous).
    The rule set is described in the in-line comments of _tag_rules. The POS tags follow the Penn Treebank tag set
    and are contained in the second element of each tuple. The first elements are as follows:
        1. 'UN' = Unidentified
        2. 'DEF' = definite, i.e. the word has been properly identified
        3. 'AMB' = ambiguous; this means that the tag in the second element is tentative

    :param defs: a tuple containing the sub-definitions of an individual 'definition' entry of a word. See return value
                 of get_defs.
    :return: a two element tuple containing the first element probability tag, and the most probable tag (see above).
    """
    # If, after cleaning the definition of html, Hebrew characters, and abbreviations, there is no text, this means
    # that the definition directs back to another word through a hyperlink. Since this cannot be resolved, the POS
    # is unidentified, 'UN.'
    defs = [d for d in defs if d != '']

    if len(defs) == 0:
        return 'UN', ''

    def_tags = _tag_rules(defs)
    return _best_tag(def_tags)
