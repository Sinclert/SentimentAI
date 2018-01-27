# Created by Sinclert Perez (Sinclert@hotmail.com)


from collections import Counter

from tweepy import API
from tweepy import OAuthHandler
from tweepy import StreamListener
from tweepy import Stream
from tweepy import TweepError

from twitter_keys import APP_KEYS

from utils import clean_text
from utils import get_tweet_text




class TwitterListener(StreamListener):

    """ Represents a Twitter stream listener

    Attributes
	----------
	API : tweepy API
		object used to make connection with Twitter end point

    stream : tweepy Stream
        Twitter stream end point. Only works with OAuth

	buffer : list
	    circular buffer containing the latest label predictions

	index : int
	    buffer index to the next position to be replaced

	clf: HierarchicalClassif
	    hierarchical classifier to predict tweets labels

	counters: dict
	    label counters
    """




    def __init__(self, token_key, token_secret, buffer_size, clf):

        """ Creates a Twitter listener object

        Arguments
		---------
		token_key : string
			string that identifies a user token

		token_secret : string
			string that accompany the user token

		buffer_size : int
			size of the label circular buffer

		clf: HierarchicalClassif object
		    hierarchical classifier to predict tweets labels
		"""

        super().__init__()

        try:
            consumer_key = APP_KEYS['consumer_key']
            consumer_secret = APP_KEYS['consumer_secret']

            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(token_key, token_secret)

            self.API = API(auth)

        except TweepError:
            exit('Unable to create the tweepy API object')

        self.stream = None
        self.buffer = buffer_size * [None]
        self.index = 0
        self.clf = clf
        self.counters = Counter()




    def __update_buffer(self, label):

        """ Replace the self.index position by the specified label

        Arguments
		---------
		label : string
			label to the replace the one in self.index position
        """

        try:
            self.counters[self.buffer[self.index]] -= 1
        except KeyError:
            pass

        self.buffer[self.index] = label
        self.index = (self.index + 1) % len(self.buffer)
        self.counters[label] += 1




    def start_stream(self, queries, languages, coordinates, timeout = 15):

        """ Starts the Twitter stream

        Arguments
		---------
		queries : string
			comma separated queries to filter the stream

		languages: string
		    comma separated language codes to filter the stream

		coordinates : string
		    comma separated groups of 4 coordinates to filter the stream

		    1. South-West longitude
		    2. South-West latitude
		    3. North-East longitude
		    4. North-East latitude

		timeout : int (optional)
		    number of seconds to launch an exception due to lack of data
        """

        self.stream = Stream(
            auth = self.API.auth,
            listener = self,
            timeout = timeout
        )

        self.stream.filter(
            track = queries,
            languages = languages,
            locations = coordinates,
            async = True
        )




    def finish_stream(self):

        """ Closes the Twitter stream """

        self.stream.disconnect()
        print('Disconnected from the Twitter stream')




    def on_status(self, tweet):

        """ Process received tweet

        Arguments
		---------
	    tweet : dictionary
		    dict object containing all the fields of a tweet
        """

        tweet_text = get_tweet_text(tweet)
        tweet_text = clean_text(tweet_text)

        label = self.clf.predict(tweet_text)

        if label is not None:
            self.__update_buffer(label)




    def on_exception(self, exception):

        """ Finish stream due to the timeout exception """

        print('Timeout exception due to lack of data')
        self.finish_stream()




    def on_error(self, code):

        """ Prints error code

        Arguments
		---------
		code : int
			stream error code
        """

        exit('Twitter stream error: ' + code)
