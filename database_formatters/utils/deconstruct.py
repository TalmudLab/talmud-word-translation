from utils import hebrew


def alph_only(token):
    return ''.join([c for c in token if c in hebrew.alphabet])


# Note that this method is slightly different from the former, in that it leaves punctuation
def remove_nikkud(tok):
    return ''.join([c for c in tok if not (1456 <= ord(c) <= 1479)])