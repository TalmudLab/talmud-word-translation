import joblib
from src.languagetagger.utils import *

model_path = './src/languagetagger/GemaraLanguageTagger.joblib'
lang_clf = joblib.load(model_path)


def tag_gemara_chunk(words_for_tagging):
    cleaned_words = [clean(word) for word in words_for_tagging]
    word_vectors = [tok_to_vec(word) for word in cleaned_words]
    predictions = lang_clf.predict_proba(word_vectors)
    print(predictions)
    #       prob[1] = probability of being Hebrew = 1 - P(Aramaic)
    return [prob[1] for prob in predictions]
