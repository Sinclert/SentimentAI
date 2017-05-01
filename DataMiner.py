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

        except Exception or ConnectionError:
            print("ERROR: Unable to establish a connection with Twitter")
            exit()




    """ Gets most recent tweets containing the word (request each 200) """
    def getUserTweets(self, user, word = None, depth = 1000):

        tweets_list = []

        try:
            cursor = Cursor(self.API.user_timeline, id = user, count = 200)

            # Each tweet is processed and appended
            for tweet in cursor.items(depth):
                tweet = tweet._json

                # If it is a retweet: the original tweet is obtained
                if tweet.get('retweeted_status'):
                    tweet = tweet['retweeted_status']

                # If the tweet does not contain the specified word: continue
                if (word is not None) and (word.lower() not in tweet['text'].lower()):
                    continue

                tweets_list.append(getCleanTweet(tweet))

            # In case word is specified but there are not tweets with it
            if (word is not None) and (len(tweets_list) == 0):
                print("There are no tweets from", user, "containing '", word, "'")

            return tweets_list


        except TweepError:

            if len(tweets_list) == 0:
                print("TWEEPY ERROR: Unable to retrieve most recent tweets from", user)
                exit()
            else:
                print("RATE LIMIT ERROR: Returning", len(tweets_list), "tweets")
                return tweets_list




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
                    tweet = tweet._json

                    # If it is a retweet: the original tweet is obtained
                    if tweet.get('retweeted_status'):
                        tweet = tweet['retweeted_status']

                    tweets_list.append(getCleanTweet(tweet))

                # Storing the tweets for each page
                storeTweets(tweets_list, file)

            print("Tweets stored into", file)


        except TweepError:

            if num_tweets == 0:
                print("TWEEPY ERROR: Unable to retrieve tweets from the specified search")
                exit()
            else:
                print("RATE LIMIT ERROR: Returning", num_tweets, "tweets")
