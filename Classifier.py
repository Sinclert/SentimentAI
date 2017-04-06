# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, pickle, os
from collections import Counter
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer
from nltk.classify import SklearnClassifier
from nltk.metrics import BigramAssocMeasures as BAM
from nltk.collocations import BigramCollocationFinder as BCF
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import NuSVC


""" Class in charge of the binary classification of sentences """
class Classifier(object):

	# Class attribute to access the tokenizer object
	tokenizer = TweetTokenizer(False, True, True)

	# Class attribute to access the lemmatizer object
	lemmatizer = SnowballStemmer('english')




	""" Initiates variables when the instance is created """
	def __init__(self):
		self.model = None
		self.best_words = None
		self.best_bigrams = None




	""" Obtains every sentence, word and bigram from the specified file """
	def __getWordsAndBigrams(self, file):

		sentences, words, bigrams = [], Counter(), Counter()

		try:
			sentences_file = open(file, 'r', encoding = "UTF8")

			# Each line is tokenize and its words and bigrams are stored in a list
			for line in sentences_file:

				# Storing the whole line
				sentences.append(line)

				# Storing all line words after extracting the root
				sentence_words = self.tokenizer.tokenize(line)
				sentence_words = [self.lemmatizer.stem(word) for word in sentence_words]
				for word in sentence_words:
					words[word] += 1

				# Storing all line bigrams
				bigram_finder = BCF.from_words(sentence_words)
				sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)
				for bigram in sentence_bigrams:
					bigrams[bigram[0] + " " + bigram[1]] += 1


			sentences_file.close()
			return sentences, words, bigrams


		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The file", file, "cannot be opened")
			exit()




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence):

		# Every line word root is obtained
		sentence_words = self.tokenizer.tokenize(sentence)
		sentence_words = [self.lemmatizer.stem(word) for word in sentence_words]

		# Every line bigram is obtained
		bigram_finder = BCF.from_words(sentence_words)
		sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

		# Transforming each bigram to avoid errors in other classifiers
		for i, bigram in enumerate(sentence_bigrams):
			sentence_bigrams[i] = bigram[0] + " " + bigram[1]

		try:
			features = dict((word, word in sentence_words) for word in self.best_words)
			features.update((bigram, bigram in sentence_bigrams) for bigram in self.best_bigrams)

			return features

		except TypeError:
			print("ERROR: 'None' type detected in some classifier attribute")
			exit()




	""" Performs the training process depending on the specified classifier """
	def __performTraining(self, classifier_name, l1_features, l2_features):

		classifier = None
		classifier_name = classifier_name.lower()
		train_features = l1_features[:] + l2_features[:]

		# Set the classifier depending on the provided name
		if classifier_name == "logistic-regression":
			classifier = SklearnClassifier(LogisticRegression())

		elif classifier_name == "naive-bayes":
			classifier = SklearnClassifier(BernoulliNB())

		elif classifier_name == "nu-svc":
			classifier = SklearnClassifier(NuSVC())

		elif classifier_name == "random-forest":
			classifier = SklearnClassifier(RandomForestClassifier(n_estimators = 100))

		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier")
			exit()

		# The training and the cross-validation testing are performed
		self.model = classifier.train(train_features)
		print("Training process completed")
		print("Calculating accuracy...")
		print("Accuracy:", Utilities.crossValidation(classifier, l1_features, l2_features), "\n")




	""" Trains a classifier using the sentences from the specified files """
	def train(self, classifier_name, l1_file, l2_file, words_pct = 5, bigrams_pct = 1):

		# Obtaining the labels
		label1 = l1_file.rsplit('/')[-1].rsplit('.')[0]
		label2 = l2_file.rsplit('/')[-1].rsplit('.')[0]

		# Obtaining every word and bigram in both files
		l1_sentences, l1_words, l1_bigrams = self.__getWordsAndBigrams(l1_file)
		l2_sentences, l2_words, l2_bigrams = self.__getWordsAndBigrams(l2_file)

		# Obtaining best words and bigrams considering the gain of information
		self.best_words = Utilities.getBestElements(l1_counter = l1_words,
		                                            l2_counter = l2_words,
		                                            percentage = words_pct)

		self.best_bigrams = Utilities.getBestElements(l1_counter = l1_bigrams,
		                                              l2_counter = l2_bigrams,
		                                              percentage = bigrams_pct)

		# Transforming each sentence into a dictionary of features
		for i, sentence in enumerate(l1_sentences):
			l1_sentences[i] = [self.__getFeatures(sentence), label1]

		for i, sentence in enumerate(l2_sentences):
			l2_sentences[i] = [self.__getFeatures(sentence), label2]


		# Trains using the specified classifier
		self.__performTraining(classifier_name, l1_sentences, l2_sentences)




	""" Classify the specified text after obtaining all its features """
	def classify(self, sentence):

		try:
			features = self.__getFeatures(sentence)

			# If none of the features give any information: return None
			if True not in features.values():
				return None
			else:
				return self.model.classify(features)

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

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model", model_path + model_name, "cannot be saved")
			exit()




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path, model_name):

		try:
			model_file = open(model_path + model_name + ".pickle", 'rb')
			self.model, self.best_words, self.best_bigrams = pickle.load(model_file)

			model_file.close()
			print("Classifier model loaded from", model_path + model_name)

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model", model_path + model_name, "cannot be loaded")
			exit()
