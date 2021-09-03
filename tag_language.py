import os
import json
from src.languagetagger.gemaratagger import tag_gemara_chunk
from src.languagetagger.identifiers import *
from utils.rlprint import rlprint

base_path = './data/connected_talmud/'
model_file = './src/pshat/PSHAT_final_model.model'
out_path = './data/lang_tagged_talmud/'

files = os.listdir(base_path)

if __name__ == '__main__':
    for file in files:
        title = file[:-5]
        do_masekhet = input('Proceed with ' + title + '? y/n: ')
        if do_masekhet == 'n':
            continue

        with open(base_path + file, encoding='utf-8') as f:
            text = json.load(f)

        lang_tagged = []
        last_words = []
        for page in text:
            print('-'*20 + page['page'] + '-'*20)

            lang_tagged.append([])
            for chunk in page['content']:
                bible = chunk['bible']
                chunk_text = chunk['text']

                # first we need to make sure that there exists a word in the Maleh word corpus corresponding
                # to a Sefaria word, otherwise the word will be '' and will not be properly predicted
                words_for_tagging = [word_forms[1] if word_forms[1] != '' else word_forms[0]
                                     for word_forms in chunk_text]

                # Mishnas are either Rabbinic Hebrew or Biblical Hebrew
                if chunk['type'] == 'm' or chunk['type'] == 'mc':
                    lang_tagged[-1].append({'type': chunk['type'],
                                            'text': [{'lang': ('B' if words_for_tagging[i] in bible else 'R'),
                                                      'word': chunk_text[i]} for i in range(len(chunk_text))]})
                    continue

                # Gemaras are more complex and need a language model to distinguish their languages
                chunk_langs = tag_gemara_chunk(words_for_tagging)

                # First, try tagging based solely on probabilities, leaving ambiguous words as unidentified
                chunk_tagged = []
                for i in range(len(chunk_text)):
                    # If the word is in the Bible or Mishna, its language is auto-tagged accordingly
                    if words_for_tagging[i] in bible:
                        chunk_tagged.append({'lang': 'B', 'word': chunk_text[i]})
                    elif is_in_mishna(words_for_tagging[i]):
                        chunk_tagged.append({'lang': 'R', 'word': chunk_text[i]})
                    # Otherwise, base it on probabilities
                    elif chunk_langs[i] > 0.8:  # i.e. 80% or higher chance of being Hebrew
                        chunk_tagged.append({'lang': 'R', 'word': chunk_text[i]})
                    elif chunk_langs[i] < 0.2:  # i.e. 80% or higher chance of being Aramaic
                        chunk_tagged.append({'lang': 'A', 'word': chunk_text[i]})
                    else:
                        chunk_tagged.append({'lang': 'U', 'word': chunk_text[i]})

                # Disambiguate words that were identified as 'U'
                chunk_tagged = disambiguate_chunk(chunk_tagged, chunk_text, chunk_langs, chunk)

                lang_tagged[-1].append({'type': chunk['type'], 'text': chunk_tagged})

                # Lastly, we check gemaras that continue across a page to see if any of the last words on a page
                #                                                 == 1 means this is the first chunk on the page
                if chunk['type'] == 'gc' and len(lang_tagged[-1]) == 1 and last_words[1]['lang'] == 'U':
                    next_prob = chunk_langs[0]
                    if is_valid_trigram(last_words[0], chunk_tagged[0]):
                        last_word_lang = trigram_language_disambiguate(last_words[0]['prob'],
                                                                       last_words[1]['prob'], next_prob)
                        lang_tagged[-2][-1]['text'][-1]['lang'] = last_word_lang
                # saves the word/lang/probability of the last two words of the last chunk on the page
                elif chunk['type'] == 'gc' and len(chunk_tagged) >= 2:
                    last_words = [{'prob': chunk_langs[-2], 'lang': chunk_tagged[-2]['lang']},
                                  {'prob': chunk_langs[-1], 'lang': chunk_tagged[-1]['lang']}]
                else:
                    last_words = [{'prob': 0, 'lang': 'B'},
                                  {'prob': 0, 'lang': 'B'}]

                for w in chunk_tagged:
                    print(w['lang'], end='\t')
                    rlprint(w['word'][1])

        # write to output file, without inessential data (i.e. daf numbers, sources)
        with open(out_path + file, 'w+', encoding='utf-8') as f:
            json.dump(lang_tagged, f, ensure_ascii=False, indent=4)
