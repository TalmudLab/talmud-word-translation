from utils.hebrew import *


def order_nikkud(token):
    """
    Takes a Hebrew word, and orders the nikkud within that word as follows:
    1. The letter
    2. The shin/sin dot, if present
    3. The dagesh, if present
    4. All other nikkud
    It also substitutes the strange long kamatz with its regular counterpart.

    :param head: the headword
    :return: the restructured word
    """
    token = token.replace(other_kamatz, long_nikkud[0]) + '.'  # Ensures that if the last char is a vowel, the loop
                                                               # still runs one more time.
    word = ''
    nik = []
    for c in token:
        if c in alphabet or c == '.':
            if shin in nik:
                word += nik.pop(nik.index(shin))
            if sin in nik:
                word += nik.pop(nik.index(sin))
            if dagesh in nik:
                word += nik.pop(nik.index(dagesh))
            if holam in nik:
                word += nik.pop(nik.index(holam))
            if len(nik) > 0:
                word += ''.join(nik)
                nik = []
            word += c if c != '.' else ''
        else:
            nik.append(c)
    return word


def has_nikkud(head):
    return any([1456 <= ord(c) <= 1479 for c in head])


def make_sofit(word):
    return word[:-1] + ('ך' if word[-1] == 'כ'
                        else ('ם' if word[-1] == 'מ'
                              else ('ן' if word[-1] == 'נ'
                                    else ('ף' if word[-1] == 'פ' else word[-1]))))
