import celery
from gensim import similarities, corpora, models
import pandas as pd
import lxml.html
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import PorterStemmer

from worker import app


class SkillsTask(celery.Task):
    """Base class for skills prediction task"""
    abstract=True

    def __init__(self):
        super().__init__()
        nltk.download('punkt')
        nltk.download('stopwords')
        self.index = similarities.MatrixSimilarity.load('./data/trans_skills.index')
        df = pd.read_csv('./data/trans_skills.csv')
        self.labels = df['label']
        self.tokenizer = TweetTokenizer()
        self.stemmer = PorterStemmer()
        self.stoplist = stopwords.words('english')
        self.dictionary = corpora.Dictionary.load('./data/dictionary')
        self.lsi = models.LsiModel.load('./data/lsi')



@app.task(
    bind=True,
    ignore_result=False,
    base=SkillsTask,
    name='lsi_skills')
def predict(self, data):
    """Predicts the labels of the text data"""
    html = data.get('html', None)
    if html is not None:
        root = lxml.html.fromstring(html)
        html_text = ' '.join(root.xpath('//*/text()'))
        html_text = re.sub('\\s+', ' ', html_text)
    else:
        html_text = ''
    plain = data.get('plain', None)
    plain_text = plain if plain is not None else ''
    doc = html_text + plain_text
    doc_bow = self.dictionary.doc2bow([self.stemmer.stem(word) 
                                  for word in self.tokenizer.tokenize(doc.lower()) 
                                  if word not in self.stoplist])
    doc_lsi = self.lsi[doc_bow]
    sims = self.index[doc_lsi]
    return [self.labels.iloc[p[0]] 
            for p in sorted(list(enumerate(sims)), key=lambda i: i[1], reverse=True)
            if p[1]>0.55]

