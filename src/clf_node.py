# Created by Sinclert Perez (Sinclert@hotmail.com)


from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_selection import chi2
from sklearn.feature_selection import SelectPercentile
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import BernoulliNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier as RandomForest
from sklearn.base import clone
from sklearn.model_selection import cross_val_score

from text_tokenizer import TextTokenizer

from utils import read_lines
from utils import load_object


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




	def __init__(self, file_name = None):

		""" Loads a trained model if specified

		Arguments:
		----------
			file_name:
				type: string
				info: name of the saved model file
		"""

		if file_name is not None:
			self.__dict__ = load_object(file_name, 'model')

		else:
			self.model = None
			self.selector = None
			self.vectorizer = None




	def __init_attr(self, algorithm, feats_pct, lang):

		""" Set ups the instance attributes before training

		Arguments:
		----------
			algorithm:
				type: string (lowercase)
				info: name of the algorithm to train

			feats_pct:
				type: int
				info: percentage of features to keep

			lang:
				type: string
				info: language to perform the tokenizer process
		"""

		try:
			self.model = algorithms[algorithm]
		except KeyError:
			exit('Invalid algorithm name')

		self.selector = SelectPercentile(
			score_func = chi2,
			percentile = feats_pct
		)

		self.vectorizer = CountVectorizer(
			tokenizer = TextTokenizer(lang),
			ngram_range = (1, 2)
		)




	def __build_feats(self, datasets_info):

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
			feats_v:
				type: numpy.array
				info: vector containing all the sentences features

			labels_v:
				type: numpy.array
				info: vector contains all the sentences labels
		"""

		feats = []
		labels = []

		for info in datasets_info:
			name = info['dataset_name']
			label = info['dataset_label']

			sentences = read_lines(
				file_name = name,
				file_type = 'dataset'
			)

			feats.extend(sentences)
			labels.extend([label] * len(sentences))

		# Sentences are transformed using tokenization and selection
		feats = self.vectorizer.fit_transform(feats)
		feats = self.selector.fit_transform(feats, labels)

		return feats, labels




	@staticmethod
	def __validate(algorithm, feats, labels, cv_folds = 10):

		""" Validates the trained algorithm using CV and F1 score

		Arguments:
		----------
			algorithm:
				type: string (lowercase)
				info: name of any valid classification algorithm

			feats:
				type: numpy.array / list
				info: vector containing all the sentences features

			labels:
				type: numpy.array / list
				info: vector contains all the sentences labels

			cv_folds:
				type: int
				info: number of cross validation folds
		"""

		results = cross_val_score(
			estimator = clone(algorithms[algorithm]),
			X = feats,
			y = labels,
			scoring = 'f1_weighted',
			cv = cv_folds
		)

		print('F1 score:', round(results.mean(), 4))




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




	def train(self, algorithm, feats_pct, lang, profile_data, validate = True):

		""" Trains the specified classification algorithm

		Arguments:
		----------
			algorithm:
				type: string (lowercase)
				info: name of the algorithm to train

			feats_pct:
				type: int
				info: percentage of features to keep

			lang:
				type: string
				info: language to perform the tokenizer process

			profile_data:
				type: list
				info: dictionaries containing datasets paths and labels

			validate:
				type: bool (optional)
				info: indicates if the model should be validated
		"""

		self.__init_attr(algorithm, feats_pct, lang)

		# Training process
		feats, labels = self.__build_feats(profile_data)
		self.model.fit(feats, labels)

		# Validation process
		if validate: self.__validate(
			algorithm = algorithm,
			feats = feats,
			labels = labels
		)

		print('Training process completed')
