# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import os, math, itertools, pickle
from nltk.tokenize import TweetTokenizer
from nltk.classify import MaxentClassifier, NaiveBayesClassifier, util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures as BAM
from nltk.collocations import BigramCollocationFinder as BCF


""" Class in charge of classify sentences as positive or negative after being trained """
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




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, classifier, positive_file, negative_file, num_best_words = 1000, num_best_bigrams = 1000):

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


		# Trains the Max Entropy Classifier
		if classifier.lower() == "max-entropy":

			train_features = pos_features[:] + neg_features[:]
			self.MODEL = MaxentClassifier.train(train_features, trace = 0, min_lldelta = 0.005)

			print("Training instances:", len(train_features), ". Testing instances:", len(train_features))
			print("Accuracy:", round(util.accuracy(self.MODEL, train_features), 4), "\n")


		# Trains the Naive Bayes Classifier
		elif classifier.lower() == "naive-bayes":

			# Obtaining the feature testing set
			pos_cut = int(math.floor(len(pos_features) * 3/4))
			neg_cut = int(math.floor(len(neg_features) * 3/4))
			train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
			test_features = pos_features[pos_cut:] + neg_features[neg_cut:]

			self.MODEL = NaiveBayesClassifier.train(train_features)

			print("Training instances:", len(train_features), ". Testing instances:", len(test_features))
			print("Accuracy:", round(util.accuracy(self.MODEL, test_features), 4), "\n")


		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier. Possible options: 'max-entropy' / 'naive-bayes'")
			exit()




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
