from utils.deconstruct import *
import numpy as np

dicta_words_path = './src/languagetagger/dicta_all_words_only.csv'
with open(dicta_words_path, encoding='utf-8') as f:
    dicta_all = f.read().split('\n')[1:]
    dicta_all = frozenset(dicta_all)


def is_in_dicta(word_forms):
    # Dicta uses haser spelling convention
    return word_forms[2] in dicta_all


def is_in_mishna(word_forms, mishna):
    return any([(word != '' and word in mishna) for word in word_forms]) \
           or any([(word != '' and heb_plural(word) in mishna) for word in word_forms])


def is_in_tanna(word_forms, tanna):
    unvoweled_forms = [remove_nikkud(word) for word in word_forms]
    return any([(word != '' and word in tanna) for word in unvoweled_forms]) \
           or any([(word != '' and heb_plural(word, voweled=False) in tanna) for word in unvoweled_forms])


def trigram_language_disambiguate(prev, curr, after, weight=1.2, boundary=0.1):
    # This equation is adapted and simplified from the trigram estimator described in Noah's Master's thesis
    # His equation: isAr = mean( P(prev = Aramaic), P(after = Aramaic) ) + P(curr = Aramaic) >
    #                      mean( P(prev = Hebrew), P(after = Hebrew) ) + P(curr = Hebrew)
    # We can simplify this by noting that P(Aramaic) = 1 - P(Hebrew). Thus this is equivalent to:
    #               isAr = mean(P(prev = Hebrew), P(after = Hebrew)) + P(curr = Hebrew) < 1
    # I also believe it is important not to oversimplify. There are many cases where a Hebrew word is jammed
    # between two Araamaic words (and vice versa); thus we should give more weight to the current word's probability.
    # Hence the weight parameter, which is somewhat arbitrarily chosen.
    # Moreover, a definite language tag should only be returned if the next tag is significantly close to the boundary.
    # I used the boundary of 0.1, i.e. 'A' is returned if isAr < 0.9 and 'R' if isAr > 0.1, else 'U.'
    stat = np.mean((prev, after)) + weight * curr
    return 'A' if stat < (1 - boundary) else ('R' if stat > (1 + boundary) else 'U')


def is_valid_trigram(prev, after):
    return prev['lang'] != 'B' and after['lang'] != 'B'


def disambiguate_chunk(chunk_tagged, chunk_text, chunk_langs, chunk):
    for i in range(len(chunk_tagged)):
        if chunk_tagged[i]['lang'] != 'U':
            continue

        # Check the Tannaitic sources to see if the word appears there, in which case it is Hebrew
        if is_in_tanna(chunk_text[i], '{} {} {}'.format(chunk['tosefta'], chunk['sifra'], chunk['sifrei'])):
            chunk_tagged[i]['lang'] = 'R'
        elif i + 1 < len(chunk_tagged) and i - 1 >= 0:
            # If the context on both sides is Biblical, then the word is probably Biblical, but spelled differently
            # than in the verse (the writers of the Talmud sometimes have a different version of Tanakh)
            if chunk_tagged[i-1]['lang'] == 'B' and chunk_tagged[i+1]['lang'] == 'B':
                chunk_tagged[i]['lang'] = 'B'
            # If the word is embedded in a valid Aramaic/Rabbinic Hebrew trigram, use trigram context disambiguation
            elif is_valid_trigram(chunk_tagged[i-1], chunk_tagged[i+1]):
                chunk_tagged[i]['lang'] = trigram_language_disambiguate(chunk_langs[i-1],
                                                                        chunk_langs[i],
                                                                        chunk_langs[i+1])

    return chunk_tagged
