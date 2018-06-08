# Created by Sinclert Perez (Sinclert@hotmail.com)

from typing import Tuple
from typing import Union

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectPercentile
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier as RandomForest
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score

from text_tokenizer import TextTokenizer

from utils import read_lines
from utils import load_object


algorithms = {
	"logistic-regression": LogisticRegression(),
	"naive-bayes": MultinomialNB(),
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




	def __init__(self, file_name: str = None, **kwargs):

		""" Loads a trained model if specified

		Arguments:
		----------
			file_name: saved model file name (optional)

			kwargs: possible arguments:
				- algorithm: name of the algorithm to train
				- feats_pct: percentage of features to keep
				- lang: language to perform the tokenizer process

		"""

		if file_name is not None:
			self.__dict__ = load_object(file_name, 'model')

		else:

			try:
				self.model = algorithms[kwargs['algorithm']]

				self.selector = SelectPercentile(
					score_func = chi2,
					percentile = kwargs['feats_pct']
				)

				self.vectorizer = CountVectorizer(
					tokenizer = TextTokenizer(kwargs['lang']),
					ngram_range = (1, 2)
				)

			except KeyError:
				exit('Invalid keyword arguments')




	@staticmethod
	def __build_feats(datasets_info: list) -> Tuple[list, list]:

		""" Builds the feature and label vectors from the specified datasets

		Arguments:
		----------
			datasets_info: list of dictionaries containing:
				- dataset_file (string)
				- dataset_label (string)

		Returns:
		----------
			samples: contains all the sentences
			labels: contains all the sentences labels

		"""

		samples, labels = [], []

		for info in datasets_info:
			name = info['dataset_name']
			label = info['dataset_label']

			sentences = read_lines(
				file_name = name,
				file_type = 'dataset'
			)

			samples.extend(sentences)
			labels.extend([label] * len(sentences))

		return samples, labels




	def __validate(self, samples: list, labels: list, cv_folds: int = 10):

		""" Validates the trained algorithm using CV and F1 score

		Arguments:
		----------
			samples: contains all the sentences
			labels: contains all the sentences labels
			cv_folds: number of cross validation folds (optional)

		"""

		model = make_pipeline(self.vectorizer, self.selector, self.model)
		print('Starting cross-validation')

		results = cross_val_score(
			estimator = model,
			X = samples,
			y = labels,
			scoring = 'f1_weighted',
			cv = cv_folds,
			n_jobs = -1
		)

		print('F-score:', round(results.mean(), 4))




	def get_labels(self) -> list:

		""" Gets the trained label names

		Returns:
		----------
			labels: trained model label names

		"""

		try:
			return list(self.model.classes_)

		except AttributeError:
			exit('The classifier has not been trained')




	def predict(self, sentence: str) -> Union[str, None]:

		""" Predicts the label of the given sentence

		Arguments:
		----------
			sentence: text to classify

		Returns:
		----------
			label: predicted sentence label

		"""

		try:
			feats = self.vectorizer.transform([sentence])
			feats = self.selector.transform(feats)

			# If none of the features give any information
			if feats.getnnz() == 0:
				return None

			return self.model.predict(feats)[0]

		except AttributeError:
			exit('The classifier has not been trained')




	def train(self, profile_data: list, validate: bool = True):

		""" Trains the specified classification algorithm

		Arguments:
		----------
			profile_data: dictionaries containing datasets paths and labels
			validate: indicates if the model should be validated (optional)

		"""

		samples, labels = self.__build_feats(profile_data)

		# Samples are transformed into features in order to train
		feats = self.vectorizer.fit_transform(samples)
		feats = self.selector.fit_transform(feats, labels)
		self.model.fit(feats, labels)

		# Validation process
		if validate: self.__validate(
			samples = samples,
			labels = labels
		)
