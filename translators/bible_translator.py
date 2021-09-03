import json

# generated from database_formatters/bdb_jastrow_linker.py
path = './data/bdb_to_jastrow.json'
with open(path, encoding='utf-8') as f:
    bdb_mapping = json.load(f)


def translate(word):
    if word in bdb_mapping:
        # The Bible translate uses MALEH spelling
        return bdb_mapping[word['word'][1]]
    else:
        return None
