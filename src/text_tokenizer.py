# Created by Sinclert Perez (Sinclert@hotmail.com)


from nltk.stem import SnowballStemmer
from nltk.tokenize import TweetTokenizer

from utils import get_file_lines


stopwords_folder = "stopwords"

languages = {
	'danish', 'dutch', 'english', 'finnish', 'french',
	'german', 'hungarian', 'italian', 'norwegian', 'portuguese',
	'russian', 'spanish', 'swedish'
}




class TextTokenizer(object):

	""" Represents the text lemmatizer and tokenizer class

	Attributes
	----------
	lemmatizer : NLTK object
		allows us to extract the root of every word

	tokenizer : NLTK object
		allows us to split a text into individual tokens

	stopwords: set
		set of irrelevant words to filter
	"""




	def __init__(self, lang):

		""" Creates a text tokenizer object

		Attributes
		----------
		lang : string
			language in which the tokenizing process is going to be done
		"""

		if lang not in languages:
			exit('Invalid language')

		self.lemmatizer = SnowballStemmer(lang)
		self.tokenizer = TweetTokenizer(
			preserve_case = False,
			reduce_len = True,
			strip_handles = True
		)

		stopwords_path = "" # TODO
		self.stopwords = set(get_file_lines(stopwords_path))




	def __call__(self, text):

		""" Each time the instance is called

		Attributes
		----------
		text : string
			text that is going to be tokenize

		Returns
		----------
		tokens : list
			tokens of the specified text (without stopwords)
		"""

		tokens = self.tokenizer.tokenize(text)
		tokens = filter(lambda t: t not in self.stopwords, tokens)
		tokens = [self.lemmatizer.stem(token) for token in tokens]

		return tokens
