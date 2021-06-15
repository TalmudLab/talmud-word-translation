import string
import re

import requests
import json

from utils.format import _unite_end_chunk

"""
Contains a public-facing method to re-add standardized punctuation from the Steinsaltz
version of the Talmud on Sefaria. Note that this is NOT the same as the dicta punctuation,
which has not yet been extended to the entirety of the Talmud, whereas the Steinsaltz is completely
punctuated.

INCOMPLETE
"""


def _unite_steinsaltz(pgs):
    """
    Unites all of the chunks into a single list of strings, removing page divisions, and uniting end chunks.
    Also removes the final hadran on the end of the last page.

    :param pgs: the pages of the commentary, formatted as a list containing lists of strings (sub-lists contain
                the chunk divisions)
    :return: a list of strings containing the text
    """
    if len(pgs) == 0:
        return []
    elif len(pgs) == 1:
        c_pages = []
        page = pgs[0][:-1]
    else:
        c_pages = _unite_end_chunk(pgs)
        page = c_pages[0]
    return page + _unite_steinsaltz(c_pages[1:])


def _remove_steinsaltz_mishna(chunks, remove=True):
    """
    Removes all mishnayot from the commentary, so that all that's left is the text of the gemara commentary.

    To be called on return value of _unite_steinsaltz.

    :param chunks:
    :param remove: DO NOT SET. Set to True by default in order to remove first mishna, which does not begin with "מתני׳"
    :return: a list of strings that is identical to "chunks," except that all mishnayot have been removed
    """
    if len(chunks) == 0:
        return []

    rm = remove
    start_mishna = re.search('<big>.+? משנה</big>', chunks[0])
    start_gemara = re.search('<big>.+? גמרא</big>', chunks[0])
    if start_gemara:
        rm = False
    if start_mishna:
        rm = True

    if rm:
        return _remove_steinsaltz_mishna(chunks[1:], remove=rm)
    else:
        return [chunks[0]] + _remove_steinsaltz_mishna(chunks[1:], remove=rm)


def _prep_steinsaltz(stein):
    """
    Prepares the Steinsaltz text in the same way as the Talmud text, by removing
    page numbers and non-text, and uniting separated text chunks.

    :param stein: text of the Steinsaltz commentary, pulled from the Sefaria text database.
    :return: a list of strings containing the text without page divisions or non-text
    """
    no_divisions = _unite_steinsaltz(stein)
    no_mishna = _remove_steinsaltz_mishna(no_divisions)
    return no_mishna


def _remove_extraneous(chunk):
    """
    Cleans the punctuation from an individual iteration of _remove_commentary. Removes extra
    punctuation from commentary section, appends punctuation to end of preceding words.

    :param chunk: the text chunk with all punctuation, separated by spaces
    :return: the chunk with only the proper punctuation
    """
    chunk = re.sub('\s+', ' ', chunk)

    strength = ['', '—', ',', '.', '!', '?']  # index is relative strength of punctuation; does not include quotations

    cleaned = '  '
    punc = ''
    for char in chunk:
        print(cleaned)
        if char != ' ' and cleaned[-1] in '"\'.?,!—':
            cleaned += ' '
        if not (char in '"\'.?,!—'):
            cleaned += char
            punc = ''
        if char in '"\'':
            cleaned += char
        if char in '.?,!—':
            punc = char if strength.index(char) > strength.index(punc) else punc
            if cleaned[-2] in '.?,!—':
                cleaned = cleaned[:-2]
            cleaned += ' ' + char

    print('\n')
    return cleaned


def _remove_commentary(stein):
    """
    Removes everything from the Steinsaltz that is not in the gemara text itself,
    aside from punctuation. Cleans punctuation.

    :param stein: text of the steinsaltz commentary, formatted as a list of strings as prepared by _prep_steinsaltz
    :return: a list of strings in the same format and length as gemara, but with punctuation added
    """
    if len(stein) == 0:
        return []

    s_chunk = stein[0]
    c_chunk = re.findall('<b>.+?</b>|[.?,!—"\']', s_chunk)
    c_chunk = re.sub('<.+?>', '', ' '.join(c_chunk))

    return [_remove_extraneous(c_chunk)] + _remove_commentary(stein[1:])


def get_steinsaltz(masekhet):
    """
    Gets Steinsaltz's commentary on the masekhet, which includes punctuation.

    :param text: the name of the masekhet
    :return: the corresponding Steinsaltz commentary
    """
    all_data = requests.get('http://www.sefaria.org/api/texts/Steinsaltz_on_' + masekhet + '.2-1000')
    stein = json.loads(json.dumps(all_data.json(), indent=4))['he']
    return stein


def punctuated_masekhet(stein):
    """
    Gets the masekhet with Steinsaltz punctuation.

    :param masekhet: the name of the masekhet
    :return: a list of strings containing the text divided into chunks, with Steinsaltz punctuation
    """
    prepped = _prep_steinsaltz(stein)
    punctuated = _remove_commentary(prepped)
    return punctuated


def steinsaltz_refs(text):
    """

    :param text:
    :return:
    """
    return