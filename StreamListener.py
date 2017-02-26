# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, json
from Keys import keys
from tweepy import AppAuthHandler, API, OAuthHandler, StreamListener, Stream


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):

    # Attribute that stores the API connection object
    API = None




    """ Set the listener connection and basic attributes """
    def __init__(self, classifier1, classifier2, buffer_size, shared_dict):

        # Calling the superclass init method in case it does something
        super().__init__()

        # Initializing basic instance attributes
        self.__setConnection()
        self.classifier1 = classifier1
        self.classifier2 = classifier2
        self.buffer = buffer_size * [None]
        self.shared_dict = shared_dict
        self.counter = 0




    """ Establish Twitter API connection using user authentication """
    def __setConnection(self):

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




    """ Updates the dictionary counter and the temporal buffer labels """
    def __updateBuffers(self, label):

        if label is None:
            print("Tweet ignored (features lack of information)")

        else:
            try:
                self.shared_dict[self.buffer[self.counter]] -= 1
            except KeyError:
                pass

            self.buffer[self.counter] = label
            self.counter = (self.counter + 1) % len(self.buffer)
            self.shared_dict[label] += 1




    """ Initiates the Twitter streaming given query, languages and locations """
    def initStream(self, query, languages, coordinates):

        twitterStream = Stream(self.API.auth, self)
        twitterStream.filter(track = query,
                             languages = languages,
                             locations = coordinates)




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
                result = self.classifier1.classify(tweet_text)

                if result == 'Polarized':
                    self.__updateBuffers(self.classifier2.classify(tweet_text))
                elif result == 'Neutral':
                    self.__updateBuffers('Neutral')


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
