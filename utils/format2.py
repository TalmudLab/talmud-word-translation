import re

import requests
import json

from utils.hebrew import *

"""
Updated version of format to allow for more flexibility as we move from testing to execution.

Tools for formatting Talmud text pulled from Sefaria API.

These tools assume the text has been punctuated and vowelized. All of them will, nevertheless, work
on non-punctuated/vowelized text, except _does_continue will always return True.
"""


def _does_continue(chunk):
    """
    Auxiliary function that checks if an end chunk continues onto the next page.

    :param chunk: the end chunk to be checked
    :return: True if the chunk continues onto the next page, False otherwise.
    """
    return not ((chunk[-1] == '.') or (chunk[-1] == '?') or (chunk[-1] == '!'))


def _tag(page, prev):
    """
    Removes html, tags pages (see get_masekhet docs).

    :param page: a page (amud) of Talmud
    :param prev: the tag of the final chunk of the previous page
    :return: the cleaned and tagged page
    """
    tagged = []
    tag = ''
    for c in page:
        chunk = re.sub(r'</*[a-z]+>', '', c)
        chunk = re.sub(other_kamatz, long_nikkud[0], chunk)             # replacement of the weird kamatz
        curr = 'm' if chunk[:8] == 'מַתְנִי׳' else ('g' if chunk[:6] == 'גְּמָ׳' else '0')
        if prev == 'mc' or prev == 'gc':
            tag = prev
            prev = prev[0]
        elif curr == '0':
            tag = prev
        elif curr != prev:
            tag = curr
            prev = curr
        else:
            tag = prev
        tag += '' if page.index(c) != len(page)-1 else 'c'*_does_continue(c)
        tagged.append((chunk, tag))
    return tagged


def get_masekhet(masekhet):
    """
    Gets the full text of a masekhet from Sefaria and removes html, indicator words (i.e. מַתְנִי׳ and גְּמָ׳).
    Tags the beginnings of mishnayot and gemaras, and tags when a chunk is split across two pages,
    by making them tuples with the following code for second entry:
    - 'm' = start of a mishna
    - 'mc' = mishna continued across page
    - 'g' = start of a gemara
    - 'gc' = gemara continued across page

    :param masekhet: the name of the masekhet
    :return: a list of sublists containing tuples, where each sublist is an amud, and each tuple contains a chunk of
             Talmud with its proper tag
    """
    length = requests.get('http://www.sefaria.org/api/texts/' + masekhet + '.2')
    length = json.loads(json.dumps(length.json(), indent=4))['length']
    all_data = requests.get('http://www.sefaria.org/api/texts/' + masekhet + '.2-' + str(length))
    pages = json.loads(json.dumps(all_data.json(), indent=4))['he']

    cleaned = [[('', 'm')]]
    for p in pages:
        tagged = _tag(p, cleaned[-1][-1][1])
        cleaned.append(tagged)
    return cleaned[1:]
