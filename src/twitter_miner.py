# Created by Sinclert Perez (Sinclert@hotmail.com)


from tweepy import API
from tweepy import AppAuthHandler
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import TweepError

from constants import CONSUMER_KEY as CK
from constants import CONSUMER_SECRET as CS
from constants import TOKEN_KEY as TK
from constants import TOKEN_SECRET as TS

from utils import clean_text
from utils import get_tweet_text


class TwitterMiner(object):

	""" Represents a Twitter data miner

	Attributes
	----------
	API : tweepy API
		object used to make connection with Twitter end point
	"""




	def __init__(self):

		""" Creates the Twitter miner object """

		self.API = None
		self.__set_API(TK, TS)




	def __set_API(self, token_key, token_secret, mode = 'app'):

		""" Sets the instance API attribute using global keys

		Arguments
		---------
		mode : string (optional) {app, user}
			specifies if the API should connect as application or as user

		token_key : string
			string that identifies a token

		token_secret : string
			string that accompany the specified token
		"""

		try:

			# App authentication
			if mode == 'app':
				auth = AppAuthHandler(CK, CS)
				self.API = API(auth)

			# User authentication
			elif mode == 'user':
				auth = OAuthHandler(CK, CS)
				auth.set_access_token(token_key, token_secret)
				self.API = API(auth)

			else:
				exit('Invalid mode. Only "app" and "user" are valid')

		except TweepError:
			exit('Unable to create the tweepy API object')




	def get_user_tweets(self, user, depth = 1000):

		""" Generator that returns the 'depth' most recent user tweets

		Arguments
		---------
		user : string
			Twitter user account without the '@'

		depth : int (optional)
			number of tweets to retrieve
		"""

		try:
			cursor = Cursor(
				method = self.API.user_timeline,
				id = user,
				count = 200
			)

			for tweet in cursor.items(depth):
				tweet_text = get_tweet_text(tweet)
				tweet_text = clean_text(tweet_text)

				yield tweet_text

		except TweepError:
			exit('Unable to retrieve tweets from ' + user)




	def search_tweets(self, query, lang, depth = 1000):

		""" Generator that returns 'depth' tweets fulfilling the query

		Arguments
		---------
		query : string
			string with logic operations (AND, OR...) to search

		lang : string
			abbreviation that indicates the desired tweets language

		depth : int (optional)
			number of tweets to retrieve
		"""

		try:
			cursor = Cursor(
				method = self.API.search,
				query = query,
				lang = lang,
				count = 100
			)

			for tweet in cursor.items(depth):
				tweet_text = get_tweet_text(tweet)
				tweet_text = clean_text(tweet_text)

				yield tweet_text

		except TweepError:
			exit('Unable to find ' + str(depth) + ' tweets')
