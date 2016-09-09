# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, os, itertools, pickle
from nltk.tokenize import TweetTokenizer
from nltk.classify import MaxentClassifier, NaiveBayesClassifier, SklearnClassifier, util
from nltk.metrics import BigramAssocMeasures as BAM
from nltk.collocations import BigramCollocationFinder as BCF
from sklearn.svm import NuSVC


""" Class in charge of classify sentences as positive or negative after being trained """
class Classifier(object):

	# Attribute that stores the trained model
	MODEL = None

	# Attribute that stores the tokenizer object
	TOKENIZER = TweetTokenizer(False, True, True)




	""" Stores every word and bigram of the specified file """
	def __getWordsAndBigrams(self, file):

		words = []
		bigrams = []

		sentences_file = open(file, 'r', encoding = "UTF8")

		# Each line is tokenize and its words and bigrams are stored in a list
		for line in sentences_file:

			# Storing all line words
			sentence_words = self.TOKENIZER.tokenize(line)
			words.append(sentence_words)

			# Storing all line bigrams
			bigram_finder = BCF.from_words(sentence_words)
			sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

			for bigram in sentence_bigrams:
				bigrams.append(bigram[0] + " " + bigram[1])

		sentences_file.close()
		return words, bigrams




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence, best_words = None, best_bigrams = None):

		# Every line word is obtained
		sentence_words = self.TOKENIZER.tokenize(sentence)

		# Every line bigram is obtained
		bigram_finder = BCF.from_words(sentence_words)
		sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

		# If the best words / bigrams lists are specified: for training
		if (best_words is not None) and (best_bigrams is not None):
			features_list = dict([(word, True) for word in sentence_words if word in best_words])
			features_list.update([(bigram[0] + " " + bigram[1], True) for bigram in sentence_bigrams
								  if (bigram[0] + " " + bigram[1]) in best_bigrams])

		# If any of them is not specified: for classifying
		else:
			features_list = dict([(word, True) for word in sentence_words])
			features_list.update([(bigram[0] + " " + bigram[1], True) for bigram in sentence_bigrams])

		return features_list




	""" Performs the training process depending on the specified classifier """
	def __performTraining(self, classifier, pos_features, neg_features):

		# Trains the Linear SVC classifier
		if classifier.lower() == "nu-svc":

			# Obtaining the feature testing set
			pos_cut = round(len(pos_features) * 3 / 4)
			neg_cut = round(len(neg_features) * 3 / 4)
			train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
			test_features = pos_features[pos_cut:] + neg_features[neg_cut:]

			self.MODEL = SklearnClassifier(NuSVC()).train(train_features)

			print("Linear SVC training process completed")
			print("Accuracy:", round(util.accuracy(self.MODEL, test_features), 4), "\n")


		# Trains the Max Entropy classifier
		elif classifier.lower() == "max-entropy":

			train_features = pos_features[:] + neg_features[:]
			self.MODEL = MaxentClassifier.train(train_features, trace = 0, min_lldelta = 0.005)

			print("Max Entropy training process completed")
			print("Accuracy:", round(util.accuracy(self.MODEL, train_features), 4), "\n")


		# Trains the Naive Bayes classifier
		elif classifier.lower() == "naive-bayes":

			# Obtaining the feature testing set
			pos_cut = round(len(pos_features) * 3 / 4)
			neg_cut = round(len(neg_features) * 3 / 4)
			train_features = pos_features[:pos_cut] + neg_features[:neg_cut]
			test_features = pos_features[pos_cut:] + neg_features[neg_cut:]

			self.MODEL = NaiveBayesClassifier.train(train_features)

			print("Naive Bayes training process completed")
			print("Accuracy:", round(util.accuracy(self.MODEL, test_features), 4), "\n")


		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier")
			exit()




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, classifier, positive_file, negative_file, num_best_words = 100, num_best_bigrams = 1000):

		# Obtain every word and bigram in both files
		pos_words, pos_bigrams = self.__getWordsAndBigrams(positive_file)
		neg_words, neg_bigrams = self.__getWordsAndBigrams(negative_file)

		# Make word lists iterable
		pos_words = list(itertools.chain(*pos_words))
		neg_words = list(itertools.chain(*neg_words))


		# Obtain best words taking into account the gain of information
		word_scores = Utilities.getScores(pos_words, neg_words)
		best_words = Utilities.getBestElements(word_scores, num_best_words)

		# Obtain best bigrams taking into account the gain of information
		bigrams_scores = Utilities.getScores(pos_bigrams, neg_bigrams)
		best_bigrams = Utilities.getBestElements(bigrams_scores, num_best_bigrams)


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


		# Trains using the specified classifier
		self.__performTraining(classifier, pos_features, neg_features)




	""" Saves a trained model into the models folder """
	def saveModel(self, model_path):

		model_file = open(model_path, 'wb')
		pickle.dump(self.MODEL, model_file)

		model_file.close()
		print("The classifier model has been saved in '", model_path, "'")




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path):

		if os.path.isfile(model_path) is True:
			model_file = open(model_path, 'rb')
			self.MODEL = pickle.load(model_file)

			model_file.close()
			print("The classifier model has been loaded from '", model_path, "'")

		else:
			print("ERROR: The specified model file does not exist")
			exit()




	""" Classify the specified text after obtaining all its words and bigrams """
	def classify(self, sentences):

		if self.MODEL is not None:
			classifications = []

			for sentence in sentences:
				features_list = self.__getFeatures(sentence)

				# If the classifier support probabilities
				try:
					result = self.MODEL.prob_classify(features_list)
					classifications.append({'Positive': result.prob('pos'), 'Negative': result.prob('neg')})

				# If the classifier does not support probabilities
				except AttributeError:
					result = self.MODEL.classify(features_list)
					classifications.append(result)

			return classifications

		else:
			print("ERROR: The classifier needs to be trained first")
			exit()
