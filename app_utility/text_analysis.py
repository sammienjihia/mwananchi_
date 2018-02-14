import string

from django.utils.html import format_html
from collections import Counter
from nltk.corpus import stopwords



def word_count(list_of_texts, most_common = 10):
    most_common = int(most_common)
    punctuation = list(string.punctuation)
    stop = stopwords.words('english') + punctuation + ['rt', 'via']
    most_frequent_words = {}
    count_all = Counter()

    for texts in list_of_texts:
        terms_only = [term for term in texts.lower().split()
                      if term not in stop
                      and not term.startswith(('#', '@', 'http', '&amp;'))]
        count_all.update(terms_only)
        most_frequent_words = count_all.most_common(most_common)
    word_count_list = []
    for count_list in most_frequent_words:
        word_count_list.append({
            'word': format_html("{}",count_list[0]),
            'count': count_list[1]
        })

    return word_count_list



