# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, pickle, os
from nltk.tokenize import TweetTokenizer
from nltk.stem import SnowballStemmer
from nltk.classify import SklearnClassifier
from nltk.metrics import BigramAssocMeasures as BAM
from nltk.collocations import BigramCollocationFinder as BCF
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import NuSVC


""" Class in charge of classifying sentences with a label given a pair of them """
class Classifier(object):

	# Attributes that stores the trained model, best words and bigrams
	MODEL = None
	BEST_WORDS = None
	BEST_BIGRAMS = None

	# Attribute that stores the tokenizer object
	TOKENIZER = TweetTokenizer(False, True, True)

	# Attribute that stores the lemmatizer object
	LEMMATIZER = SnowballStemmer('english')




	""" Obtains every sentence with its words and bigrams of the specified file """
	def __getWordsAndBigrams(self, file):

		sentences = []
		words = []
		bigrams = []

		try:
			sentences_file = open(file, 'r', encoding = "UTF8")

			# Each line is tokenize and its words and bigrams are stored in a list
			for line in sentences_file:

				# Storing the whole line
				sentences.append(line)

				# Storing all line words after extracting the root
				sentence_words = self.TOKENIZER.tokenize(line)
				sentence_words = [self.LEMMATIZER.stem(word) for word in sentence_words]

				for word in sentence_words:
					words.append(word)

				# Storing all line bigrams
				bigram_finder = BCF.from_words(sentence_words)
				sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

				for bigram in sentence_bigrams:
					bigrams.append(bigram[0] + " " + bigram[1])

			sentences_file.close()
			return sentences, words, bigrams


		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The file '", file, "' cannot be opened")
			exit()




	""" Transform a sentence into a features list to train / classify """
	def __getFeatures(self, sentence):

		# Every line word root is obtained
		sentence_words = self.TOKENIZER.tokenize(sentence)
		sentence_words = [self.LEMMATIZER.stem(word) for word in sentence_words]

		# Every line bigram is obtained
		bigram_finder = BCF.from_words(sentence_words)
		sentence_bigrams = bigram_finder.nbest(BAM.pmi, None)

		# Transforming each bigram to avoid errors in other classifiers
		for i in range(0, len(sentence_bigrams)):
			sentence_bigrams[i] = sentence_bigrams[i][0] + " " + sentence_bigrams[i][1]


		try:
			features_list = dict([(word, word in sentence_words) for word in self.BEST_WORDS])
			features_list.update([(bigram, bigram in sentence_bigrams) for bigram in self.BEST_BIGRAMS])

			return features_list

		except TypeError:
			print("ERROR: 'None' type detected in some classifier attribute")
			exit()




	""" Performs the training process depending on the specified classifier """
	def __performTraining(self, classifier_name, l1_features, l2_features):

		train_features = l1_features[:] + l2_features[:]

		# Trains the Logistic Regression classifier
		if classifier_name.lower() == "logistic-regression":

			classifier = SklearnClassifier(LogisticRegression())
			self.MODEL = classifier.train(train_features)

			print("Logistic Regression training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", Utilities.crossValidation(classifier, l1_features, l2_features), "\n")


		# Trains the Naive Bayes classifier
		elif classifier_name.lower() == "naive-bayes":

			classifier = SklearnClassifier(BernoulliNB())
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


		# Trains the Random Forest classifier
		elif classifier_name.lower() == "random-forest":

			classifier = SklearnClassifier(RandomForestClassifier(n_estimators = 100))
			self.MODEL = classifier.train(train_features)

			print("Random Forest training process completed")
			print("Calculating accuracy...")
			print("Accuracy:", Utilities.crossValidation(classifier, l1_features, l2_features), "\n")


		# In case another option is specified: error
		else:
			print("ERROR: Invalid classifier")
			exit()




	""" Trains a classifier using the sentences from the specified files """
	def train(self, classifier, label1_file, label2_file, words_proportion = 20, bigrams_proportion = 100):

		# Obtaining the labels
		label1 = label1_file.rsplit('/')[-1].rsplit('.')[0]
		label2 = label2_file.rsplit('/')[-1].rsplit('.')[0]

		# Obtaining every word and bigram in both files
		l1_sentences, l1_words, l1_bigrams = self.__getWordsAndBigrams(label1_file)
		l2_sentences, l2_words, l2_bigrams = self.__getWordsAndBigrams(label2_file)

		# Obtaining best words and bigrams taking into account their gain of information
		self.BEST_WORDS = Utilities.getBestElements(l1_words, l2_words, words_proportion)
		self.BEST_BIGRAMS = Utilities.getBestElements(l1_bigrams, l2_bigrams, bigrams_proportion)


		# Transforming each sentence into a dictionary of features
		for i in range(0, len(l1_sentences)):
			l1_sentences[i] = [self.__getFeatures(l1_sentences[i]), label1]

		for i in range(0, len(l2_sentences)):
			l2_sentences[i] = [self.__getFeatures(l2_sentences[i]), label2]


		# Trains using the specified classifier
		self.__performTraining(classifier, l1_sentences, l2_sentences)




	""" Classify the specified text after obtaining all its words and bigrams """
	def classify(self, sentence):

		if self.MODEL is not None:
			features_list = self.__getFeatures(sentence)

			# If none of the features give any information: return None
			if True not in features_list.values():
				return None
			else:
				return self.MODEL.classify(features_list)

		else:
			print("ERROR: The classifier needs to be trained first")
			exit()




	""" Saves a trained model into the models folder """
	def saveModel(self, model_path, model_name):

		try:
			# If the folder does not exist: it is created
			if os.path.exists(model_path) is False:
				os.mkdir(model_path)

			model_file = open(model_path + model_name + ".pickle", 'wb')
			pickle.dump([self.MODEL, self.BEST_WORDS, self.BEST_BIGRAMS], model_file)

			model_file.close()
			print("The classifier model has been saved in '", model_path, "'")

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model cannot be saved into '", model_path, "'")
			exit()




	""" Loads a trained model into our classifier object """
	def loadModel(self, model_path, model_name):

		try:
			model_file = open(model_path + model_name + ".pickle", 'rb')
			self.MODEL, self.BEST_WORDS, self.BEST_BIGRAMS = pickle.load(model_file)

			model_file.close()
			print("The classifier model has been loaded from '", model_path, "'")

		except FileNotFoundError or PermissionError or IsADirectoryError:
			print("ERROR: The model '", model_path, "' cannot be loaded")
			exit()
