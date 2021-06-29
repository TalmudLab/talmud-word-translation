import re
from string import punctuation

import requests
import json

from utils.hebrew import *
from utils.respell import sub_kamatz

"""
A module containing classes that deal with texts from Sefaria, including storage, manipulation, and tagging.
Mainly a way to consolidate and restructure format2.
"""


def _does_continue(chunk):
    """
    Auxiliary function that checks if an end chunk continues onto the next page.

    :param chunk: the end chunk to be checked
    :return: True if the chunk continues onto the next page, False otherwise.
    """
    return not ((chunk[-1] == '.') or (chunk[-1] == '?') or (chunk[-1] == '!'))


def _break_chunk(chunk):
    """
    Breaks a text chunk into a list of words and punctuation.

    :param chunk: the chunk of text, a string
    :return: a list containing the words and punctuation in order
    """
    add_space = lambda m: " {} ".format(m.group())
    spaced = re.sub(r'[' + punctuation + r'…׳״—]+?', add_space, chunk)
    as_list = re.split('\s\s*', spaced)
    return as_list if as_list[-1] != '' else as_list[:-1]


def _clean_text(chunk):
    """
    Removes html and weird kamatz.

    :param chunk: a chunk of text
    :return: the chunk without html and the weird kamatz.
    """
    chunk = sub_kamatz(chunk)
    return re.sub(r'</*[a-z]+>', '', chunk)


def _tag(page, prev):
    """
    Tags the beginnings of mishnayot and gemaras, and tags when a chunk is split across two pages,
    by making them tuples with the following code for second entry:
    - 'm' = start of a mishna
    - 'mc' = mishna continued across page
    - 'g' = start of a gemara
    - 'gc' = gemara continued across page

    :param page: a page (amud) of Talmud
    :param prev: the tag of the final chunk of the previous page
    :return: the cleaned and tagged page
    """
    tags = []
    tag = ''
    for c in page:
        curr = 'm' if c[0] == 'מַתְנִי' else ('g' if c[0] == 'גְּמָ' else '0')
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
        tag += '' if page.index(c) != len(page) - 1 else 'c' * _does_continue(c)
        tags.append(tag)
    return tags


class Masekhet:
    """
    A class to represent a masekhet, storing the original text, the text formatted as lists representing the "chunks,"
    and the tags of those chunks (see utils.texts._tag). Also contains functions for accessing and manipulating
    the text.
    """
    def __init__(self, name):
        """
        Gets and stores the full text of a masekhet from Sefaria and removes html.
        Stores the text in multiple formats for viewing and internal processing.

        :param name: the name of the masekhet, formatted per the Sefaria API instructions.
        """
        length = requests.get('http://www.sefaria.org/api/texts/' + name + '.2')
        length = json.loads(json.dumps(length.json(), indent=4))['length']
        all_data = requests.get('http://www.sefaria.org/api/texts/' + name + '.2-' + str(length))
        self.original = json.loads(json.dumps(all_data.json(), indent=4))['he']

        self.pages = []
        for page in self.original:
            prepped = [_break_chunk(_clean_text(c)) for c in page]
            self.pages.append(prepped)

        self.tags = [['m']]
        for p in self.pages:
            tagged = _tag(p, self.tags[-1][-1])
            self.tags.append(tagged)
        self.tags = self.tags[1:]

    def __getitem__(self, loc):
        return self.pages[loc]

    def __len__(self):
        return len(self.pages)


class Library:
    """
    A class to represent a collection of masekhtot.
    """
    def __init__(self, *names):
        for n in names:
            m = Masekhet(n)
            setattr(self, n.lower(), m)
