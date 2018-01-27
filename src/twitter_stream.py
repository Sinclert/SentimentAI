# Created by Sinclert Perez (Sinclert@hotmail.com)

from keys import keys
from tweepy import API, OAuthHandler, StreamListener, Stream, TweepError
from utils import getCleanTweet


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):


    # Attribute that stores the API connection object
    API = None




    """ Set the listener connection and basic attributes """
    def __init__(self, h_cls, buffer_size, labels):

        # Calling the superclass init method in case it does something
        super().__init__()

        # Initializing basic instance attributes
        self.__setConnection()
        self.hierarchical_cls = h_cls
        self.buffer = buffer_size * [None]
        self.counter = 0
        self.stream = None
        self.stream_dict = dict().fromkeys(labels, 0)




    """ Establish Twitter API connection using user authentication """
    def __setConnection(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_token_secret = keys['access_token_secret']

        try:
            # Authentication creation using keys and tokens
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            # Tweepy API connection creation
            self.API = API(auth)

        except TweepError:
            print("TWEEPY ERROR: Unable to establish connection with Twitter")
            exit()




    """ Updates the dictionary counter and the temporal buffer labels """
    def __updateBuffers(self, label):

        try:
            self.stream_dict[self.buffer[self.counter]] -= 1
        except KeyError:
            pass

        self.buffer[self.counter] = label
        self.counter = (self.counter + 1) % len(self.buffer)
        self.stream_dict[label] += 1




    """ Initiates the streaming given query, languages and locations """
    def initStream(self, query, languages, coordinates):

        self.stream = Stream(self.API.auth, self)
        self.stream.filter(track = query,
                           languages = languages,
                           locations = coordinates,
                           async = True)




    """ Closes the Twitter streaming """
    def closeStream(self):
        self.stream.disconnect()
        print("Disconnected from the Twitter streaming")




    """ Prints live data according to the stream parameters """
    def on_status(self, tweet):

        try:
            tweet_text = getCleanTweet(tweet)
            label = self.hierarchical_cls.predict(tweet_text)

            if label is not None:
                self.__updateBuffers(label)

        # In case of tweet limit warning: pass
        except KeyError:
            pass

        # In case of an attribute NoneType error
        except AttributeError:
            print("TwitterListener attributes not correctly initiated")
            exit()




    """ In case of an error: prints its code """
    def on_error(self, status):
        print("CONNECTION ERROR:", status)
        exit()
