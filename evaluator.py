#from dandelion import DataTXT 
#import spacy
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob, Word, Blobber
import string

def remove_punctuation(text):
    text = "".join([c for c in text if c not in string.punctuation])
    return text

#convert sentence into list of words
def tokenize(text):
    text = word_tokenize(text)
    return text

#remove irrelevant words like is, the, etc
def remove_stopwords(text):
    sw = stopwords.words('english')
    words = [w for w in text if w not in sw]
    return words

#Converts words to its root or base form meaningfully, eg: running to run
def word_lemmatizer(text):
    lemmatizer = WordNetLemmatizer()
    t = [lemmatizer.lemmatize(i) for i in text]
    return t
#Cuts of prefixes and suffixes to reach the root word
def word_stemmer(text):
    stemmer = PorterStemmer()
    t = [stemmer.stem(i) for i in text]
    return t

#Used to detect the sentiment of two texts and compare them to detect contradictions
def sentence_polarity(text1, text2):
    t1 = TextBlob(text1)
    t2 = TextBlob(text2)
    polarity = abs(t1.sentiment.polarity - t2.sentiment.polarity)
    return polarity
#Preprocessing text by applying above functions
def preprocess(text):
    text = TextBlob(text).correct()#Correcting spelling errors
    text = remove_punctuation(text)
    text = tokenize(text)
    text = remove_stopwords(text)
    text = word_lemmatizer(text)
    text = word_stemmer(text)
    return text

#divides the number of matching keywords in student answer and reference answer divided
#by the no of keywords in the reference
def matched_keywords(text1,text2):
    n = 0
    for w1 in text1:
        for w2 in text2:
            if w1 == w2:
                n = n + 1
    match = n/len(text1) #assume text1 is reference answer
    return match


#Converts list of words in text to vectors and calculates cosine between vectors
def cosine_sim(X,Y): 
    X_set = {w for w in X}
    Y_set = {w for w in Y}
    l1 = []
    l2 = []
    # form a set containing keywords of both strings  
    rvector = X_set.union(Y_set)  
    for w in rvector: 
        if w in X_set: l1.append(1) # create a vector 
        else: l1.append(0) 
        if w in Y_set: l2.append(1) 
        else: l2.append(0) 
    c = 0
    
    # cosine formula  
    for i in range(len(rvector)): 
            c+= l1[i]*l2[i] 
    cosine = c / float((sum(l1)*sum(l2))**0.5)
    return(cosine) 

def evaluate(qapair):
    question = qapair[1]
    studentAnswer = qapair[0]
    referenceAnswer = qapair[2]
    #Evaluating sentence polarities
    polarity = sentence_polarity(referenceAnswer,studentAnswer)
    #Removing words from answer that are in question
    qwlist = list(question.split(" "))
    for w in qwlist:
        referenceAnswer = referenceAnswer.replace(w,'')
        studentAnswer = studentAnswer.replace(w,'')

    X = preprocess(referenceAnswer)  
    Y = preprocess(studentAnswer)
    match = 1
    #match = 1 - matched_keywords(X,Y)
    if match == 0:
        cosine = 0
    else:
        cosine = cosine_sim(X,Y)
    
    cosine = cosine - cosine*polarity*match
    return(cosine)


