import requests
import os
import json
from utils.deconstruct import *
from utils.rlprint import rlprint

data_path = './data/lang_tagged_talmud/'
output_path = './data/pos_tagged_talmud/'

yap_host_address = 'http://localhost:8000/yap/heb/joint'


def remove_aram_prefixes_from_start(word):
    return detach_prefixes(word, lang='A')


def get_yap_tagging(heb_phrase):
    data = '{{"text": "{}"}}'.format(heb_phrase).encode('utf-8')
    yap_response = requests.get(yap_host_address, data=data, headers={'content-type': 'application/json'})
    yap_json = json.loads(yap_response.text)
    return yap_json


def clean_yap_rval(yap_rval):
    """
    Returns list of (token, pos) tuples
    """
    token_info = yap_rval['md_lattice'].split('\n')
    # info line is structured as:   INDEX   INDEX+1   TOKEN   REVISED_TOKEN   POS   POS   OTHER_INFO   ORIGINAL_INDEX
    token_info = [info.split('\t') for info in token_info]

    pos_list = []
    curr = 1
    for info in token_info:
        if len(info) == 1:  # The table ends with empty strings
            continue

        pos = info[4]
        index = info[-1]

        # The final POS for the given index is the one that matters, since the preceding ones are prefixes
        if curr == index:
            pos_list[-1] = pos
        else:
            curr = index
            pos_list.append(pos)

    return pos_list


def tag_heb_pos(seq):
    heb_phrases = ' '.join(seq) + '  '
    rlprint(heb_phrases)

    tagged_heb_sequence = get_yap_tagging(heb_phrases)
    heb_tags_only = clean_yap_rval(tagged_heb_sequence)

    return heb_tags_only


def prep_for_yap(chk_text):
    words_for_tagging = [word_forms['word'][1] if word_forms['word'][1] != '' else word_forms['word'][0]
                         for word_forms in chk_text]
    words_for_tagging = [heb_plural(to_hitpael(wd)) for wd in words_for_tagging]

    heb_words_only = []
    for i in range(len(words_for_tagging)):
        # Second line ensures 'מתני' isn't included in the phrase
        for_yap = alph_only(words_for_tagging[i]) if chk_text[i]['lang'] == 'R' \
                                                     and '׳' not in words_for_tagging[i] \
            else '.'
        heb_words_only.append(for_yap)

    return heb_words_only


if __name__ == '__main__':
    print('REMINDER: YAP must be running in order for this program to run.')
    run = input('Is YAP running? y/n: ')
    if run == 'n':
        assert False

    files = os.listdir(data_path)

    for file in files:
        title = file[:-5]
        do_masekhet = input('Proceed with ' + title + '? y/n: ')
        if do_masekhet == 'n':
            continue

    with open(data_path + file, encoding='utf-8') as f:
        text = json.load(f)

    text_with_pos_tags = []

    continued = False
    prev_chunk_text = []

    for page in text:
        print('-'*10 + 'next page' + '-'*10)

        # What will be written to the file -- just the chunks themselves with each word POS and language tagged
        text_with_pos_tags.append([])

        for chunk in page:
            print('='*10)
            chunk_text = chunk['text']

            if not continued:
                hebrew_words_only = prep_for_yap(chunk_text)
            else:
                hebrew_words_only = prep_for_yap(prev_chunk_text + chunk_text)
            pos_tags = tag_heb_pos(hebrew_words_only)[::-1]

            if continued:
                prev_chunk_tagged = [{'lang': word_forms['lang'],
                                      'word': word_forms['word'],
                                      'pos': pos_tags.pop()} for word_forms in prev_chunk_text]
                text_with_pos_tags[-2][-1] = prev_chunk_tagged

                print('*'*10)
                for w in prev_chunk_tagged:
                    rlprint(w['word'][1], end='\t\t\t')
                    print(w['pos'])
                print('*'*10)

            curr_chunk_tagged = [{'lang': word_forms['lang'],
                                  'word': word_forms['word'],
                                  'pos': pos_tags.pop()} for word_forms in chunk_text]
            text_with_pos_tags[-1].append(curr_chunk_tagged)

            if not continued and (chunk['type'] == 'mc' or chunk['type'] == 'gc') and hebrew_words_only[-1] != '.':
                prev_chunk_text = chunk_text
                continued = True
            else:
                prev_chunk_text = []
                continued = False

            for w in curr_chunk_tagged:
                rlprint(w['word'][1], end='\t\t\t')
                print(w['pos'])

    with open(output_path + file, 'w+', encoding='utf-8') as f:
        json.dump(text_with_pos_tags, f, ensure_ascii=False, indent=4)
