from utils.deconstruct import remove_nikkud
import sys

"""
A method to print characters from languages that have a right-to-left writing system in the proper
direction in a Windows Command Prompt. Special support for Hebrew language.
"""


def rlprint(*objects, sep=' ', end='\n', file=sys.stdout, flush=False, lang='heb'):
    fn = remove_nikkud if lang == 'heb' else lambda i: i
    rev = tuple([fn(str(o[::-1])) for o in objects])
    for o in rev:
        print(o, sep=sep, end=end, file=file, flush=flush)
