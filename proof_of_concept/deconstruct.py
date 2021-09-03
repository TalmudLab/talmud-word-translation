import hebrew
import pandas as pd

prefix_table_path = './prefix_table.csv'
all_prefix_rules = pd.read_csv(prefix_table_path, encoding='utf-8')
all_prefix_rules[['ARAM', 'HEB', 'ALL']].astype('int64')

all_verb_tags = ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'MD', 'VB-M')
all_noun_tags = ('NN', 'NNS', 'NNP', 'NNPS', 'NNG', 'NNGT', 'NNT')
morfix_pos_to_yap_pos = {
    'תואר': ('JJ', 'JJR', 'JJS', 'JJT'),
    'תואר הפועל': ('RB', 'RBR', 'RBS'),
    'מילת קישור': ('CC', 'IN'),
    'מילת קריאה': ('UH',),
    'מילת שאלה': ('HAM', 'QW', 'WDT'),
    'תחילית': ('Prefix',),
    'שֵם ז\'': all_noun_tags, 'שֵם נ\'': ('NN', 'NNS', 'NNP', 'NNPS'),
    'מספר מונה': ('CDT', 'CD'), 'מספר סודר': ('CDT', 'CD'),
    'מילת יחס': ('IN',),
    'כינוי נפרד': ('PRP', 'PRP$'),
    'שֵם כמות': ('MOD',),
    '': 'Ambiguous',  # Can be shel, holiday, or other
    'פ\' קל': all_verb_tags, 'פ\' פיעל': all_verb_tags, 'פ\' הפעיל': all_verb_tags, 'פ\' התפעל': all_verb_tags,
    'פ\' נפעל': all_verb_tags, 'פ\' פועל': all_verb_tags, 'פ\' הופעל': all_verb_tags
}


def alph_only(token):
    return ''.join([c for c in token if c in hebrew.alphabet])


# Note that this method is slightly different from the former, in that it leaves punctuation
def remove_nikkud(token):
    return ''.join([c for c in token if not (1456 <= ord(c) <= 1479)])


def heb_plural(word, voweled=True):
    # TODO: Check if word is a valid word ending in the same suffix as the plural
    if voweled and word[-3:] == 'ִין':
        return word[:-1] + 'ם'
    elif word[-2:] == 'ין':
        return word[:-1] + 'ם'
    else:
        return word


def to_nitpael(word, voweled=True):
    if voweled and word[:4] == 'הִתְ':
        return 'נ' + word[1:]
    elif word[:2] == 'הת':
        return 'נ' + word[1:]
    else:
        return word


def to_hitpael(word, voweled=True):
    if voweled and word[:4] == 'נִתְ':
        return 'ה' + word[1:]
    elif word[:2] == 'נת':
        return 'ה' + word[1:]
    else:
        return word


def _is_in_order(pref, curr):
    pref, curr = remove_nikkud(pref), remove_nikkud(curr)
    return ((pref != 'ה') and (pref != 'ק')    # Must come last
            and (curr != 'ו')  # Must come last
            and not (curr == 'ה' and pref in 'כלב')    # Conjoins and hey is dropped
            and not (curr in 'בלמא' and pref in 'בלמא'))  # No double prepositions


def detach_prefixes(token, lang='U'):
    prefixes = all_prefix_rules[all_prefix_rules['ALL'] == 1 if lang == 'U'
                                else (all_prefix_rules['ARAM'] == 1 if lang == 'A'
                                      else all_prefix_rules['HEB'] == 1)]
    word = token
    pref = ''
    sub_table = None

    possibilities = [('', word)]
    done = False
    while len(word) > 1:
        # Loop through remaining characters in the word until completing a full syllable
        for i in range(1, len(word)):
            if word[i] in hebrew.alphabet:
                curr = word[:i]
                # This is a prefix and it is the first one
                if pref == '' and prefixes['PREFIX'].isin([curr]).any():
                    pref = curr
                    sub_table = prefixes[prefixes['PREFIX'] == curr]
                    word = word[i:]
                # This is a valid next letter for the previous prefix
                elif pref != '' and sub_table['NEXT'].isin([curr]).any():
                    curr = sub_table[sub_table['NEXT'] == curr].iloc[0]['SUB']
                    word = word[i:]
                    possibilities.append( possibilities[-1][:-1] + (pref,  curr + word) )
                    if prefixes['PREFIX'].isin([curr]).any() and _is_in_order(pref, curr):
                        pref = curr
                        sub_table = prefixes[prefixes['PREFIX'] == curr]
                    else:
                        done = True
                # Not a prefix or not a valid following letter
                else:
                    done = True
                # Break after a syllable is checked in order to reset len(word)
                break
            # If the last character is not a letter, we have reached the end of the word
            elif i == len(word) - 1:
                done = True

        if done:
            break

    return possibilities
