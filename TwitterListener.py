# Created by Sinclert Perez (Sinclert@hotmail.com)

from Keys import keys
from tweepy import API, OAuthHandler, StreamListener, Stream
from Utilities import getCleanTweet


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):


    # Attribute that stores the API connection object
    API = None




    """ Set the listener connection and basic attributes """
    def __init__(self, classifier1, classifier2, buffer_size, labels):

        # Calling the superclass init method in case it does something
        super().__init__()

        # Initializing basic instance attributes
        self.__setConnection()
        self.classifier1 = classifier1
        self.classifier2 = classifier2
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

        except Exception or ConnectionError:
            print("ERROR: Unable to establish a connection with Twitter")
            exit()




    """ Updates the dictionary counter and the temporal buffer labels """
    def __updateBuffers(self, label):

        if label is None:
            print("Tweet ignored (features lack of information)")

        else:
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
