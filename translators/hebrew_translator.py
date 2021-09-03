import requests
import json
from utils import cachemanager
from utils.deconstruct import *


def find_matches():
    return


def translate(word, pos):
    # The Hebrew translating uses MALEH spelling for maximum data
    word = word['word'][1]
    pos = word['pos']

    word = to_hitpael(word)

    while True:
        try:
            page = requests.get(
                'http://services.morfix.com/translationhebrew/TranslationService/GetTranslation/' + word, timeout=1)
        except requests.ReadTimeout:
            continue

        data = json.loads(page.text)
        if data['ResultType'] == 'NoResult':
            word = heb_plural(word)
            continue

    if data['ResultType'] == 'NoResult':
        return None

    results = []
    for w in data['Words']:
        pos = morfix_pos_to_yap_pos[ w['PartOfSpeech'] ]
        word = w['InputLanguageMeanings'][0][0]['DisplayText']
        results.append((word, pos))

    cachemanager.add_to_cache(word, results)

    return [result for result in results if result[1] == pos]
