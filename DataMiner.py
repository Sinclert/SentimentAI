# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities
from Keys import keys
from tweepy import AppAuthHandler, API, Cursor, TweepError


""" Class in charge of retrieving data from the Twitter API """
class DataMiner(object):

    # Attribute that stores the API connection object
    API = None




    """ Establish Twitter API connection using application-only authentication """
    def __init__(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']

        try:
            # Application-only authentication creation
            auth = AppAuthHandler(consumer_key, consumer_secret)

            # Tweepy API connection creation
            self.API = API(auth)

        except Exception or ConnectionError:
            print("ERROR: Unable to establish a connection with Twitter")
            exit()




    """ Returns a list containing most recent tweets containing the specified word (each 200 is a request) """
    def getUserTweets(self, user, word = None, depth = 1000):

        tweets_list = []

        try:

            # Each tweet is processed and appended at the end of the list
            for tweet in Cursor(self.API.user_timeline, id = user, count = 200).items(depth):
                tweet = tweet._json

                # If it is a retweet: the original tweet is obtained
                if tweet.get('retweeted_status'):
                    tweet = tweet['retweeted_status']

                # If the tweet does not contain the specified word: continue
                if (word is not None) and (word.lower() not in tweet['text'].lower()):
                    continue

                tweets_list.append(Utilities.getCleanTweet(tweet))

            # In case word is specified but there are not tweets with it
            if (word is not None) and (len(tweets_list) == 0):
                print("There are no tweets from", user, "containing '", word, "'")

            return tweets_list


        except TweepError:

            if len(tweets_list) == 0:
                print("TWEEPY ERROR: Unable to retrieve most recent tweets from", user)
                exit()
            else:
                print("RATE LIMIT ERROR: Unable to retrieve", depth, "tweets from", user, ". Returning", len(tweets_list))
                return tweets_list




    """ Returns a list containing tweets that fulfill the specified query (each 100 is a request).
        Link to learn about queries: https://dev.twitter.com/rest/public/search """
    def searchTweets(self, query, language, depth = 1000):

        tweets_list = []

        try:

            # Each tweet is processed and appended at the end of the list
            for tweet in Cursor(self.API.search, query, lang = language, count = 100).items(depth):
                tweet = tweet._json

                # If it is a retweet: the original tweet is obtained
                if tweet.get('retweeted_status'):
                    tweet = tweet['retweeted_status']

                tweets_list.append(Utilities.getCleanTweet(tweet))

            # In case there are not enough tweets: print message
            if len(tweets_list) < depth:
                print("There are not", depth, "tweets meeting query '", query, "' . Retrieving", len(tweets_list))

            return tweets_list


        except TweepError:

            if len(tweets_list) == 0:
                print("TWEEPY ERROR: Unable to retrieve tweets from the specified search")
                exit()
            else:
                print("RATE LIMIT ERROR: Unable to retrieve", depth, "tweets. Returning", len(tweets_list))
                return tweets_list
