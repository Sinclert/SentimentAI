# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import math, itertools
from nltk.tokenize import TweetTokenizer
from nltk.classify import NaiveBayesClassifier, util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder


""" Class in charge of classify sentences as positive or negative after being trained"""
class Classifier(object):


	# Attribute that stores the trained model
	MODEL = None

	# Attribute that stores the tokenizer object
	tokenizer = TweetTokenizer(False, True, True)

	# Attributes that store the best words and bigrams
	best_words = []
	best_bigrams = []


	""" Give score to every element taking into account the gain of information """
	def __createScores(self, pos_elements, neg_elements):

		# Build frequency distribution of every word and the conditional one within positive and negative labels
		freqDist = FreqDist()
		conditional_freqDist = ConditionalFreqDist()

		for element in pos_elements:
			freqDist[element] += 1
			conditional_freqDist['pos'][element] += 1

		for element in neg_elements:
			freqDist[element] += 1
			conditional_freqDist['neg'][element] += 1

		# Counts the number of positive and negative words, as well as the total number of them
		pos_count = conditional_freqDist['pos'].N()
		neg_count = conditional_freqDist['neg'].N()
		total_count = pos_count + neg_count


		scores = {}

		# Builds a dictionary of word scores based on chi-squared test
		for elem, freq in freqDist.items():
			pos_score = BigramAssocMeasures.chi_sq(conditional_freqDist['pos'][elem], (freq, pos_count), total_count)
			neg_score = BigramAssocMeasures.chi_sq(conditional_freqDist['neg'][elem], (freq, neg_count), total_count)
			scores[elem] = pos_score + neg_score

		return scores




	""" Finds the best 'n' elements based on their scores """
	def __getBestElements(self, scores, number):
		best_values = sorted(scores.items(), key = lambda element: element[1], reverse = True)[:number]
		best_elements = set([w for w, s in best_values])
		return best_elements




	""" Transform a sentence into valid list to train """
	def __createFeatures(self, sentence):

		# Every line word is obtained
		sentence_words = self.tokenizer.tokenize(sentence)

		# Every line bigram is obtained
		bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
		sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)

		# The features list is created
		features_list = dict([(word, True) for word in sentence_words if word in self.best_words])
		features_list.update([(bigram, True) for bigram in sentence_bigrams if bigram in self.best_bigrams])
		return features_list




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, positive_file, negative_file, num_best_words = 1000, num_best_bigrams = 1000):

		# These lists will store every lines word and bigram
		pos_words = []
		neg_words = []
		pos_bigrams = []
		neg_bigrams = []


		pos_sentences = open(positive_file, 'r', encoding = "UTF8")
		neg_sentences = open(negative_file, 'r', encoding = "UTF8")

		# Each line is tokenize and its words and bigrams are stored in a list
		for line in pos_sentences:

			# Storing all line words
			sentence_words = self.tokenizer.tokenize(line)
			pos_words.append(sentence_words)

			# Storing all line bigrams
			bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
			sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)
			pos_bigrams.append(sentence_bigrams)


		# Each line is tokenize and its words and bigrams are stored in a list
		for line in neg_sentences:

			# Storing all line words
			sentence_words = self.tokenizer.tokenize(line)
			neg_words.append(sentence_words)

			# Storing all line bigrams
			bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
			sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)
			neg_bigrams.append(sentence_bigrams)

		pos_sentences.close()
		neg_sentences.close()


		# Make all lists iterable
		pos_words = list(itertools.chain(*pos_words))
		neg_words = list(itertools.chain(*neg_words))
		pos_bigrams = list(itertools.chain(*pos_bigrams))
		neg_bigrams = list(itertools.chain(*neg_bigrams))

		# Obtain best words taking into account the gain of information
		word_scores = self.__createScores(pos_words, neg_words)
		self.best_words = self.__getBestElements(word_scores, num_best_words)

		# Obtain best bigrams taking into account the gain of information
		bigrams_scores = self.__createScores(pos_bigrams, neg_bigrams)
		self.best_bigrams = self.__getBestElements(bigrams_scores, num_best_bigrams)


		# These lists will store lines words with their correspondent label
		pos_features = []
		neg_features = []


		pos_sentences = open(positive_file, 'r', encoding = "UTF8")
		neg_sentences = open(negative_file, 'r', encoding = "UTF8")

		# Each line is tokenize and its words and bigrams are used to create positive features
		for line in pos_sentences:
			pos_features.append([self.__createFeatures(line), 'pos'])


		# Each line is tokenize and its words and bigrams are used to create negative features
		for line in neg_sentences:
			neg_features.append([self.__createFeatures(line), 'neg'])

		pos_sentences.close()
		neg_sentences.close()


		# Divide the features: 3/4 for training and 1/4 for testing
		pos_cut = int(math.floor(len(pos_features) * 3/4))
		neg_cut = int(math.floor(len(neg_features) * 3/4))
		train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
		test_features = pos_features[pos_cut:] + neg_features[neg_cut:]


		# Trains the Naive Bayes Classifier
		self.MODEL = NaiveBayesClassifier.train(train_features)

		print("Train on", len(train_features), "instances and test on", len(test_features), "instances")
		print("Accuracy:", util.accuracy(self.MODEL, test_features))
		self.MODEL.show_most_informative_features(10)




	""" Classify the specified text after obtaining all its words and bigrams """
	def classify(self, text):

		features_list = self.__createFeatures(text)
		percentages = self.MODEL.prob_classify(features_list)

		return {"Positive": percentages.prob('pos'), "Negative": percentages.prob('neg')}




##### TESTING #####
classifier = Classifier()
classifier.train("./Datasets/PosSentences.txt", "./Datasets/NegSentences.txt", 5000, 20000)
print(classifier.classify("This is not good"))
