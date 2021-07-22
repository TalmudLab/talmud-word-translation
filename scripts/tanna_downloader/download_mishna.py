import requests
import re
import string
import json

"""
Downloads the raw text of every masekhet of mishna, for the purpose of creating a corpus of all words
in Rabbinic Hebrew. Text of the Mishna with nikkud is downloaded from Sefaria.
"""

with open('mishnas.txt') as f: mishnas = f.readlines()
mishnas = [m.strip('\n') for m in mishnas]

complete_text = ''

if __name__ == '__main__':
    for name in mishnas:
        print(name)
        if name != 'Pirkei Avot':
            length = requests.get('http://www.sefaria.org/api/texts/Mishnah_' + name)
        else:
            length = requests.get('http://www.sefaria.org/api/texts/' + name)
        length = json.loads(json.dumps(length.json()))['length']
        if name != 'Pirkei Avot':
            original = requests.get('http://www.sefaria.org/api/texts/Mishnah_' + name + '.1-' + str(length))
        else:
            original = requests.get('http://www.sefaria.org/api/texts/' + name + '.1-' + str(length))
        original = json.loads(json.dumps(original.json()))['he']
        original = [m for ch in original for m in ch]

        merged = (' '.join(original)).replace('\n', '')
        no_refs = re.sub(r'\(.*?\)', '', merged)
        no_punc = re.sub(r'[' + string.punctuation + ']+?', '', no_refs)

        complete_text += ' ' + no_punc

    stripped = re.sub(r'\s+', ' ', complete_text)
    with open('all_mishnayot.txt', 'w', encoding='utf-8') as f: f.write(stripped)