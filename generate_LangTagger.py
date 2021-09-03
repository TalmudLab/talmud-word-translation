from sklearn import svm
import json
import joblib
from src.languagetagger.utils import *


train_data_path = './data/vowelized_cal_texts/71667_each_training_data.json'
out_path = './src/languagetagger/'

# Python unfortunately can't handle all 140,000+ pieces of data :(
sample_size = 20000

if __name__ == '__main__':
    with open(train_data_path, encoding='utf-8') as f:
        data = json.load(f)
    print('Data loaded...')

    # data[:sample_size] + data[-sample_size:] = the same number of Hebrew and Aramaic words
    train_labels = [d['tag'] for d in data[:sample_size] + data[-sample_size:]]
    train_words = [clean(d['word']) for d in data[:sample_size] + data[-sample_size:]]
    print('Data separated and cleaned...')

    dimension = max([len(word) for word in train_words]) * len(characters)
    print(dimension)
    train_vecs = [tok_to_vec(word, dimension) for word in train_words]
    print('Vectors generated...')

    lang_clf = svm.SVC(probability=True)
    lang_clf.fit(train_vecs, train_labels)
    print('Model completed...')

    with open(out_path + 'GemaraLanguageTagger.joblib', 'wb') as f:
        joblib.dump(lang_clf, f)
    print('Done!')
