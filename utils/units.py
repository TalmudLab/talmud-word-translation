from string import punctuation
from nltk import ngrams

from utils.respell import *
from utils.deconstruct2 import *

"""
A module containing classes that deal with individual units of ideas, namely chunks, sentences, and words.
Mainly a way to consolidate and restructure deconstruct2.
"""


def _does_continue(chunk):
    """
    Auxiliary function that checks if an end chunk continues onto the next page.

    :param chunk: the end chunk to be checked
    :return: True if the chunk continues onto the next page, False otherwise.
    """
    return not ((chunk[-1] == '.') or (chunk[-1] == '?') or (chunk[-1] == '!'))


def _clean_text(chunk):
    """
    Removes html and weird kamatz.

    :param chunk: a chunk of text
    :return: the chunk without html and the weird kamatz.
    """
    chunk = sub_kamatz(chunk)
    return re.sub(r'</*[a-z]+>', '', chunk)


def _break_sentences(chunk, soft=True):
    """
    Takes a punctuated chunk of text and breaks it into individual sentences.

    :param chunk: the punctuated chunk of text, a string
    :param soft: whether to count soft breaks (colons and semicolons) as EOS markers, a bool; defalts to True
    :return: the individual sentences, a list of Sentences
    """
    punc = r'(.*?[!\.\?:;][…׳״]*)' if soft else r'(.*?(!|\.|\?)[…׳״]*)'
    pattern = re.compile(punc)
    return [Sentence(s) if s[0] != ' ' else Sentence(s[1:]) for s in pattern.split(chunk) if s != '']


def _break_tokens(sentence):
    """
    Breaks a sentence into a list of words and punctuation.

    :param chunk: the sentence, a string
    :return: a list containing the words and punctuation in order
    """
    add_space = lambda m: " {} ".format(m.group())
    spaced = re.sub(r'[' + punctuation + r'…׳״—]+?', add_space, sentence)
    as_list = re.split(r'\s\s*', spaced)
    return as_list if as_list[-1] != '' else as_list[:-1]


class Word:
    """
    A class that contains individual words/tokens. Its default value is the word itself, and also stores the
    language of the word and the POS, if known. Methods of deconstruction can be called on it directly
    to get different spellings, orderings, etc.
    """
    def __init__(self, word, lang='u', pos='u'):
        """
        :param word: The word itself, a string
        :param lang: The language of the word, if known; a string. Defaults to 'u' according to the following code:
            - 'u' = unknown
            - 'a' = Aramaic
            - 'rh' = Rabbinic Hebrew
            - 'bh' = Biblical Hebrew
        :param pos: The POS of the word, if knownl a string. Defaults to 'u' according to the following code:
            - 'u' = unknown
            - 'v' = verb
            - 'n' = noun
            - 'j' = adjective
            - 'd' = adverb
            - 'p' = preposition
            - 'c' = conjunction
        """
        self._lang = lang
        self._pos = pos
        self._word = sub_kamatz(word)

        self.orders = order_nikkud(word)
        self.translations = []

    def __str__(self):
        return self._word

    def __getitem__(self, loc):
        return self._word[loc]

    def __len__(self):
        return len(self._word)

    def set_pos(self, pos):
        """
        Use to set the POS to a new value, if the POS is discovered or recalculated.

        :param pos: a string, the new POS (see code in __init__)
        """
        self._pos = pos

    def set_lang(self, lang):
        """
        Use to set the language to a new value, if the language is discovered or recalculated.

        :param lang: a string, the new language (see code in __init__)
        """
        self._lang = lang

    def alt_order(self, index=0):
        """
        Alters the primary spelling of the word to one of the alternates contained in self.orders, by index.
        The primary spelling, which is contained in "self.word," is used in all internal and external functions.

        :param index: the index within the list self.orders, an int
        """
        self._word = self.orders[index]

    def spellings(self):
        """
        Returns the possible spellings of the word from maleh/haser form.
        TODO: complete
        """
        return

    def no_nikkud(self):
        """
        Returns the word without nikkud.
        """
        alph_only = ''.join([c for c in self._word if not (1456 <= ord(c) <= 1479)])
        return alph_only

    def add_translation(self, headword, lang='', pos=''):
        """
        Stores possible translations of the word.

        :param headword: the headword in Jastrow that is linked to (TODO: incorporate RID)
        :param lang: to be set if self._lang == 'u,' stores the language of this word
        :param pos: to be set if self._pos == 'u,' stores the POS of this word
        """
        tr = [headword] + [lang]*(self._lang == 'u') + [pos]*(self._pos == 'u')
        self.translations.append( tuple(tr) )


class Sentence:
    """
    A class that contains individual sentences. It does so by acting as a collection of Words.
    """

    def __init__(self, sentence, context='g', lang='u'):
        """
        :param sentence: The sentence itself, a string, punctuated with nikkud.
        :param: context: The context of the sentence, 'g' for gemara and 'm' for mishna; defaults to 'g.'
        :param lang: The language of the sentence as a whole, if known; a string. Defaults to 'u' according to the
        following code:
            - 'u' = unknown
            - 'a' = Aramaic
            - 'rh' = Rabbinic Hebrew
            - 'bh' = Biblical Hebrew
        """
        self._lang = lang
        self._context = context
        self._original = sentence

        self.tokens = [Word(t) if (t not in punctuation + '…׳״—') else t for t in _break_tokens(sentence)]

    def __str__(self):
        return self._original

    def __getitem__(self, loc):
        return self.tokens[loc]

    def __len__(self):
        return len(self.tokens)

    def ngrams(self, n=2):
        """
        Returns an n-gram iterator over the tokens.

        :return: an n-gram iterator from the nltk module
        """
        return ngrams([str(t) for t in self.tokens], n)


class Chunk:
    """
    A class that contains a full text chunk, the largest single-idea textual unit.
    """
    def __init__(self, chunk, context='u'):
        """
        :param sentence: The sentence itself, a string, punctuated with nikkud.
        :param: context: The context of the sentence:
            - 'g' for gemara
            - 'gc' for gemara continuing across a page
            - 'm' for mishna
            - 'mc' for mishna continuing across a page
            - 'u' for unknown; default
        """
        self._context = context
        self._original = chunk

        self.sentences = _break_sentences(chunk)

    def __str__(self):
        return self._original

    def __getitem__(self, loc):
        return self.sentences[loc]

    def __len__(self):
        return len(self.sentences)

    def set_context(self, context):
        """
        Resets the context, if it has been changed or discovered.

        :param context:
        """
        self._context = context
