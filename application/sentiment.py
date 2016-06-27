import string, nltk
from stopwords import *

def findSentiment(classifier, review):
	words = preProcess(review)
	sentiment = classifier.classify(word_feats(words))
	return sentiment

def word_feats(words):
	return dict([(word, True) for word in words])

def preProcess(review):
	#remove punctuation
	review = review.encode('utf-8').translate(None, string.punctuation)
	review = review.decode('utf-8')
	#translate to lower case
	words = review.lower().split()
	#remove stop words
	content = [w for w in words if w not in stopwords]
	#stem the words
	stemmer = nltk.stem.porter.PorterStemmer()
	stems = [stemmer.stem(w) for w in content]
	return stems
