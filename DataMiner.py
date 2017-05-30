# Created by Sinclert Perez (Sinclert@hotmail.com)

from Keys import keys
from math import ceil
from tweepy import AppAuthHandler, API, Cursor, TweepError
from Utilities import getCleanTweet, storeTweets


""" Class in charge of retrieving data from the Twitter API """
class DataMiner(object):


    # Attribute that stores the API connection object
    API = None




    """ Establish Twitter API connection using app authentication """
    def __init__(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']

        try:
            # Application-only authentication creation
            auth = AppAuthHandler(consumer_key, consumer_secret)

            # Tweepy API connection creation
            self.API = API(auth)

        except TweepError:
            print("TWEEPY ERROR: Unable to establish connection with Twitter")
            exit()




    """ Gets most recent tweets containing the word (request each 200) """
    def getUserTweets(self, user, word = None, depth = 1000):

        tweets_list = []

        try:
            cursor = Cursor(self.API.user_timeline, id = user, count = 200)

            # Each tweet is processed and appended
            for tweet in cursor.items(depth):
                tweet_text = getCleanTweet(tweet)

                # If the tweet does not contain the specified word: continue
                if (word is not None) and (word.lower() not in tweet_text):
                    continue

                tweets_list.append(tweet_text)

            return tweets_list


        except TweepError:
            print("TWEEPY ERROR: Unable to retrieve", depth, "tweets from", user)
            exit()




    """ Stores the tweets fulfilling the specified query (request each 100).
        To learn about queries: https://dev.twitter.com/rest/public/search """
    def searchTweets(self, query, language, file, depth = 1000):

        # Number of pages and tweets returned
        num_pages = ceil(depth / 100)
        num_tweets = 0

        try:
            cursor = Cursor(self.API.search, query, lang = language, count = 100)

            # Each page is traversed and its tweets appended
            for page in cursor.pages(num_pages):
                num_tweets += len(page)
                tweets_list = []

                # Each tweet in the page is processed
                for tweet in page:
                    tweet_text = getCleanTweet(tweet)
                    tweets_list.append(tweet_text)

                # Storing the tweets for each page
                storeTweets(tweets_list, file)

            print("Tweets stored into", file)


        except TweepError:
            print("TWEEPY ERROR: Unable to retrieve", depth, "tweets from search")
            exit()
