# Constants
nikkud = ['ֹ', 'ְ', 'ּ', 'ׁ', 'ׂ', 'ָ', 'ֵ', 'ַ', 'ֶ', 'ִ', 'ֻ', 'ֱ', 'ֲ', 'ֳ', 'ׇ']
alphabet = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ך', 'ל', 'מ',
            'ם', 'נ', 'ן', 'ס', 'ע', 'פ', 'ף', 'צ', 'ץ', 'ק', 'ר', 'ש', 'ת']
punctuation = ['״', '׳']
characters = alphabet + nikkud + punctuation


# Turns a token into a vector
# dim is the vector dimension parameter. By default it is 968 because that happens to be the dimension of the current
# 40,000 word model, but I'll need to fix this somehow so you don't need to change it each time.
def tok_to_vec(token, dim=968):
    # print(token)
    vec = [0]*dim
    for i in range(len(token)):
        vec[i * len(characters) + characters.index(token[i])] = 1
    return vec


# Removes any extraneous characters that hadn't been eliminated earlier
def clean(token):
    return ''.join([c for c in token if c in characters])