import json
import csv
from deconstruct import *
from hebrew_translator import translate
from cachemanager import *
from rlprint import rlprint


if __name__ == '__main__':
    with open('Meilah.json', encoding='utf-8') as f:
        meilah = json.load(f)
    with open('dicta_all_words_only.csv', encoding='utf-8') as f:
        dicta = f.read().split('\n')
    with open('bdb_word_mapping.json', encoding='utf-8') as f:
        bdb = json.load(f)
    with open('jastrow_all_word_forms.csv', encoding='utf-8') as f:
        jastrow = f.read().split('\n')

    matches = []

    for page in meilah:
        # two empty lines
        matches += [[], []]

        for chunk in page:
            print('-'*20)

            for word_container in chunk:
                print('Translating:', end='\t')

                word = word_container['word']
                lang = word_container['lang']

                rlprint(word_container['word'][1], end=' ')
                print(lang)

                # Aramaic
                if lang == 'A' or lang == 'U':
                    removed_prefixes = detach_prefixes(word[2], lang='A')
                    links = []
                    for option in removed_prefixes:
                        if option[-1] in dicta:
                            links.append(option[-1])
                    if links:
                        matches.append([word[0], lang] + links)
                        continue

                # Biblical Hebrew
                if lang == 'B':
                    if word[1] in bdb:
                        matches.append([word[0], lang] + bdb[word[1]])
                        continue

                # Rabbinic Hebrew, and a backup if the particular translators fail
                heb_options = translate(word[1])
                heb_links = []
                for option in heb_options:
                    if option[0] in jastrow:
                        heb_links.append(option)
                if heb_links:
                    matches.append([word[0], (lang, word_container['pos'])] + heb_links[:3])
                    continue

                # Last resort is a naive search of Jastrow
                removed_prefixes = detach_prefixes(word[1])
                amb_links = []
                for option in removed_prefixes:
                    if option[-1] in dicta:
                        amb_links.append(option[-1])
                matches.append([word[0], lang] + amb_links)

            # one empty line
            matches += [[]]

    # save_hebrew('hebrew_cache.csv')
    with open('Meilah_full.csv', 'w+', encoding='utf-8-sig', newline='') as f:
        meilah_writer = csv.writer(f)
        meilah_writer.writerows(matches)
