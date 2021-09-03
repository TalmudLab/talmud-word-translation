import json

# downloaded from the Mongodb, only the dicta words and corresponding Jastrow RIDs
path = './data/dicta_to_jastrow.json'
with open(path, encoding='utf-8') as f:
    dicta_mapping = json.load(f)


def translate(word):
    if word in dicta_mapping:
        # The Dicta database keys are HASER words
        return dicta_mapping[word['word'][2]]
    else:
        return None
