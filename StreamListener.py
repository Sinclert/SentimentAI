# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, json, re
from tweepy import OAuthHandler, StreamListener, Stream
from Keys import keys


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):

    # Attributes to stores stream classifier, probabilities buffer and connection
    CLASSIFIER = None
    BUFFER = None
    AUTH = None

    # Attribute to store the line counter for overwriting
    COUNTER = 0




    """ Establish Twitter API connection using user authentication """
    def setConnection(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_token_secret = keys['access_token_secret']

        # Authentication creation using keys and tokens
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Tweepy API connection creation
        self.AUTH = auth




    """ Set the listener classifier, buffer and connection """
    def init(self, classifier, query, languages, coordinates, prob_buffer):
        self.CLASSIFIER = classifier
        self.BUFFER = prob_buffer
        self.setConnection()

        twitterStream = Stream(self.AUTH, self)
        twitterStream.filter(track = query, languages = languages, locations = coordinates)




    """ Prints live data according to the stream parameters """
    def on_data(self, tweet):

        # In case either the classifier or the buffer is not specified: error
        if (self.CLASSIFIER is None) or (self.BUFFER is None):
            print("ERROR: TwitterListener object requires to call 'init()' first")
            exit()

        labels = self.CLASSIFIER.MODEL.labels()
        tweet_dict = json.loads(tweet)


        try:
            # If it is a retweet: the original text is obtained
            if tweet_dict.get('retweeted_status'):
                tweet_text = tweet_dict['retweeted_status']['text']
            else:
                tweet_text = tweet_dict['text']

            # If there is any URL or image link in the text: it is removed
            if (len(tweet_dict['entities']['urls']) != 0) or (tweet_dict['entities'].get('media') is not None):
                tweet_text = re.sub("http\S+", "", tweet_text)


            # Clean the tweet
            tweet_text = Utilities.getCleanTweet(tweet_text)

            # If it has enough length: write it
            if len(tweet_text) >= 30:
                result = self.CLASSIFIER.classify([tweet_text])
                self.BUFFER[self.COUNTER] = result[0][labels[0]]
                self.COUNTER = (self.COUNTER + 1) % len(self.BUFFER)


        # In case of tweet limit warning: pass
        except KeyError:
            pass




    """ In case of an error: prints its code """
    def on_error(self, status):
        print("CONNECTION ERROR:", status)
        exit()
