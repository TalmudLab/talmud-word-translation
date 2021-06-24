"""
A module containing static variables for Hebrew language parsing.
"""

# Alphabetical characters
alphabet = 'אבגדהוזחטיכךלמםנןסעפףצץקרשת'
prefix_letters = 'אבדהוכלמקש'
gutturals = 'אחהער'
weak_letters = 'אהוחיענן'
strong_letters = 'בגדזטכךלמםספףצץקרשת'


# Nikkud
holam = 'ֹ'
shva = 'ְ'
dagesh = 'ּ'
shin = 'ׁ '
sin = 'ׂ '

other_kamatz = 'ׇ'              # used sometimes, unrecognized by Morfix
long_nikkud = ['ָ', 'ֵ']
short_nikkud = ['ַ', 'ֶ', 'ִ', 'ֻ']
reduced_nikkud = ['ֱ', 'ֲ ', 'ֳ']
# (Nikkud that corresponds to weak nikkud, with same indices)
reduced_correspondence = [shva, short_nikkud[0], long_nikkud[0]]

all_nikkud = [holam, shva, dagesh] + [shin, sin] + long_nikkud + short_nikkud + reduced_nikkud


# Hebrew and Aramaic specific prefixes
aram_which = ['דִּ', 'דְּ']
aram_on = 'אַ'
aram_interrogative = 'הֲ'
aram_intense = 'קָ'
aram_prefixes = aram_which + [aram_on, aram_interrogative, aram_intense]

heb_which = 'שֶׁ'


# Prefixes for both languages
conjunction = ['וְ', 'וּ', 'וָ']

definite_article = ['הֶָ', 'הָ', 'הַ']

inseparable_prepositions = ['לְ', 'לָ', 'לַ', 'לִ',
                            'כָ', 'כְ', 'כִ',
                            'כָּ', 'כְּ', 'כִּ',
                            'בִ', 'בַ', 'בְ',
                            'בִּ', 'בָּ', 'בְּ']

mem_prepositions = ['מֵ', 'מִ']

god_prefixes = ['לֵ', 'כֵ', 'כֵּ', 'בֵ', 'בֵּ']
maleh_prefixes = ['כִי', 'כִּי', 'מֵי', 'מִי']

# Combined complete Hebrew and Aramaic prefixes
aram_all = aram_prefixes + conjunction + definite_article + inseparable_prepositions + mem_prepositions  # \
                         # + god_prefixes + maleh_prefixes

heb_all = [heb_which] + conjunction + definite_article + inseparable_prepositions \
                      + mem_prepositions # + god_prefixes + maleh_prefixes


# All prefixes
all_prefixes = aram_prefixes + [heb_which] + conjunction + definite_article + inseparable_prepositions \
                             + mem_prepositions  # + god_prefixes + maleh_prefixes
