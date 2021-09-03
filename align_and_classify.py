import os
import json
import requests
import re
from utils.rlprint import rlprint
from utils.deconstruct import alph_only


def clean_text(text):
    no_html = re.sub(r'</*[a-z]+>', '', text)
    no_quotes = re.sub(r'(״ | ״| ׳)', ' ', no_html)
    no_punc = re.sub(r'["\'\.\?!,;:…—]+?', '', no_quotes)
    return ' '.join(no_punc.split())


def get_from_sefaria(name):
    length = requests.get('http://www.sefaria.org/api/texts/' + name + '.2')
    length = json.loads(json.dumps(length.json()))['length']
    all_data = requests.get('http://www.sefaria.org/api/texts/' + name + '.2-' + str(length))
    original = json.loads(json.dumps(all_data.json()))['he']

    structured = []
    for p in original:
        structured.append([clean_text(c).split(' ') for c in p])
    return structured


def all_words(lines):
    text = []
    for l in lines:
        if l == '' or '*' in l:
            continue
        else:
            spaces_only = ' '.join(l.split())
            text += re.sub( '"', '״', re.sub("'", '׳', spaces_only) ).split(' ')
    return text


def align_texts(mal, has, sef):

    aligned_text = []
    dicta_index = 0
    p = 0

    while p < len(sef):
        aligned_text.append([])
        c = 0
        while c < len(sef[p]):
            aligned_text[p].append([])
            w = 0
            while w < len(sef[p][c]):
                print(str(p) + ' ' + str(c) + ' ' + str(w))

                if dicta_index >= len(mal):
                    aligned_text[p][c].append([sef[p][c][w], '', ''])
                    w += 1
                    continue

                if alph_only(sef[p][c][w]) == alph_only(mal[dicta_index]):
                    aligned_text[p][c].append([sef[p][c][w], maleh[dicta_index], has[dicta_index]])
                    dicta_index += 1; w += 1

                else:
                    print('Sefaria:', end='\t')
                    rlprint(sef[p][c][w])
                    rlprint(' '.join(sef[p][c][w-3:w+3]), end='\n')
                    print('Dicta:', end='\t')
                    rlprint(mal[dicta_index])
                    rlprint(' '.join(mal[dicta_index-3:dicta_index+3]), end='\n')

                    opt = ''
                    while opt != 'a' and opt != 's' and opt != 'd':
                        opt = input('Align (a), skip Sefaria word (s), skip Dicta word (d): ')

                    if opt == 'a':
                        aligned_text[p][c].append([sef[p][c][w], maleh[dicta_index], has[dicta_index]])
                        dicta_index += 1; w += 1
                    elif opt == 's':
                        aligned_text[p][c].append([sef[p][c][w], '', ''])
                        w += 1
                    elif opt == 'd':
                        aligned_text[p][c].append(['', maleh[dicta_index], haser[dicta_index]])
                        dicta_index += 1
            c += 1
        p += 1

    return aligned_text


def tag_page(page, prev):
    """
    Tags the beginnings of mishnayot and gemaras, and tags when a chunk is split across two pages,
    by making them tuples with the following code for second entry:
    - 'm' = start of a mishna
    - 'mc' = mishna continued across page
    - 'g' = start of a gemara
    - 'gc' = gemara continued across page

    :param page: a page (amud) of Talmud
    :param prev: the tag of the final chunk of the previous page
    :return: the cleaned and tagged page
    """
    # Special case of Nazir 33b
    if len(page) == 0:
        return [{'type': prev, 'text': []}]

    tagged_page = []
    for c in page:
        head = alph_only(c[0][1])   # The first word in the Dicta Maleh version of the chunk
        curr = 'm' if head == "מתני" else ('g' if head == "גמ" else '0')
        if (prev == 'mc' or prev == 'gc') and curr == '0':
            tag = prev
            prev = prev[0]
        elif curr == '0':
            tag = prev
        elif curr != prev:
            tag = curr
            prev = curr
        else:
            tag = prev
        tagged_page.append({'type': tag, 'text': c})
    tagged_page[-1]['type'] += 'c' if tag[-1] != 'c' else ''
    return tagged_page


def label_pages(mas):
    num = 2
    amud = 'a'
    for p in range(len(mas)):
        mas[p] = {'page': str(num) + amud, 'content': mas[p]}
        if amud == 'a':
            amud = 'b'
        else:
            amud = 'a'
            num += 1
    return mas


path = './data/dicta_talmud/'
dirs = os.listdir(path)


if __name__ == '__main__':

    for dir in dirs:
        do_masekhet = input('Proceed with ' + dir + '? y/n: ')
        if do_masekhet == 'n':
            continue

        files = os.listdir(path + dir)
        maleh_loc = 1*('maleh' in files[1])
        with open(path + dir + '/' + files[maleh_loc], encoding='utf-8') as m:
            maleh = all_words(m.read().split('\n'))
        with open(path+ dir + '/' + files[1 - maleh_loc], encoding='utf-8') as h:
            haser = all_words(h.read().split('\n'))
        assert len(maleh) == len(haser)

        sefaria = get_from_sefaria(dir)

        aligned = align_texts(maleh, haser, sefaria)

        tagged = [[{'type': 'm'}]]
        for p in aligned:
            p_tagged = tag_page(p, tagged[-1][-1]['type'])
            tagged.append(p_tagged)
        tagged = tagged[1:]

        labeled = label_pages(tagged)

        with open('./data/aligned_talmud/' + dir + '.json', 'w+', encoding='utf-8') as path:
            json.dump(labeled, path, ensure_ascii=False, indent=4)
