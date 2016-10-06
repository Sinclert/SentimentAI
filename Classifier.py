# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, math, itertools, pickle
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer
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
	def __performTraining(self, classifier_name, pos_features, neg_features):

		train_features = pos_features[:] + neg_features[:]

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
			print("Accuracy:", self.__crossValidation(classifier, pos_features, neg_features), "\n")


		# Trains the Nu SVC classifier
		elif classifier_name.lower() == "nu-svc":

			classifier = SklearnClassifier(NuSVC())
			self.MODEL = classifier.train(train_features)

			print("Nu SVC training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", self.__crossValidation(classifier, pos_features, neg_features), "\n")


		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier")
			exit()




	""" Test the specified classifier applying cross validation """
	@staticmethod
	def __crossValidation(classifier, pos_features, neg_features, folds = 10):

		if folds > 1:

			# Calculating cut offs in both features lists
			pos_cutoff = math.floor(len(pos_features) / folds)
			neg_cutoff = math.floor(len(neg_features) / folds)

			mean_accuracy = 0

			# Calculating each fold accuracy
			for i in range(folds):
				test_features = pos_features[((folds - i - 1) * pos_cutoff):((folds - i) * pos_cutoff)] + \
								neg_features[((folds - i - 1) * neg_cutoff):((folds - i) * neg_cutoff)]

				train_features = [feature for feature in (pos_features + neg_features) if feature not in test_features]

				model = classifier.train(train_features)
				mean_accuracy += util.accuracy(model, test_features)

			return round((mean_accuracy / folds), 4)

		else:
			print("ERROR: The number of cross validation folds must be greater than 1")
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

		try:
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

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: One of the files cannot be opened")
			exit()


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

		try:
			model_file = open(model_path, 'rb')
			self.MODEL = pickle.load(model_file)

			model_file.close()
			print("The classifier model has been loaded from '", model_path, "'")

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model '", model_path, "' cannot be loaded")
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
					pos_prob = round(result.prob('pos'), 4)
					neg_prob = round(result.prob('neg'), 4)
					classifications.append({'Positive': pos_prob, 'Negative': neg_prob})

				# If the classifier does not support probabilities
				except AttributeError:
					result = self.MODEL.classify(features_list)
					classifications.append(result)

			return classifications

		else:
			print("ERROR: The classifier needs to be trained first")
			exit()
