# Created by Sinclert Perez (Sinclert@hotmail.com)


from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import TweepError

from twitter_keys import APP_KEYS

from utils import build_filters
from utils import clean_text


search_ops = {'AND', 'OR', ':'}




class TwitterMiner(object):

	""" Represents a Twitter REST API data miner

	Attributes:
	----------
		API:
			type: tweepy.API
			info: object used to make connection with Twitter
	"""




	def __init__(self, token_key: str, token_secret: str):

		""" Creates a Twitter miner object

		Arguments:
		----------
			token_key: identifies the user
			token_secret: accompanies the token key

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
	def get_text(tweet) -> str:

		""" Extracts the text from a Status object (tweet)

		Arguments:
		----------
			tweet: Status object containing all the attributes of a tweet

		Returns:
		----------
			text: lowercase tweet text

		"""

		if hasattr(tweet, 'retweeted_status'):
			tweet = tweet.retweeted_status

		try:
			return tweet.full_text.lower()
		except AttributeError:
			return tweet.text.lower()




	def get_user_tweets(self, user: str, word: str, depth: int = 1000) -> str:

		""" Generator that returns the 'depth' most recent user tweets

		Arguments:
		----------
			user: Twitter user account without the '@'
			word: word used to filter the tweets (lowercase)
			depth: number of tweets to retrieve (optional)

		Yield:
		----------
			tweet_text: cleaned tweet text

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




	def search_tweets(self, query: str, lang: str, filter_prob: int = 95, depth: int = 1000) -> str:

		""" Generator that returns the 'depth' most recent user tweets

		Arguments:
		----------
			query: string with logic operations (AND, OR...)
			lang: language abbreviation to filter the tweets
			filter_prob: probability percentage to remove query words (optional)
			depth: number of tweets to retrieve (optional)

		Yield:
		----------
			tweet_text: cleaned tweet text

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
				tweet_text = clean_text(tweet_text)

				yield tweet_text

		except TweepError:
			exit('Unable to find ' + str(depth) + ' tweets')
