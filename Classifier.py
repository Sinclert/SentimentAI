# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re, codecs, math
from nltk.classify import NaiveBayesClassifier, util


""" Class in charge of classify sentences as positive or negative after being trained"""
class Classifier(object):

	# Attribute that store the trained model
	MODEL = None


	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, positive_file, negative_file):

		pos_features = []
		neg_features = []

		pos_sentences = codecs.open(positive_file, 'r', encoding = "latin-1")
		neg_sentences = codecs.open(negative_file, 'r', encoding = "latin-1")

		# Each line is tokenize and stored with the positive label in a list
		for line in pos_sentences:
			pos_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			pos_words = [dict([(word, True) for word in pos_words]), 'pos']
			pos_features.append(pos_words)

		# Each line is tokenize and stored with the negative label in a list
		for line in neg_sentences:
			neg_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			neg_words = [dict([(word, True) for word in neg_words]), 'neg']
			neg_features.append(neg_words)


		pos_sentences.close()
		neg_sentences.close()

		# Divide the features: 3/4 for training and 1/4 for testing
		pos_cut = int(math.floor(len(pos_features) * 3/4))
		neg_cut = int(math.floor(len(neg_features) * 3/4))
		train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
		test_features = pos_features[pos_cut:] + neg_features[neg_cut:]


		# Trains the Naive Bayes Classifier
		self.MODEL = NaiveBayesClassifier.train(train_features)


		print ("Train on", len(train_features), "instances and test on", len(test_features))
		print ("Accuracy:", util.accuracy(self.MODEL, test_features))
		self.MODEL.show_most_informative_features(10)



# Testing:
classifier = Classifier()
classifier.train("./Datasets/PosSentences.txt", "./Datasets/NegSentences.txt")
