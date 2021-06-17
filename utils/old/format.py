import string
import re

import requests
import json

"""
Tools for formatting Talmud text pulled from Sefaria API.

The formatting removes all punctuation, niqqud, mishnas, and irrelevant terms (e.g. מתני׳).
It leaves only the "chunk" breaks, per the Steinsaltz division.
As such, page numbers are also deleted.

Note that some of the methods are recursion heavy and can only be completed by making
a call to sys.setrecursionlimit(X).

Most of these methods are background processes and should not be used directly.

TODO:
- Re-add page numbers.
- Re-divide end chunks if needed.
"""


def _strip_niqqud(s):
    """
    Removes niqqud from the text.

    :param s: a string containing a single text unit
    :return: the string without niqqud
    """
    return ''.join(['' if 1456 <= ord(c) <= 1479 else c for c in s])


def _strip_punc(s):
    """
    Removes punctuation from the text.
    Does not remove the ׳ character as this is used to identify non-text later.

    :param s: a string containing a single text unit
    :return: the string without punctuation
    """
    return re.sub('[' + string.punctuation + '״—]+?', '', s)


def _unite_end_chunk(pgs):
    """
    Concatenates the last chunk of an amud with the first chunk of the next amud.
    This is needed because chunks containing the same subject are sometimes divided across amudim.

    :param pgs: the pages of the text, formatted as a list containing lists of strings (sub-lists contain
                the chunk divisions)
    :return: a list of the same size and format, with the first chunk of the second page appended to the last chunk
             of the first page
    """
    curr_page = pgs[0][:-1] + [pgs[0][-1] + ' ' + pgs[1][0]]
    next_pages = [pgs[1][1:]] + pgs[2:]
    return [curr_page] + next_pages


def _unite_all(pgs):
    """
    Unites all of the chunks into a single list of strings, removing
    punctuation, niqqud, and page divisions, and uniting end chunks.
    Also removes the final hadran on the end of the last page.

    :param pgs: the pages of the text, formatted as a list containing lists of strings (sub-lists contain
                the chunk divisions)
    :return: a list of strings, containing all of the chunks of the text with partial formatting
    """
    if len(pgs) == 0:
        return []
    elif len(pgs) == 1:
        c_pages = []
        page = pgs[0][:-1]
    else:
        c_pages = _unite_end_chunk(pgs)
        page = c_pages[0]
    return [_strip_punc(_strip_niqqud(c)) for c in page] + _unite_all(c_pages[1:])


def _remove_mishna(chunks, remove=True):
    """
    Removes all mishnayot from the text, so that all that's left is the text of the gemara.

    To be called on return value of _unite_all.

    :param chunks: a list of strings containing the text, pre-formatted by _unite_all
    :param remove: DO NOT SET. Set to True by default in order to remove first mishna, which does not begin with "מתני׳"
    :return: a list of strings that is identical to "chunks," except that all mishnayot have been removed
    """
    if len(chunks) == 0:
        return []

    rm = remove
    #if chunks[0].split(' ')[0] == 'bigstrongגמ׳strongbig':
    if 'גמ׳' in chunks[0]:
        rm = False
    #if chunks[0].split(' ')[0] == 'bigstrongמתני׳strongbig':
    if 'מתני׳' in chunks[0]:
        rm = True

    if rm:
        return _remove_mishna(chunks[1:], remove=rm)
    else:
        return [chunks[0]] + _remove_mishna(chunks[1:], remove=rm)


def _drop_nontext(chunks):
    """
    Removes all text that is not really part of the gemara, namely "גמ׳" and הדרן.
    Also removes any leftover html characters.

    To be called on return value of _remove_mishna.

    :param chunks: a list of strings containing the text, pre-formatted by remove_mishna
    :return: a list of strings that is identical to "chunks," except that all "non-text" has been removed
    """
    for i in range(len(chunks)):
        c = re.sub('(br)*(bigstrong)+.*(strongbig)+', '', chunks[i])
        chunks[i] = c
    return [c for c in chunks if c != '']


def prep_text(text):
    """
    Prepares the text for further analysis, by removing punctuation, niqqud,
    page numbers, mishnayot, and non-text, and uniting separated text chunks.

    :param text: a list of sublists containing strings with the text of a set of amudim divided into chunks (presumably
                one masekhet)
    :return: a list of strings containing the text, prepared for analysis

    TODO: Remove extraneous whitespace.
    """
    united = _unite_all(text)
    no_mishna = _remove_mishna(united)
    only_text = _drop_nontext(no_mishna)
    return only_text


def get_masekhet(masekhet):
    """
    Gets the full text of a masekhet from Sefaria.

    :param masekhet: the name of the masekhet
    :return: a list a list of sublists containing strings with the text of the masekhet divided into chunks
    """
    all_data = requests.get('http://www.sefaria.org/api/texts/' + masekhet + '.2-1000')
    pages = json.loads(json.dumps(all_data.json(), indent=4))['he']
    return pages
