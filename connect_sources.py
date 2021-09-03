import os
import json
import requests
from utils.rlprint import rlprint
from utils import hebrew
import re


def basic_clean(txt):
    if type(txt) == list:
        txt = ' '.join(txt)
    txt = ' '.join(txt.split())
    return txt


def remove_punctuation(txt, has_nikkud=False):
    return ''.join([char for char in txt
                    if char in hebrew.alphabet + ' '
                    or (has_nikkud and char in hebrew.all_nikkud)])


def clean_bible(txt):
    txt = basic_clean(txt)
    txt = txt.replace('־', ' ')
    txt = re.sub(r'\{.*\}', '', txt)
    return remove_punctuation(txt, has_nikkud=True)


def clean_mishna(txt):
    txt = basic_clean(txt)
    txt = re.sub(r'\(.*\)', '', txt)
    return remove_punctuation(txt, has_nikkud=True)


def clean_tosefta(txt):
    txt = basic_clean(txt)
    txt = re.sub(r'[<\(].*[\)>]', '', txt)
    return remove_punctuation(txt)


def clean_sifra(txt):
    txt = basic_clean(txt)
    txt = re.sub(r'[\[\(].*[\)\]]', '', txt)
    txt = txt.replace('...', '')
    return remove_punctuation(txt)


def clean_sifrei(txt):
    txt = basic_clean(txt)
    txt = re.sub(r'\(.*\)', '', txt)
    return remove_punctuation(txt)


def get_connections(name, page, chunk):
    all_connections = requests.get('https://www.sefaria.org/api/links/' + name + '.' + page + '.' + str(chunk))
    all_connections = json.loads(json.dumps(all_connections.json()))

    # Bible Processing
    bible = [con for con in all_connections if con['category'] == 'Tanakh']
    bible = ' '.join([clean_bible(con['he']) for con in bible])

    # Mishna Processing
    mishna = [con for con in all_connections if con['category'] == 'Mishnah']
    mishna = ' '.join([clean_mishna(con['he']) for con in mishna])

    # Tosefta Processing
    tosefta = [con for con in all_connections if con['category'] == 'Tosefta']
    tosefta = ' '.join([clean_tosefta(con['he']) for con in tosefta])

    # Sifra Processing
    sifra = [con for con in all_connections if con['index_title'] == 'Sifra']
    sifra = ' '.join([clean_sifra(con['he']) for con in sifra])

    # Sifrei Processing
    sifrei = [con for con in all_connections if con['index_title'] in ('Sifrei Bamidbar', 'Sifrei Devarim')]
    sifrei = ' '.join([clean_sifrei(con['he']) for con in sifrei])

    return bible, mishna, tosefta, sifra, sifrei


files = os.listdir('./data/aligned_talmud/')


if __name__ == '__main__':

    for file in files:
        title = file[:-5]
        do_masekhet = input('Proceed with ' + title + '? y/n: ')
        if do_masekhet == 'n':
            continue

        with open('./data/aligned_talmud/' + file, encoding='utf-8') as f:
            text = json.load(f)

        linked = []
        for p in text:
            linked.append({'page': p['page'], 'content': []})
            for c in range(len(p['content'])):
                print(p['page'] + ':' + str(c + 1))
                connections = get_connections(title, p['page'], c + 1)
                linked[-1]['content'].append({'type': p['content'][c]['type'],
                                              'text': p['content'][c]['text'],
                                              'bible': connections[0],
                                              'mishna': connections[1],
                                              'tosefta': connections[2],
                                              'sifra': connections[3],
                                              'sifrei': connections[4]})
                for i in connections:
                    rlprint(i)

        with open('./data/connected_talmud/' + title + '.json', 'w+', encoding='utf-8') as path:
            json.dump(linked, path, ensure_ascii=False, indent=4)
