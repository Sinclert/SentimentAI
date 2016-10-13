# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, itertools, pickle
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer
from nltk.classify import MaxentClassifier, NaiveBayesClassifier, SklearnClassifier, util
from nltk.metrics import BigramAssocMeasures as BAM
from nltk.collocations import BigramCollocationFinder as BCF
from sklearn.svm import NuSVC


""" Class in charge of classifying sentences with a label given a pair of them """
class Classifier(object):

	# Attribute that stores the trained model
	MODEL = None

	# Attribute that stores the tokenizer object
	TOKENIZER = TweetTokenizer(False, True, True)

	# Attribute that stores the lemmatizer object
	LEMMATIZER = SnowballStemmer('english')




	""" Stores every word and bigram of the specified file """
	def __getWordsAndBigrams(self, file):

		words = []
		bigrams = []

		try:
			sentences_file = open(file, 'r', encoding = "UTF8")

			# Each line is tokenize and its words and bigrams are stored in a list
			for line in sentences_file:

				# Storing all line words after extracting the root
				sentence_words = self.TOKENIZER.tokenize(line)
				sentence_words = [self.LEMMATIZER.stem(word) for word in sentence_words]
				words.append(sentence_words)

				# Storing all line bigrams
				bigram_finder = BCF.from_words(sentence_words)
				sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

				for bigram in sentence_bigrams:
					bigrams.append(bigram[0] + " " + bigram[1])

			sentences_file.close()
			return words, bigrams


		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The file '", file, "' cannot be opened")
			exit()




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence, best_words = None, best_bigrams = None):

		# Every line word root is obtained
		sentence_words = self.TOKENIZER.tokenize(sentence)
		sentence_words = [self.LEMMATIZER.stem(word) for word in sentence_words]

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
	def __performTraining(self, classifier_name, l1_features, l2_features):

		train_features = l1_features[:] + l2_features[:]

		# Trains the Max Entropy classifier
		if classifier_name.lower() == "max-entropy":

			self.MODEL = MaxentClassifier.train(train_features, trace = 0, min_lldelta = 0.005)

			print("Max Entropy training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", round(util.accuracy(self.MODEL, train_features), 4), "\n")


		# Trains the Naive Bayes classifier
		elif classifier_name.lower() == "naive-bayes":

			classifier = NaiveBayesClassifier
			self.MODEL = classifier.train(train_features)

			print("Naive Bayes training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", Utilities.crossValidation(classifier, l1_features, l2_features), "\n")


		# Trains the Nu SVC classifier
		elif classifier_name.lower() == "nu-svc":

			classifier = SklearnClassifier(NuSVC())
			self.MODEL = classifier.train(train_features)

			print("Nu SVC training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", Utilities.crossValidation(classifier, l1_features, l2_features), "\n")


		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier")
			exit()




	""" Train the Naive Bayes Classifier using the specified files """
	def train(self, classifier, label1_file, label2_file, num_best_words = 100, num_best_bigrams = 1000):

		# Obtaining the labels
		label1 = label1_file.rsplit('/')[-1].rsplit('.')[0]
		label2 = label2_file.rsplit('/')[-1].rsplit('.')[0]


		# Obtain every word and bigram in both files
		l1_words, l1_bigrams = self.__getWordsAndBigrams(label1_file)
		l2_words, l2_bigrams = self.__getWordsAndBigrams(label2_file)

		# Make word lists iterable
		l1_words = list(itertools.chain(*l1_words))
		l2_words = list(itertools.chain(*l2_words))


		# Obtain best words taking into account the gain of information
		word_scores = Utilities.getScores(l1_words, l2_words)
		best_words = Utilities.getBestElements(word_scores, num_best_words)

		# Obtain best bigrams taking into account the gain of information
		bigrams_scores = Utilities.getScores(l1_bigrams, l2_bigrams)
		best_bigrams = Utilities.getBestElements(bigrams_scores, num_best_bigrams)


		# These lists will store lines words with their correspondent label
		l1_features = []
		l2_features = []

		try:
			l1_sentences = open(label1_file, 'r', encoding = "UTF8")
			l2_sentences = open(label2_file, 'r', encoding = "UTF8")

			# Each line is tokenize and its words and bigrams are used to create label1 features
			for line in l1_sentences:
				l1_features.append([self.__getFeatures(line, best_words, best_bigrams), label1])

			# Each line is tokenize and its words and bigrams are used to create label2 features
			for line in l2_sentences:
				l2_features.append([self.__getFeatures(line, best_words, best_bigrams), label2])

			l1_sentences.close()
			l2_sentences.close()

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: One of the files cannot be opened")
			exit()


		# Trains using the specified classifier
		self.__performTraining(classifier, l1_features, l2_features)




	""" Classify the specified text after obtaining all its words and bigrams """
	def classify(self, sentence):

		if self.MODEL is not None:

			labels = sorted(self.MODEL.labels())
			features_list = self.__getFeatures(sentence)

			# If the classifier support probabilities
			try:
				result = self.MODEL.prob_classify(features_list)
				l1_prob = round(result.prob(labels[0]), 4)
				l2_prob = round(result.prob(labels[1]), 4)
				return {labels[0]: l1_prob, labels[1]: l2_prob}

			# If the classifier does not support probabilities
			except AttributeError:
				return self.MODEL.classify(features_list)

		else:
			print("ERROR: The classifier needs to be trained first")
			exit()




	""" Saves a trained model into the models folder """
	def saveModel(self, model_path):

		try:
			model_file = open(model_path, 'wb')
			pickle.dump(self.MODEL, model_file)

			model_file.close()
			print("The classifier model has been saved in '", model_path, "'")

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model cannot be saved into '", model_path, "'")
			exit()




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path):

		try:
			model_file = open(model_path, 'rb')
			self.MODEL = pickle.load(model_file)

			model_file.close()
			print("The classifier model has been loaded from '", model_path, "'")

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model '", model_path, "' cannot be loaded")
			exit()
