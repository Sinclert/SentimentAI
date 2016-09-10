# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, json, re
from tweepy import OAuthHandler, StreamListener
from Keys import keys


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):

    # Attribute to stores the stream classifier
    CLASSIFIER = None

    # Attribute to store the output file name
    OUTPUT = None

    # Attribute to store the number of results stored in the output file
    TOTAL_LINES = 200

    # Attribute to store the line counter for overwriting
    LINE_COUNTER = 0




    """ Establish Twitter API connection using user authentication """
    @staticmethod
    def getConnection():

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']
        access_token = keys['access_token']
        access_token_secret = keys['access_token_secret']

        # Authentication creation using keys and tokens
        auth = OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        # Tweepy API connection creation
        return auth




    """ Set the listener classifier and output file """
    def init(self, classifier, output_file):
        self.CLASSIFIER = classifier
        self.OUTPUT = output_file




    """ Prints live data according to the stream parameters """
    def on_data(self, tweet):

        # In case either the classifier or the output file are not specified: error
        if (self.CLASSIFIER is None) or (self.OUTPUT is None):
            print("ERROR: The TwitterListener object needs to call 'init()' first")
            exit()

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

                if result[0]['Positive'] >= result[0]['Negative']:
                    string = "Positive " + str(result[0]['Positive']) + "\n"
                else:
                    string = "Negative " + str(result[0]['Negative']) + "\n"

                Utilities.storeStreamResults(string, self.OUTPUT, self.TOTAL_LINES, self.LINE_COUNTER)
                self.LINE_COUNTER += 1

                # Restart line counter
                if self.LINE_COUNTER >= self.TOTAL_LINES:
                    self.LINE_COUNTER = 0


        except KeyError:
            print("One of the tweet texts can not be obtained")




    """ In case of an error: prints its code """
    def on_error(self, status):
        print("CONNECTION ERROR:", status)
        exit()
