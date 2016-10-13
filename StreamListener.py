# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, json, re
from tweepy import AppAuthHandler, API, OAuthHandler, StreamListener, Stream
from Keys import keys


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):

    # Attributes to stores stream classifier, probabilities buffer and connection
    CLASSIFIER = None
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

        # AppAuthHandler call is needed due to a OAuth 1.0 bug
        AppAuthHandler(consumer_key, consumer_secret)

        # Authentication creation using keys and tokens
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Tweepy API connection creation
        self.API = API(auth)




    """ Set the listener classifier, buffer and connection """
    def init(self, classifier, buffer_size, query, languages, coordinates, shared_dict):
        self.CLASSIFIER = classifier
        self.BUFFER = [None] * buffer_size
        self.SHARED_DICT = shared_dict

        twitterStream = Stream(self.API.auth, self)
        twitterStream.filter(track = query, languages = languages, locations = coordinates)




    """ Prints live data according to the stream parameters """
    def on_data(self, tweet):

        # In case either the classifier or the buffer is not specified: error
        if (self.CLASSIFIER is None) or (self.BUFFER is None):
            print("ERROR: TwitterListener object requires to call 'init()' first")
            exit()

        labels = sorted(self.CLASSIFIER.MODEL.labels())
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
                result = self.CLASSIFIER.classify(tweet_text)

                # If the classifier supports probabilities
                if isinstance(result, dict):

                    if result[labels[0]] > 0.55:
                        self.updateBuffers(labels[0])

                    if result[labels[1]] > 0.55:
                        self.updateBuffers(labels[1])

                # If the result is just the label
                else:
                    self.updateBuffers(result)


        # In case of tweet limit warning: pass
        except KeyError:
            pass




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
