# Created by Sinclert Perez (Sinclert@hotmail.com)


from tweepy import API
from tweepy import Cursor
from tweepy import OAuthHandler
from tweepy import TweepError

from twitter_keys import APP_KEYS

from utils import clean_text
from utils import get_tweet_text




class TwitterMiner(object):

	""" Represents a Twitter data miner

	Attributes
	----------
	API : tweepy API
		object used to make connection with Twitter end point
	"""




	def __init__(self, token_key, token_secret):

		""" Creates a Twitter miner object

		Arguments
		---------
		token_key : string
			string that identifies a user token

		token_secret : string
			string that accompany the user token
		"""

		try:
			consumer_key = APP_KEYS['consumer_key']
			consumer_secret = APP_KEYS['consumer_secret']

			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(token_key, token_secret)

			self.API = API(auth)

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
