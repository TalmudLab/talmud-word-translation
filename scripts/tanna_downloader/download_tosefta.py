import requests
import re
import string
from html.parser import HTMLParser

"""
Downloads the raw text of every available masekhet of Tosefta, for the purpose of creating a corpus of all words
in Rabbinic Hebrew. Text of the Tosefta with nikkud is downloaded from Wikisource.
"""


class _GetText(HTMLParser):
    """
    Extends the HTMLParser object and retrieves Tosefta text.
    """
    def __init__(self):
        super().__init__()
        self.begin = False      # Beginning of a text section
        self.internal = False   # Ignores any divs inside of a text section
        self.text = []

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
            self.text.append(data)


with open('toseftas.txt', encoding='utf-8') as f: toseftas = f.readlines()
toseftas = [t.strip('\n') for t in toseftas]

if __name__ == '__main__':
    complete_text = ''

    for name in toseftas:
        print(name)

        page = requests.get('https://he.wikisource.org/wiki/%D7%AA%D7%95%D7%A1%D7%A4%D7%AA%D7%90_('
                              '%D7%91%D7%90%D7%A8%D7%99)/' + name)
        parser = _GetText()
        parser.feed(page.text)
        original = ' '.join(parser.text[:-2])

        no_headers = re.sub(r'(פרק|הלכה)\s+\S+', '', original)
        no_comments = re.sub(r'[<\(\[].*?[>\)\]]', '', no_headers)
        no_punc = re.sub(r'[' + string.punctuation + ']+?', '', no_comments)

        complete_text += no_punc + ' '

    stripped = (re.sub(r'\s+', ' ', complete_text)).strip()
    with open('all_toseftas.txt', 'w', encoding='utf-8') as f: f.write(stripped)