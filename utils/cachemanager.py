import csv


heb_cache = {}


def add_to_cache(word, results=None):
    global heb_cache
    heb_cache[word] = results


def save_hebrew(csv_file):
    global heb_cache
    with open(csv_file, 'a', encoding='utf-8', newline='') as f:
        heb_saver = csv.writer(f, delimiter='\t')
        for w in heb_cache:
            heb_saver.writerow([w] + [entry[0] + ',' + entry[1] for entry in heb_cache[w]])


def load_hebrew(csv_file):
    global heb_cache
    with open(csv_file, 'r', encoding='utf-8', newline=''):
        file_rows = csv.reader(csv_file, delimiter='\t')
        for row in file_rows:
            heb_cache[row[0]] = [tuple(entry.split(',')) for entry in row[1:]]


def save_non_hebrew(txt_file):
    global non_heb_cache
    with open(txt_file, 'a', encoding='utf-8') as f:
        f.write('\n'.join(non_heb_cache))


def load_non_hebrew(txt_file):
    global non_heb_cache
    with open(txt_file, 'r', encoding='utf-8') as f:
        txt = f.read()
        non_heb_cache = txt.split('\n')
