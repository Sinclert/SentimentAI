# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, json, re
from tweepy import OAuthHandler, StreamListener
from Keys import keys


""" Class in charge of retrieving live data from the Twitter Streaming API """
class TwitterListener(StreamListener):


    """ Establish Twitter API connection using user authentication """
    @staticmethod
    def init():

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




    """ Prints live data according to the stream parameters """
    def on_data(self, tweet):

        tweet_dict = json.loads(tweet)

        # If it is a retweet: the original text is obtained
        if tweet_dict.get('retweeted_status'):
            tweet_text = tweet_dict['retweeted_status']['text']
        else:
            tweet_text = tweet_dict['text']

        # If there is any URL or image link in the text: it is removed
        if (len(tweet_dict['entities']['urls']) != 0) or (tweet_dict['entities'].get('media') is not None):
            tweet_text = re.sub("http\S+", "", tweet_text)

        print(Utilities.getCleanTweet(tweet_text))




    """ In case of an error: prints its code """
    def on_error(self, status):

        print("CONNECTION ERROR:", status)
        exit()
