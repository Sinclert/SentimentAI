# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, json
from Keys import keys
from tweepy import AppAuthHandler, API, OAuthHandler, StreamListener, Stream


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):

    # Attributes to stores stream classifiers, probabilities buffer and connection
    CLASSIFIER1 = None
    CLASSIFIER2 = None
    BUFFER = None
    API = None

    # Shared variable between this process and the graphic one
    SHARED_DICT = None

    # Attribute to store the buffer overwriting position
    COUNTER = 0




    """ Establish Twitter API connection using user authentication """
    def setConnection(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_token_secret = keys['access_token_secret']

        try:
            # AppAuthHandler call is needed due to a OAuth 1.0 bug
            AppAuthHandler(consumer_key, consumer_secret)

            # Authentication creation using keys and tokens
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)

            # Tweepy API connection creation
            self.API = API(auth)

        except Exception or ConnectionError:
            print("ERROR: Unable to establish a connection with Twitter")
            exit()




    """ Set the listener classifier, buffer and connection """
    def init(self, classifier1, classifier2, buffer_size, query, languages, coordinates, shared_dict):
        self.CLASSIFIER1 = classifier1
        self.CLASSIFIER2 = classifier2
        self.BUFFER = [None] * buffer_size
        self.SHARED_DICT = shared_dict

        twitterStream = Stream(self.API.auth, self)
        twitterStream.filter(track = query, languages = languages, locations = coordinates)




    """ Prints live data according to the stream parameters """
    def on_data(self, tweet):
        tweet = json.loads(tweet)

        try:
            # If it is a retweet: the original tweet is obtained
            if tweet.get('retweeted_status'):
                tweet = tweet['retweeted_status']

            # Clean the tweet
            tweet_text = Utilities.getCleanTweet(tweet)

            # If it has enough length: write it
            if len(tweet_text) >= 30:
                result = self.CLASSIFIER1.classify(tweet_text)

                # If the tweet is classified as polarized
                if result == 'Polarized':
                    self.updateBuffers(self.CLASSIFIER2.classify(tweet_text))

                # If the tweet is not consider as polarized: neutral
                else:
                    self.updateBuffers('Neutral')


        # In case of tweet limit warning: pass
        except KeyError:
            pass

        # In case of an attribute NoneType error
        except AttributeError:
            print("One of the TwitterListener attributes has not been correctly initiated")
            exit()




    """ In case of an error: prints its code """
    def on_error(self, status):
        print("CONNECTION ERROR:", status)
        exit()




    """ Updates the dictionary counter and the temporal buffer labels """
    def updateBuffers(self, label):

        try:
            self.SHARED_DICT[self.BUFFER[self.COUNTER]] -= 1
        except KeyError:
            pass

        self.BUFFER[self.COUNTER] = label
        self.COUNTER = (self.COUNTER + 1) % len(self.BUFFER)
        self.SHARED_DICT[label] += 1
