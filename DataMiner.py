# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re, tweepy
from Keys import keys


""" Class in charge of retrieving data from the Twitter API """
class DataMiner(object):

    # Attribute that stores the API connection object
    API = None


    """ Establish Twitter API connection using keys and tokens """
    def __init__(self):

        # Obtaining keys and tokens from the Keys file
        CONSUMER_KEY = keys['consumer_key']
        CONSUMER_SECRET = keys['consumer_secret']
        ACCESS_TOKEN = keys['access_token']
        ACCESS_TOKEN_SECRET = keys['access_token_secret']

        # Authenticator manager creation and introduction of tokens
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # Creation and return of the API connection
        self.API = tweepy.API(auth)




    """ Returns a list containing friends IDs (up to 5000) """
    def getFriends(self, user):

        try:
            return self.API.friends_ids(id = user)

        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve friends from", user)
            exit(-1)

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve friends from", user)
            exit(-1)




    """ Returns a list containing followers IDs (up to 5000) """
    def getFollowers(self, user):

        try:
            return self.API.followers_ids(id = user)

        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve followers from", user)
            exit(-1)

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve followers from", user)
            exit(-1)




    """ Returns a list containing most recent tweet texts subtracting URLs (each 200 is a request) """
    def getUserTweets(self, user, count = 200):

        tweets_list = []

        try:
            for tweet in tweepy.Cursor(self.API.user_timeline, id = user).items(count):

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, "retweeted_status"):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text

                # If there is any URL or image link in the text: it is removed
                if (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)
                    tweet_text = tweet_text.replace("\n", "")
                    tweet_text = tweet_text.strip()

                # The final text is added at the end of the list
                tweets_list.append(tweet_text)


            # In case there are not enough tweets: print message
            if len(tweets_list) < count:
                print("There are not", count, "tweets from", user, ". Retrieving", len(tweets_list))

            return tweets_list


        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve most recent tweets from", user)
            exit(-1)

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve most recent tweets from", user)
            exit(-1)




    """ Returns a list of tweet texts containing the specified word (each 200 is a request) """
    def getTweetsContainingWord(self, user, word, depth = 1000):

        tweets_list = []

        try:
            for tweet in tweepy.Cursor(self.API.user_timeline, id = user).items(depth):

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, "retweeted_status"):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text


                # If the tweet does not contain the word: continue
                if word.lower() not in tweet_text.lower():
                    continue

                # If there is any URL or image link in the text: it is removed
                elif (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)
                    tweet_text = tweet_text.replace("\n", "")
                    tweet_text = tweet_text.strip()


                # The final text is added at the end of the list
                tweets_list.append(tweet_text)


            # In case there are not any tweet with the specified word: print message
            if len(tweets_list) == 0:
                print("There are no tweets from", user, "containing '", word, "'")

            return tweets_list


        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve most recent tweets from", user, "containing", word)
            exit(-1)

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve most recent tweets from", user, "containing", word)
            exit(-1)




##### TESTING #####
data = DataMiner()
print(len(data.getFriends("Sinclert_95")))
print(len(data.getFollowers("Sinclert_95")))
print(data.getUserTweets("Sinclert_95", 10))
print(data.getTweetsContainingWord("Sinclert_95", "Obama"))
