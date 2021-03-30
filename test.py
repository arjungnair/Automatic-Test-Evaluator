import string
import nltk
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob, Word, Blobber

def remove_punctuation(text):
    text = "".join([c for c in text if c not in string.punctuation])
    return text

def tokenize(text):
    text = word_tokenize(text)
    return text

def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words
def word_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    t = [lemmatizer.lemmatize(i) for i in text]
    return t
def word_stemmer(text):
    stemmer = PorterStemmer()
    t = [stemmer.stem(i) for i in text]
    return t

def sentence_polarity(text1, text2):
    text1 = TextBlob(text1)
    text2 = TextBlob(text2)
    print(text1.sentiment)
    print(text2.sentiment)
    polarity = abs(text1.sentiment.polarity - text2.sentiment.polarity)
    return polarity

def matched_keywords(text1,text2):
    text1 = preprocess(text1)
    text2 = preprocess(text2)
    print(text1)
    print(text2)
    n = 0
    for w1 in text1:
        for w2 in text2:
            if w1 == w2:
                n = n + 1
    match = n/len(text1) #assume text1 is reference answer
    return match

def preprocess(text):
    text = remove_punctuation(text)
    text = tokenize(text)
    text = remove_stopwords(text)
    text = word_lemmatizer(text)
    text = word_stemmer(text)
    return text

#print(preprocess("He was studying for the exam very rigourously, but he still couldn't pass the exam"))
print(matched_keywords("i hate the exam", "i did not like the exam"))
""" referenceAnswer = "Smog is a mixture of smoke and fog"
qwlist = ['Smog','eggs']
for w in qwlist:
    referenceAnswer = referenceAnswer.replace(w,'')
print(referenceAnswer) """