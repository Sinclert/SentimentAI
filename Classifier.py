# Created by Sinclert Perez (Sinclert@hotmail.com)

import pickle, os, itertools, numpy
from Utilities import getStopWords, getBestElements
from collections import Counter
from nltk import bigrams as getBigrams
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier as RandomForest
from sklearn.preprocessing import LabelEncoder
from sklearn.base import clone
from sklearn.model_selection import cross_val_score


possible_classifiers = {
	"logistic-regression": LogisticRegression(n_jobs = -1),
	"naive-bayes": BernoulliNB(),
	"linear-svc": LinearSVC(),
	"random-forest": RandomForest(n_estimators = 100, n_jobs = -1)
}




""" Class in charge of the binary classification of sentences """
class Classifier(object):


	# Class attribute to access the tokenizer object
	tokenizer = TweetTokenizer(False, True, True)

	# Class attribute to compress feature dictionaries
	vectorizer = DictVectorizer()




	""" Initiates variables when the instance is created """
	def __init__(self, language = "english"):

		self.lemmatizer = SnowballStemmer(language)
		self.stopwords = getStopWords(language)

		self.model = None
		self.best_words = None
		self.best_bigrams = None




	""" Obtains the processed tokens of the specified sentence """
	def __getWords(self, sentence):

		sentence_words = self.tokenizer.tokenize(sentence)
		sentence_words = filter(lambda w: w not in self.stopwords, sentence_words)
		sentence_words = [self.lemmatizer.stem(word) for word in sentence_words]

		return sentence_words




	""" Obtains every sentence, word and bigram from the specified file """
	def __getWordsAndBigrams(self, file):

		sentences, words, bigrams = [], Counter(), Counter()

		try:
			sentences_file = open(file, 'r', encoding = "UTF8")

			# Each line is tokenize and its words and bigrams stored
			for line in sentences_file:

				# Storing the whole line
				sentences.append(line)

				# Storing all line words
				sentence_words = self.__getWords(line)
				for word in sentence_words:
					words[word] += 1

				# Storing all line bigrams
				sentence_bigrams = getBigrams(sentence_words)
				for bigram in sentence_bigrams:
					bigrams[" ".join(bigram)] += 1


			sentences_file.close()
			return sentences, words, bigrams


		except (FileNotFoundError, PermissionError, IsADirectoryError):
			print("ERROR: The file", file, "cannot be opened")
			exit()




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence):

		# Every line word is obtained
		sentence_words = self.__getWords(sentence)

		# Every bigram is obtained and transformed (avoiding errors)
		sentence_bigrams = getBigrams(sentence_words)
		sentence_bigrams = [" ".join(b) for b in sentence_bigrams]

		try:
			features = dict((word, word in sentence_words) for word in self.best_words)
			features.update((bigram, bigram in sentence_bigrams) for bigram in self.best_bigrams)

			return features

		except TypeError:
			print("ERROR: 'None' type detected in some classifier attribute")
			exit()




	""" Performs the training and testing processes """
	def __performTraining(self, classifier_name, features, labels):

		try:
			# Generating the model that is going to be stored
			classifier = possible_classifiers[classifier_name]
			self.model = classifier.fit(features, labels)
			print("Training process completed")

			# The labels are encoded to perform F1 scoring
			labels = LabelEncoder().fit_transform(labels)
			bin_classifier = clone(possible_classifiers[classifier_name])
			bin_classifier.fit(features, labels)

			# The model is tested using cross validation
			results = cross_val_score(estimator = bin_classifier,
			                          X = features,
			                          y = labels,
			                          scoring = 'f1',
			                          cv = 10)

			print("F1 score:", round(sum(results) / len(results), 4), "\n")

		except KeyError:
			print("ERROR: Invalid classifier")
			exit()




	""" Trains a classifier using the sentences from the specified files """
	def train(self, classifier_name, l1_file, l2_file, words_pct = 5, bigrams_pct = 1):

		# Obtaining the label names
		label1 = l1_file.rsplit('/')[-1].rsplit('.')[0]
		label2 = l2_file.rsplit('/')[-1].rsplit('.')[0]

		# Obtaining every word and bigram in both files
		l1_sentences, l1_words, l1_bigrams = self.__getWordsAndBigrams(l1_file)
		l2_sentences, l2_words, l2_bigrams = self.__getWordsAndBigrams(l2_file)

		# Obtaining best words and bigrams considering the gain of information
		self.best_words = getBestElements(l1_counter = l1_words,
		                                  l2_counter = l2_words,
		                                  percentage = words_pct)

		self.best_bigrams = getBestElements(l1_counter = l1_bigrams,
		                                    l2_counter = l2_bigrams,
		                                    percentage = bigrams_pct)

		# Getting the labels as a numpy array
		labels = numpy.array(([label1] * len(l1_sentences)) + ([label2] * len(l2_sentences)))

		# Transforming each sentence into a dictionary of vectorized features
		features = itertools.chain(map(self.__getFeatures, l1_sentences),
		                           map(self.__getFeatures, l2_sentences))

		features = self.vectorizer.fit_transform(features)

		# Trains using the specified classifier
		self.__performTraining(classifier_name, features, labels)




	""" Classify the specified text after obtaining all its features """
	def classify(self, sentence):

		try:
			features = self.__getFeatures(sentence)
			features = self.vectorizer.fit_transform(features)

			# If none of the features give any information: return None
			if features.getnnz() == 0:
				return None
			else:
				return self.model.predict(features)[0]

		except AttributeError:
			print("ERROR: The classifier needs to be trained first")
			exit()




	""" Saves a trained model into the models folder """
	def saveModel(self, model_path, model_name):

		try:
			# If the folder does not exist: it is created
			if os.path.exists(model_path) is False:
				os.mkdir(model_path)

			model_file = open(model_path + model_name + ".pickle", 'wb')
			pickle.dump([self.model, self.best_words, self.best_bigrams], model_file)

			model_file.close()
			print("Classifier model saved in", model_path + model_name)

		except (FileNotFoundError, PermissionError, IsADirectoryError):
			print("ERROR: The model", model_path + model_name, "cannot be saved")
			exit()




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path, model_name):

		try:
			model_file = open(model_path + model_name + ".pickle", 'rb')
			self.model, self.best_words, self.best_bigrams = pickle.load(model_file)

			model_file.close()
			print("Classifier model loaded from", model_path + model_name)

		except (FileNotFoundError, PermissionError, IsADirectoryError):
			print("ERROR: The model", model_path + model_name, "cannot be loaded")
			exit()
