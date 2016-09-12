# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, re
from Keys import keys
from tweepy import AppAuthHandler, API, Cursor, RateLimitError, TweepError


""" Class in charge of retrieving data from the Twitter API """
class DataMiner(object):

    # Attribute that stores the API connection object
    API = None




    """ Establish Twitter API connection using application-only authentication """
    def __init__(self):

        # Obtaining application keys from the Keys file
        consumer_key = keys['consumer_key']
        consumer_secret = keys['consumer_secret']

        # Application-only authentication creation
        auth = AppAuthHandler(consumer_key, consumer_secret)

        # Tweepy API connection creation
        self.API = API(auth)




    """ Returns a list containing friends IDs (up to 5000) """
    def getFriends(self, user):

        try:
            return self.API.friends_ids(id = user)

        except RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve friends from", user)
            exit()

        except TweepError:
            print("TWEEPY ERROR: Unable to retrieve friends from", user)
            exit()




    """ Returns a list containing followers IDs (up to 5000) """
    def getFollowers(self, user):

        try:
            return self.API.followers_ids(id = user)

        except RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve followers from", user)
            exit()

        except TweepError:
            print("TWEEPY ERROR: Unable to retrieve followers from", user)
            exit()




    """ Returns a list containing most recent tweets containing the specified word (each 200 is a request) """
    def getUserTweets(self, user, word = None, depth = 1000):

        tweets_list = []

        try:

            # Each tweet is processed and appended at the end of the list
            for tweet in Cursor(self.API.user_timeline, id = user, count = 200).items(depth):

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, 'retweeted_status'):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text

                # If the tweet does not contain the specified word: continue
                if (word is not None) and (word.lower() not in tweet.lower()):
                    continue


                # If there is any URL or image link in the text: it is removed
                if (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)

                tweets_list.append(Utilities.getCleanTweet(tweet_text))


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

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, 'retweeted_status'):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text


                # If there is any URL or image link in the text: it is removed
                if (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)

                tweets_list.append(Utilities.getCleanTweet(tweet_text))


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
