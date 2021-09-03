import json
import pandas as pd
import requests
import re
from collections import defaultdict
from html.parser import HTMLParser
from utils.format import *
from utils.deconstruct import *
from utils.rlprint import rlprint
import pymongo


with open('pswrd.txt') as f: pswrd = f.read()
conn_str = 'mongodb+srv://dov-db2:' + pswrd + '@apicluster.s8lqy.mongodb.net/test'
_client = pymongo.MongoClient(conn_str)
_db = _client['bavli']
jastrow = _db['dov-jastrow']


with open('jastrow_all_word_forms.csv', encoding='utf-8') as f:
    jastrow_all = f.read().split('\n')
    jastrow_all = frozenset(jastrow_all)


searches = ['word', 'all_forms', 'unvoweled', 'all_unvoweled']


class JSONGetter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.begin = False
        self.content = False
        self.json_content = ''

    def handle_starttag(self, tag, attrs):
        self.content = tag == 'json'

    def handle_endtag(self, tag):
        self.content = self.content and not tag == 'json'

    def handle_data(self, data):
        if self.content:
            self.json_content = data.strip()


def extract_heads(page_text):
    head_container = re.search(r'"BDB":\{.*?\}', page_text.text)
    head = head_container.group(0).split(':')[-1]
    head = re.sub(r'["}\[\]]', '', head)
    return [w.strip() for w in head.split(',')]


def get_jastrow_heads(rt, used):
    rlprint(rt, lang='')

    duplicate = []
    for search in searches:
        entries = jastrow.find({search: rt if 'unvoweled' not in search else remove_nikkud(rt)})
        entry_heads = [entry['headword'] for entry in entries]

        # if the root matches a Jastrow headword exactly, return it
        if entry_heads and search == 'word':
            return entry_heads

        # if matches are found, and they are not duplicates of the matches assigned to a different root,
        # return them
        if entry_heads:
            non_duplicates = [h for h in entry_heads if h not in used]
            if non_duplicates:
                return non_duplicates

        # in case no non-duplicate matches are found, save the most likely duplicate match
        if not duplicate:
            duplicate = entry_heads

    # if there are no non-duplicate matches found, return the most likely duplicate match, if it exists
    return duplicate


if __name__ == '__main__':
    # get all dictionary entries and forms
    parser = JSONGetter()
    lexicon = requests.get('https://mg.alhatorah.org/MikraotGedolot/ajax/Lexical')
    parser.feed(lexicon.text)
    lexicon = parser.json_content

    data = json.loads(lexicon)
    data = data['lexicon']['index']['data'][:-1]  # Last element is the number 0

    # map each word to the headword  of  its entry in the dictionary
    print('*'*10 + 'MAPPING TO BDB HEADWORDS' + '*'*10)

    direct_map = defaultdict(lambda: [])
    for forms in data[:200]:
        headword = [re.sub(r'\(.*\)', '', forms[0]).strip()]

        if not has_nikkud(headword[0]) and headword[0] not in jastrow_all:
            rlprint(headword[0])
            page_content = requests.get('https://mg.alhatorah.org/MikraotGedolot/lexicon/lexicon.php/'
                                        + str(forms[1]['s']))
            headword = extract_heads(page_content)

        headword = [order_nikkud(h) for h in headword]

        for form in forms:
            if type(form) == dict:
                continue

            ## RECORD IF WORD IS ARAMAIC, AND THEN TAKE INTO ACCOUNT RESERVED WORDS

            # clean the word of extra info and make sure that words end in sofits and have no internal sofits
            form = re.sub(r'\(.*\)', '', form).strip()
            headroot = ((((headword[0].replace('ך', 'כ')).replace('ם', 'מ'))
                         .replace('ן', 'נ')).replace('ף', 'פ')).replace('צ', 'ץ')
            form = form.replace('*', headroot)
            form = make_sofit(form)

            direct_map[order_nikkud(form)] += headword

    # remove duplicate heads
    dict_map = {w: list( dict.fromkeys(direct_map[w]) ) for w in direct_map}

    # map each headword to its corresponding headword in the jastrow by searching all_forms
    print('*'*10 + 'MAPPING TO JASTROW RIDs' + '*'*10)

    bdb_to_jas = defaultdict(lambda: [])
    linked = {}
    for word in dict_map:
        rlprint('--' + word + '--')

        for root in dict_map[word]:
            if root not in linked:
                linked[root] = get_jastrow_heads(root, [h for hs in linked.values() for h in hs])
            bdb_to_jas[word] += linked[root]
            bdb_to_jas[word] = list(dict.fromkeys(bdb_to_jas[word]))

            for match in linked[root]:
                rlprint(match, lang='')

    # write to csv file
    df_mapping = pd.DataFrame.from_dict(bdb_to_jas, orient='index')
    df_mapping.to_csv('bdb_mappings3.csv', encoding='utf-8-sig')
