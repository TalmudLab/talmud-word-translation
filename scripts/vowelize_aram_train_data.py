import json
import os
from utils.rlprint import rlprint
from utils.deconstruct import remove_nikkud
import sys

import re
import string


def run_on_sefaria_cal(cal_folder):
    vowelized_words = []

    for m in vowelized_masekhtot_cal_sefaria:
        cont = input('Proceed with ' + m + '? y/n: ')
        if cont == 'n':
            continue

        print('*' * 20 + m + '*' * 20)

        with open(vowelized_folder + m + '.json', encoding='utf-8') as f:
            vow_text = json.load(f)
        vow_mas = {p['page']: [[re.sub(r'[' + string.punctuation + ']', '', form) for form in w_forms]
                               for chunk in p['content'] for w_forms in chunk['text']] for p in vow_text}
        devoweled = {
            page_num: [[re.sub(r'[״׳]', '', remove_nikkud(form)) for form in forms] for forms in vow_mas[page_num]] for
            page_num in vow_mas}

        cal_mas = {}
        cal_pages = os.listdir(cal_folder + m)
        for p in vow_mas:
            if p + '.json' not in cal_pages:
                continue

            with open(cal_folder + m + '/' + p + '.json', encoding='utf-8') as f:
                cal_text = json.load(f)
            cal_words = [(w['word'], w['class']) for w in cal_text['words']]
            cal_mas[p] = cal_words

        for p in cal_mas:
            print('-' * 20 + p + '-' * 20)

            vow_index = -1
            for word, w_class in cal_mas[p]:
                word = re.sub(r'[׳״' + string.punctuation + ']', '', word)

                for i in range(vow_index + 1, min(vow_index + range_of_search + 1, len(vow_mas[p]))):
                    if word in devoweled[p][i]:
                        if w_class == 'talmud':
                            vowelized_words.append({'tag': 'A', 'word': vow_mas[p][i][1]})
                        vow_index = i
                        break

                    elif i == min(vow_index + range_of_search, len(vow_mas[p]) - 1):
                        print('''Error: Missed word!
                                  Select the first index from below that matches the query.
                                  Query: ''', end='')
                        rlprint(word)

                        for j in range(vow_index + 1, i + 1):
                            print(j, end=' ')
                            rlprint(vow_mas[p][j][1])
                        proper_index = input('\nMatching index (x to skip, p to see previous words): ')

                        steps = 1
                        while proper_index == 'p':
                            back = steps * range_of_search
                            for j in range(vow_index - back, vow_index - back + range_of_search + 1):
                                print(j, end=' ')
                                rlprint(vow_mas[p][j][1])
                            steps += 1
                            proper_index = input('\nMatching index (x to skip, p to see previous words): ')

                        if proper_index == 'x':
                            break

                        vow_index = int(proper_index)
                        vowelized_words.append({'tag': 'A', 'word': vow_mas[p][vow_index][1]})
                        break

        with open(output_path + m + '.json', 'w+', encoding='utf-8') as f:
            json.dump(vowelized_words, f, ensure_ascii=False, indent=4)


def run_on_base_cal(cal_folder):
    for m in vowelized_masekhtot_base_cal:
        vowelized_words = []

        cont = input('Proceed with ' + m + '? y/n: ')
        if cont == 'n':
            continue

        print('*' * 20 + m + '*' * 20)

        # Open and clean the aligned Sefaria/Maleh/Haser Masekhet
        with open(vowelized_folder + m + '.json', encoding='utf-8') as f:
            vow_text = json.load(f)
        vow_mas = [[re.sub(r'[' + string.punctuation + ']', '', form) for form in w_forms]
                   for p in vow_text for chunk in p['content'] for w_forms in chunk['text']]
        devoweled = [[re.sub(r'[״׳]', '', remove_nikkud(form)) for form in w_forms] for w_forms in vow_mas]

        # Open and clean the CAL masekhet
        with open(cal_folder + m + '.txt', encoding='utf-8') as f:
            cal_text = f.read()
        cal_cleaned = re.sub(r'".*"', '', cal_text)
        cal_cleaned = re.sub(r'"\{.*\}"', '', cal_cleaned)
        cal_mas = (''.join([c for c in cal_cleaned if c in 'אבגדהוזחטיכךלמםנןסעפףצץקרשת׳ '])).split()

        vow_index = -1
        for word in cal_mas:
            print('-' * 20 + str(vow_index) + '-' * 20)

            word = re.sub(r'[׳״' + string.punctuation + ']', '', word)

            for i in range(vow_index + 1, min(vow_index + range_of_search + 1, len(vow_mas))):
                if word in devoweled[i]:
                    vowelized_words.append({'tag': 'A', 'word': vow_mas[i][1]})
                    vow_index = i
                    break

                elif i == min(vow_index + range_of_search, len(vow_mas) - 1):
                    for j in range(vow_index + 1, i + 1):
                        print(j, end=' ')
                        rlprint(vow_mas[j][1])

                    print('''Error: Missed word!
                                  Select the first index from below that matches the query.
                                  Query: ''', end='')
                    rlprint(word)

                    proper_index = input('\nMatching index (x to skip, p to see previous words): ')


                    steps = 1
                    while proper_index == 'p':
                        back = steps * range_of_search
                        for j in range(vow_index - back, vow_index - back + range_of_search + 1):
                            print(j, end=' ')
                            rlprint(vow_mas[j][1])
                        steps += 1
                        proper_index = input('\nMatching index (x to skip, p to see previous words): ')

                    if proper_index == 'x':
                        break

                    vow_index = int(proper_index)
                    vowelized_words.append({'tag': 'A', 'word': vow_mas[vow_index][1]})
                    break

        with open(output_path + m + '.json', 'w+', encoding='utf-8') as f:
            json.dump(vowelized_words, f, ensure_ascii=False, indent=4)


# Should be updated as more masekhtot are vowelized by Dicta in order to enlarge training set
vowelized_masekhtot_cal_sefaria = ['Bava_Batra', 'Berakhot', 'Eruvin', 'Pesachim', 'Shabbat']
vowelized_masekhtot_base_cal = ['Meilah', 'Nazir', 'Rosh_Hashanah', 'Sukkah', 'Yoma']

cal_path = './data/'

vowelized_folder = './data/aligned_talmud/'
output_path = './data/vowelized_cal_texts/'

range_of_search = 50  # NEEDS TO BE MANUALLY ADJUSTED


if __name__ == '__main__':
    cal_path += sys.argv[1]

    if cal_path == './data/cal_sefaria_matched':
        run_on_sefaria_cal(cal_path + '/')
    elif cal_path == './data/remaining_cal_texts':
        run_on_base_cal(cal_path + '/')
    else:
        print('Error: invalid folder.')
