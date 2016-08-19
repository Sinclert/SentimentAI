# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re, math, itertools
from nltk.classify import NaiveBayesClassifier, util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures
from nltk.collocations import BigramCollocationFinder


""" Class in charge of classify sentences as positive or negative after being trained"""
class Classifier(object):

	# Attribute that store the trained model
	MODEL = None


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
		best_values = sorted(scores.items(), key=lambda element: element[1], reverse = True)[:number]
		best_elements = set([w for w, s in best_values])
		return best_elements



	""" Transform the lists of words and bigrams into valid lists to train """
	def __createFeatures(self, words, bigrams, best_words, best_bigrams):
		features_list = dict([(word, True) for word in words if word in best_words])
		features_list.update([(bigram, True) for bigram in bigrams if bigram in best_bigrams])
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
			sentence_words = [word.lower() for word in re.findall("[A-Za-z]+[']?[A-Za-z]+", line)]
			pos_words.append(sentence_words)

			# Storing all line bigrams
			bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
			sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)
			pos_bigrams.append(sentence_bigrams)


		# Each line is tokenize and its words and bigrams are stored in a list
		for line in neg_sentences:

			# Storing all line words
			sentence_words = [word.lower() for word in re.findall("[A-Za-z]+[']?[A-Za-z]+", line)]
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
		best_words = self.__getBestElements(word_scores, num_best_words)

		# Obtain best bigrams taking into account the gain of information
		bigrams_scores = self.__createScores(pos_bigrams, neg_bigrams)
		best_bigrams = self.__getBestElements(bigrams_scores, num_best_bigrams)


		# These lists will store lines words with their correspondent label
		pos_features = []
		neg_features = []


		pos_sentences = open(positive_file, 'r', encoding = "UTF8")
		neg_sentences = open(negative_file, 'r', encoding = "UTF8")

		# Each line is tokenize and its words are stored with the positive label in a list
		for line in pos_sentences:

			# Every line word is obtained
			sentence_words = [word.lower() for word in re.findall("[A-Za-z]+[']?[A-Za-z]+", line)]

			# Every line bigram is obtained
			bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
			sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)
			pos_features.append([self.__createFeatures(sentence_words, sentence_bigrams, best_words, best_bigrams), 'pos'])


		# Each line is tokenize and its words are stored with the negative label in a list
		for line in neg_sentences:

			# Every line word is obtained
			sentence_words = [word.lower() for word in re.findall("[A-Za-z]+[']?[A-Za-z]+", line)]

			# Every line bigram is obtained
			bigram_finder = BigramCollocationFinder.from_words(sentence_words, window_size = 3)
			sentence_bigrams = bigram_finder.nbest(BigramAssocMeasures.pmi, None)
			neg_features.append([self.__createFeatures(sentence_words, sentence_bigrams, best_words, best_bigrams), 'neg'])

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
classifier.train("./Datasets/PosSentences.txt", "./Datasets/NegSentences.txt", 5000, 20000)
