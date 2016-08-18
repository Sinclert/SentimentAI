# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re, math, itertools
from nltk.classify import NaiveBayesClassifier, util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures


""" Class in charge of classify sentences as positive or negative after being trained"""
class Classifier(object):

	# Attribute that store the trained model
	MODEL = None


	""" Give score to every word taking into account the gain of information """
	def __createScores(self, pos_words, neg_words):

		# Build frequency distribution of every word and the conditional one within positive and negative labels
		words_freqDist = FreqDist()
		conditional_freqDist = ConditionalFreqDist()

		for word in pos_words:
			words_freqDist[word.lower()] += 1
			conditional_freqDist['pos'][word.lower()] += 1

		for word in neg_words:
			words_freqDist[word.lower()] += 1
			conditional_freqDist['neg'][word.lower()] += 1

		# Counts the number of positive and negative words, as well as the total number of them
		pos_word_count = conditional_freqDist['pos'].N()
		neg_word_count = conditional_freqDist['neg'].N()
		total_word_count = pos_word_count + neg_word_count


		word_scores = {}

		# Builds a dictionary of word scores based on chi-squared test
		for word, freq in words_freqDist.items():
			pos_score = BigramAssocMeasures.chi_sq(conditional_freqDist['pos'][word], (freq, pos_word_count), total_word_count)
			neg_score = BigramAssocMeasures.chi_sq(conditional_freqDist['neg'][word], (freq, neg_word_count), total_word_count)
			word_scores[word] = pos_score + neg_score

		return word_scores




	""" Finds the best 'n' words based on word scores """
	def __getBestWords(self, word_scores, number):
		best_values = sorted(word_scores.items(), key=lambda word_score: word_score[1], reverse = True)[:number]
		best_words = set([w for w, s in best_values])
		return best_words




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, positive_file, negative_file, num_best_words = 1000):

		# These lists will store lines words in order to built the frequency distributions
		pos_words = []
		neg_words = []

		pos_sentences = open(positive_file, 'r')
		neg_sentences = open(negative_file, 'r')

		# Each line is tokenize and its words are stored in a list
		for line in pos_sentences:
			sentence_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			pos_words.append(sentence_words)

		# Each line is tokenize and its words are stored in a list
		for line in neg_sentences:
			sentence_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			neg_words.append(sentence_words)

		pos_sentences.close()
		neg_sentences.close()


		# Make both words lists iterable
		pos_words = list(itertools.chain(*pos_words))
		neg_words = list(itertools.chain(*neg_words))

		# Word scores are obtained taking into account the gain of information
		word_scores = self.__createScores(pos_words, neg_words)
		best_words = self.__getBestWords(word_scores, num_best_words)


		# These lists will store lines words with their correspondent label
		pos_features = []
		neg_features = []

		pos_sentences = open(positive_file, 'r')
		neg_sentences = open(negative_file, 'r')

		# Each line is tokenize and its words are stored with the positive label in a list
		for line in pos_sentences:
			sentence_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			sentence_words = (dict([(word, True) for word in sentence_words if word in best_words]), 'pos')
			pos_features.append(sentence_words)

		# Each line is tokenize and its words are stored with the negative label in a list
		for line in neg_sentences:
			sentence_words = re.findall("[A-Za-z]+[']?[A-Za-z]+", line)
			sentence_words = (dict([(word, True) for word in sentence_words if word in best_words]), 'neg')
			neg_features.append(sentence_words)

		pos_sentences.close()
		neg_sentences.close()


		# Divide the features: 3/4 for training and 1/4 for testing
		pos_cut = int(math.floor(len(pos_features) * 3/4))
		neg_cut = int(math.floor(len(neg_features) * 3/4))
		train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
		test_features = pos_features[pos_cut:] + neg_features[neg_cut:]


		# Trains the Naive Bayes Classifier
		self.MODEL = NaiveBayesClassifier.train(train_features)

		print ("Train on", len(train_features), "instances and test on", len(test_features), "instances")
		print ("Accuracy:", util.accuracy(self.MODEL, test_features))
		self.MODEL.show_most_informative_features(10)




##### TESTING #####
classifier = Classifier()
classifier.train("./Datasets/PosSentences.txt", "./Datasets/NegSentences.txt", 5000)
