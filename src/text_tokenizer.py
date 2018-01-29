# Created by Sinclert Perez (Sinclert@hotmail.com)


from nltk.stem import SnowballStemmer
from nltk.tokenize import TweetTokenizer

from utils_files import read_lines


languages = {
	'danish', 'dutch', 'english', 'finnish', 'french',
	'german', 'hungarian', 'italian', 'norwegian', 'portuguese',
	'russian', 'spanish', 'swedish'
}




class TextTokenizer(object):

	""" Represents the text lemmatizer and tokenizer class

	Attributes:
	----------
		lemmatizer:
		    type: SnowballStemmer
		    info: use to extract the root of every word

		tokenizer:
		    type: TweetTokenizer
		    info: use to split a text into individual tokens

		stopwords:
		    type: set
		    info: irrelevant words to filter
	"""




	def __init__(self, lang):

		""" Creates a text tokenizer object

		Arguments:
		----------
			lang:
				type: string
				info: language to perform the tokenizer process
		"""

		if lang not in languages:
			exit('Invalid language')

		self.lemmatizer = SnowballStemmer(lang)
		self.tokenizer = TweetTokenizer(
			preserve_case = False,
			reduce_len = True,
			strip_handles = True
		)

		self.stopwords = set(read_lines(
			file_name = lang + '.txt',
			file_type = 'stopwords'
		))




	def __call__(self, text):

		""" Tokenize the specified text

		Arguments:
		----------
			text:
				type: string
				info: text that is going to be tokenize

		Returns:
		----------
			tokens:
				type: list
				info: text tokens (without stopwords)
		"""

		tokens = self.tokenizer.tokenize(text)
		tokens = filter(lambda t: t not in self.stopwords, tokens)
		tokens = [self.lemmatizer.stem(token) for token in tokens]

		return tokens
