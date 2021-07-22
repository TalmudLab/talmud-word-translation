import requests
import re
import string
from html.parser import HTMLParser

"""
Downloads the raw text of every available section of the Mekhilta, for the purpose of creating a corpus of all words
in Rabbinic Hebrew. Text of the Mekhilta with nikkud is downloaded from Wikisource.
"""


class _GetText(HTMLParser):
    """
    Extends the HTMLParser object and retrieves Tosefta text.
    """
    def __init__(self):
        super().__init__()
        self.begin = False      # Beginning of a text section
        self.internal = False   # Ignores any divs inside of a text section
        self.text = ''

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and self.begin:
            self.internal = True
        elif tag == 'div' and len(attrs) != 0:
            self.begin = attrs[0][1] == 'poem'

    def handle_endtag(self, tag):
        if tag == 'div' and self.internal:
            self.internal = False
        elif tag == 'div' and self.begin:
            self.begin = False

    def handle_data(self, data):
        if self.begin:
            self.text += data + ' '


with open('mekhiltas.txt', encoding='utf-8') as f: mekhiltas = f.readlines()
mekhiltas = [m.strip('\n') for m in mekhiltas]

if __name__ == '__main__':
    complete_text = ''

    for name in mekhiltas:
        print(name)

        page = requests.get('https://he.wikisource.org/wiki/' + name)
        parser = _GetText()
        parser.feed(page.text)
        original = parser.text

        no_comments = re.sub(r'[<\(\[].*?[>\)\]]', '', original)
        no_punc = re.sub(r'[' + string.punctuation + ']+?', '', no_comments)

        complete_text += no_punc + ' '

    stripped = (re.sub(r'\s+', ' ', complete_text)).strip()
    with open('all_mekhiltas.txt', 'w', encoding='utf-8') as f: f.write(stripped)