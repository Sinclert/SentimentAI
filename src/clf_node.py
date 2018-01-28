# Created by Sinclert Perez (Sinclert@hotmail.com)


import numpy
import os
import pickle

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectPercentile
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier as RandomForest
from sklearn.preprocessing import LabelEncoder
from sklearn.base import clone
from sklearn.model_selection import cross_val_score

from text_tokenizer import TextTokenizer
from utils import get_file_lines


models_folder = "models"

algorithms = {
	"logistic-regression": LogisticRegression(),
	"naive-bayes": BernoulliNB(),
	"linear-svc": LinearSVC(),
	"random-forest": RandomForest(n_estimators = 100, n_jobs = -1)
}




class NodeClassif(object):

	""" Represents a hierarchical node classifier

	Attributes:
	----------
		model:
			type: sklearn.estimator
			info: trained classifier model

		selector:
			type: SelectPercentile
			info: filter the features depending on their relevance. It has:
				- score_func (func)
				- percentile (float)

		vectorizer:
			type: CountVectorizer
			info: builds the vector of features. It has:
				- tokenizer (class)
				- ngram_range (tuple of ints)
	"""




	def __init__(self, saved_model = None):

		""" Loads a trained model if specified

		Arguments:
		----------
			saved_model:
				type: string
				info: name of the saved model
		"""

		if saved_model is not None:
			self.__load_model("", saved_model)   # TODO

		else:
			self.model = None
			self.selector = None
			self.vectorizer = None




	""" Trains a classifier using the sentences from the specified files """
	def train(self, clf_name, l1_file, l2_file, features_pct, language):

		##############33
		CountVectorizer(
			tokenizer=TextTokenizer(language),
			ngram_range=(1, 2)
		)

		# Creating the feature selector object
		self.selector = SelectPercentile(
			score_func = chi2,
			percentile = features_pct
		)

		##########


		##########
		# Obtaining the label names
		label1 = os.path.basename(l1_file).rsplit('.')[0]
		label2 = os.path.basename(l2_file).rsplit('.')[0]

		# Obtaining every sentence inside both files
		l1_sentences = getFileLines(l1_file)
		l2_sentences = getFileLines(l2_file)

		# Getting the labels as a numpy array
		labels = numpy.array(([label1] * len(l1_sentences)) + ([label2] * len(l2_sentences)))

		# Extracting and selecting the best features
		features = numpy.array(l1_sentences + l2_sentences)
		features = self.vectorizer.fit_transform(features)
		features = self.selector.fit_transform(features, labels)

		#############


		# Training process
		classifier = possible_classifiers[clf_name]
		self.model = classifier.fit(features, labels)
		print("Training process completed")


		##########
		# The labels are encoded to perform F1 scoring
		labels = LabelEncoder().fit_transform(labels)
		bin_classifier = clone(algorithms[clf_name])

		# The model is tested using cross validation
		results = cross_val_score(
			estimator = bin_classifier,
			X = features,
			y = labels,
			scoring = 'f1',
			cv = 10,
			n_jobs = -1
		)

		print("F1 score:", round(results.mean(), 4), "\n")

		################




	""" Classify the specified text after obtaining all its features """
	def classify(self, sentence):

		try:
			features = self.vectorizer.transform([sentence])
			features = self.selector.transform(features)

			# If none of the features give any information: return None
			if features.getnnz() == 0:
				return None
			else:
				return self.model.predict(features)[0]

		except AttributeError:
			exit('The classifier needs to be trained first')




	""" Saves a trained model into the models folder """
	def saveModel(self, models_folder, model_name):

		# Joining the paths to create the total model path
		file_path = os.path.join(models_folder, model_name)

		try:
			# If the folder does not exist: it is created
			if os.path.exists(models_folder) is False:
				os.mkdir(models_folder)

			file = open(file_path, 'wb')
			pickle.dump([self.model, self.selector], file)
			file.close()

			print('Classifier model saved in', file_path)

		except IOError:
			exit('The model cannot be saved in ' + file_path)




	""" Loads a trained model into our classifier object """
	def __load_model(self, models_folder, model_name):

		# Joining the paths to create the total model path
		file_path = os.path.join(models_folder, model_name)

		try:
			file = open(file_path, 'rb')
			self.model, self.selector = pickle.load(file)
			file.close()

			print('Classifier model loaded from', file_path)

		except IOError:
			exit('The model cannot be loaded from ' + file_path)
