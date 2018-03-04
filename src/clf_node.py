# Created by Sinclert Perez (Sinclert@hotmail.com)


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




	def __init__(self, file_name = None, **parameters):

		""" Loads a trained model if specified

		Arguments:
		----------
			file_name:
				type: string
				info: name of the saved model file

			parameters:
				type: keywords arguments
				info: the possible keys are:

					- algorithm:
						type: string (lowercase)
						info: name of the algorithm to train

					- feats_pct:
						type: int
						info: percentage of features to keep

					- lang:
						type: string
						info: language to perform the tokenizer process
		"""

		if file_name is not None:
			self.__dict__ = load_object(file_name, 'model')

		else:

			try:
				self.model = algorithms[parameters['algorithm']]

				self.selector = SelectPercentile(
					score_func = chi2,
					percentile = parameters['feats_pct']
				)

				self.vectorizer = CountVectorizer(
					tokenizer = TextTokenizer(parameters['lang']),
					ngram_range = (1, 2)
				)

			except KeyError:
				exit('Invalid keyword arguments')




	@staticmethod
	def __build_feats(datasets_info):

		""" Builds the feature and label vectors from the specified datasets

		Arguments:
		----------
			datasets_info:
				type: list
				info: list of dictionaries containing:
					- dataset_file (string)
					- dataset_label (string)

		Returns:
		----------
			samples:
				type: list
				info: contains all the sentences

			samples:
				type: list
				info: contains all the sentences labels
		"""

		samples = []
		labels = []

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




	def __validate(self, samples, labels, cv_folds = 10):

		""" Validates the trained algorithm using CV and F1 score

		Arguments:
		----------
			samples:
				type: list
				info: contains all the sentences

			labels:
				type: list
				info: contains all the sentences labels

			cv_folds:
				type: int
				info: number of cross validation folds
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




	def get_labels(self):

		""" Gets the trained label names

		Returns:
		----------
			labels:
				type: list
				info: trained model label names
		"""

		try:
			return self.model.classes_
		except AttributeError:
			exit('The classifier has not been trained')




	def predict(self, sentence):

		""" Predicts the label of the given sentence

		Arguments:
		----------
			sentence:
				type: string
				info: text to classify

		Returns:
		----------
			label:
				type: string / None
				info: predicted sentence label
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




	def train(self, profile_data, validate = True):

		""" Trains the specified classification algorithm

		Arguments:
		----------
			profile_data:
				type: list
				info: dictionaries containing datasets paths and labels

			validate:
				type: bool (optional)
				info: indicates if the model should be validated
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
