# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import os, math, itertools, collections, pickle
from nltk.tokenize import TweetTokenizer
from nltk.classify import NaiveBayesClassifier, util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures as BAM, precision, recall
from nltk.collocations import BigramCollocationFinder as BCF


""" Class in charge of classify sentences as positive or negative after being trained"""
class Classifier(object):


	# Attribute that stores the trained model
	MODEL = None

	# Attribute that stores the tokenizer object
	tokenizer = TweetTokenizer(False, True, True)


	""" Give score to every element taking into account the gain of information """
	def __getScores(self, pos_elements, neg_elements):

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
			pos_score = BAM.chi_sq(conditional_freqDist['pos'][elem], (freq, pos_count), total_count)
			neg_score = BAM.chi_sq(conditional_freqDist['neg'][elem], (freq, neg_count), total_count)
			scores[elem] = pos_score + neg_score

		return scores




	""" Finds the best 'n' elements based on their scores """
	def __getBestElements(self, scores, number):
		best_values = sorted(scores.items(), key = lambda element: element[1], reverse = True)[:number]
		best_elements = set([w for w, s in best_values])
		return best_elements




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence, best_words = None, best_bigrams = None):

		# Every line word is obtained
		sentence_words = self.tokenizer.tokenize(sentence)

		# Every line bigram is obtained
		bigram_finder = BCF.from_words(sentence_words)
		sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

		# If the best words / bigrams lists are specified: for training
		if (best_words is not None) and (best_bigrams is not None):
			features_list = dict([(word, True) for word in sentence_words if word in best_words])
			features_list.update([(bigram, True) for bigram in sentence_bigrams if bigram in best_bigrams])

		# If any of them is not specified: for classifying
		else:
			features_list = dict([(word, True) for word in sentence_words])
			features_list.update([(bigram, True) for bigram in sentence_bigrams])

		return features_list




	""" Compares the test features with their labels in order to obtain the recall and the precision """
	def __getStatisticSets(self, test_features):

		if self.MODEL is None:
			print("ERROR: The training model has not been initialized")
			exit()

		ref_set = collections.defaultdict(set)
		test_set = collections.defaultdict(set)

		# For each feature: we compare the classifier result with the correct label
		for i, (feat, label) in enumerate(test_features):
			ref_set[label].add(i)
			observed = self.MODEL.classify(feat)
			test_set[observed].add(i)

		return ref_set, test_set




	""" Shows information about the training process if it is specified """
	def __showInformation(self, pos_features, neg_features, debug):

		train_features = None
		test_features = None

		# If debug mode: 3/4 features for training and 1/4 features for testing
		if debug is True:
			pos_cut = int(math.floor(len(pos_features) * 3/4))
			neg_cut = int(math.floor(len(neg_features) * 3/4))
			train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
			test_features = pos_features[pos_cut:] + neg_features[neg_cut:]

		# If no debug mode: every feature is for training
		elif debug is False:
			train_features = pos_features[:] + neg_features[:]

		else:
			print("ERROR: Invalid 'debug' argument value")
			exit()


		# Trains the Naive Bayes Classifier
		self.MODEL = NaiveBayesClassifier.train(train_features)


		if debug is True:
			print("Trained on", len(train_features), "instances and tested on", len(test_features), "instances\n")

			# Obtaining recall and precision necessary sets
			ref_set, test_set = self.__getStatisticSets(test_features)

			print("Accuracy:", round(util.accuracy(self.MODEL, test_features), 4))
			print("'Pos' false positives:", round(1 - precision(ref_set['pos'], test_set['pos']), 4))
			print("'Pos' false negatives:", round(1 - recall(ref_set['pos'], test_set['pos']), 4))
			print("'Neg' false positive:", round(1 - precision(ref_set['neg'], test_set['neg']), 4))
			print("'Neg' false negative:", round(1 - recall(ref_set['neg'], test_set['neg']), 4))
			print()

			self.MODEL.show_most_informative_features(10)
			print()

		elif debug is False:
			print("Trained on", len(train_features), "instances")




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, positive_file, negative_file, num_best_words = 1000, num_best_bigrams = 1000, debug = False):

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
			bigram_finder = BCF.from_words(sentence_words)
			sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)
			pos_bigrams.append(sentence_bigrams)


		# Each line is tokenize and its words and bigrams are stored in a list
		for line in neg_sentences:

			# Storing all line words
			sentence_words = self.tokenizer.tokenize(line)
			neg_words.append(sentence_words)

			# Storing all line bigrams
			bigram_finder = BCF.from_words(sentence_words)
			sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)
			neg_bigrams.append(sentence_bigrams)

		pos_sentences.close()
		neg_sentences.close()


		# Make all lists iterable
		pos_words = list(itertools.chain(*pos_words))
		neg_words = list(itertools.chain(*neg_words))
		pos_bigrams = list(itertools.chain(*pos_bigrams))
		neg_bigrams = list(itertools.chain(*neg_bigrams))

		# Obtain best words taking into account the gain of information
		word_scores = self.__getScores(pos_words, neg_words)
		best_words = self.__getBestElements(word_scores, num_best_words)

		# Obtain best bigrams taking into account the gain of information
		bigrams_scores = self.__getScores(pos_bigrams, neg_bigrams)
		best_bigrams = self.__getBestElements(bigrams_scores, num_best_bigrams)


		# These lists will store lines words with their correspondent label
		pos_features = []
		neg_features = []


		pos_sentences = open(positive_file, 'r', encoding = "UTF8")
		neg_sentences = open(negative_file, 'r', encoding = "UTF8")

		# Each line is tokenize and its words and bigrams are used to create positive features
		for line in pos_sentences:
			pos_features.append([self.__getFeatures(line, best_words, best_bigrams), 'pos'])


		# Each line is tokenize and its words and bigrams are used to create negative features
		for line in neg_sentences:
			neg_features.append([self.__getFeatures(line, best_words, best_bigrams), 'neg'])

		pos_sentences.close()
		neg_sentences.close()

		# Depending on the "debug" value, additional information is shown or not
		self.__showInformation(pos_features, neg_features, debug)




	""" Saves a trained model into the models folder """
	def saveModel(self, model_path):

		model_file = open(model_path, 'wb')
		pickle.dump(self.MODEL, model_file)

		print("The classifier model has been saved in '", model_path, "'")
		model_file.close()




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path):

		if os.path.isfile(model_path) is True:
			model_file = open(model_path, 'rb')
			self.MODEL = pickle.load(model_file)

			print("The classifier model has been loaded from '", model_path, "'")
			model_file.close()

		else:
			print("ERROR: The specified model file does not exist")
			exit()




	""" Classify the specified text after obtaining all its words and bigrams """
	def classify(self, sentences):

		if self.MODEL is not None:
			probabilities = []

			for sentence in sentences:
				features_list = self.__getFeatures(sentence)
				percentages = self.MODEL.prob_classify(features_list)
				probabilities.append({"Positive": percentages.prob('pos'), "Negative": percentages.prob('neg')})

			return probabilities

		else:
			print("ERROR: The classifier needs to be trained first")
			exit()
