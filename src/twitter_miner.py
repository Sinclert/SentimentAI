# Created by Sinclert Perez (Sinclert@hotmail.com)


from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import TweepError

from twitter_keys import APP_KEYS

from utils import build_filters
from utils import clean_text


search_ops = ['AND', 'OR', ':']




class TwitterMiner(object):

	""" Represents a Twitter REST API data miner

	Attributes:
	----------
		API:
		    type: tweepy.API
		    info: object used to make connection with Twitter
	"""




	def __init__(self, token_key, token_secret):

		""" Creates a Twitter miner object

		Arguments:
		----------
			token_key:
				type: string
				info: identifies the user

			token_secret:
				type: string
				info: accompanies the token key
		"""

		try:
			consumer_key = APP_KEYS['consumer_key']
			consumer_secret = APP_KEYS['consumer_secret']

			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(token_key, token_secret)

			self.API = API(auth)

		except TweepError:
			exit('Unable to create the tweepy API object')




	@staticmethod
	def get_text(tweet):

		""" Extracts the text from a Status object (tweet)

		Arguments:
		----------
			tweet:
				type: Status object
				info: contains all the attributes of a tweet

		Returns:
		----------
			text:
				type: string
				info: original tweet text
		"""

		if hasattr(tweet, 'retweeted_status'):
			tweet = tweet.retweeted_status

		try:
			return tweet.full_text
		except AttributeError:
			return tweet.text




	def get_user_tweets(self, user, word, depth = 1000):

		""" Generator that returns the 'depth' most recent user tweets

		Arguments:
		----------
			user:
				type: string
				info: Twitter user account without the '@'

			word:
				type: string (lowercase)
				info: word used to filter the tweets

			depth:
				type: int (optional)
				info: number of tweets to retrieve

		Yield:
		----------
			tweet_text:
				type: string
				info: cleaned tweet text
		"""

		try:
			cursor = Cursor(
				method = self.API.user_timeline,
				id = user,
				count = 200,
				tweet_mode = 'extended'
			)

			for tweet in cursor.items(depth):
				tweet_text = self.get_text(tweet)
				tweet_text = clean_text(tweet_text)

				if word in tweet_text: yield tweet_text

		except TweepError:
			exit('Unable to retrieve tweets from ' + user)




	def search_tweets(self, query, lang, filter_prob = 95, depth = 1000):

		""" Generator that returns the 'depth' most recent user tweets

		Arguments:
		----------
			query:
				type: string
				info: string with logic operations (AND, OR...)

			lang:
				type: string
				info: language abbreviation to filter the tweets

			filter_prob:
				type: int (optional)
				info: probability in which the query words are removed

			depth:
				type: int (optional)
				info: number of tweets to retrieve

		Yield:
		----------
			tweet_text:
				type: string
				info: cleaned tweet text
		"""

		try:
			cursor = Cursor(
				method = self.API.search,
				q = query,
				lang = lang,
				count = 100,
				tweet_mode = 'extended'
			)

			# Obtaining the search query words in order to build a filter
			query_words = query.split(' ')
			query_words = filter(
				lambda w: not any(op in w for op in search_ops),
				query_words
			)

			# Build a probabilistic filter in order to avoid overfitting
			search_filters = build_filters(query_words, filter_prob)


			for tweet in cursor.items(depth):
				tweet_text = self.get_text(tweet)
				tweet_text = clean_text(tweet_text, search_filters)

				yield tweet_text

		except TweepError:
			exit('Unable to find ' + str(depth) + ' tweets')
