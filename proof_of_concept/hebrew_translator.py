import requests
import json
import cachemanager
from deconstruct import *


def find_matches():
    return


def translate(word):
    if word in cachemanager.heb_cache:
        return cachemanager.heb_cache[word]

    print('\tGetting page response...')
    page = requests.get('http://services.morfix.com/translationhebrew/TranslationService/GetTranslation/' + word)
    print('\tPage received!')
    data = json.loads(page.text)

    if data['ResultType'] == 'NoResult' or data['ResultType'] == 'Suggestions':
        word = heb_plural(word)
        print('\tGetting page response...')
        page = requests.get('http://services.morfix.com/translationhebrew/TranslationService/GetTranslation/' + word)
        print('\tPage received!')
        data = json.loads(page.text)

    if data['ResultType'] == 'NoResult':
        return []

    results = []
    for w in data['Words']:
        if w['PartOfSpeech'] in morfix_pos_to_yap_pos:
            pos = morfix_pos_to_yap_pos[ w['PartOfSpeech'] ][0]
        else:
            pos = w['PartOfSpeech']
        word = w['InputLanguageMeanings'][0][0]['DisplayText']
        results.append((word, pos))

    cachemanager.add_to_cache(word, results)

    return results
