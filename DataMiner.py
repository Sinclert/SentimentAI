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

        ########### OAUTH TOKEN REQUEST PROCESS ###########
        #
        # auth_url = auth.get_authorization_url()
        #
        # print("Please visit this link and authorize the app:", auth_url)
        # print("Enter your PIN code")
        # verifier = input().strip()
        #
        # # Tokens should be store in a DB because they do not expire
        # token = auth.get_access_token(verifier)
        #
        ########### OAUTH TOKEN REQUEST PROCESS ###########

        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        # Creation and return of the API connection
        self.API = tweepy.API(auth)




    """ Returns a list containing friends IDs (up to 5000) """
    def getFriends(self, user):

        try:
            return self.API.friends_ids(id = user)

        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve friends from", user)
            exit()

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve friends from", user)
            exit()




    """ Returns a list containing followers IDs (up to 5000) """
    def getFollowers(self, user):

        try:
            return self.API.followers_ids(id = user)

        except tweepy.RateLimitError:
            print("RATE LIMIT ERROR: Unable to retrieve followers from", user)
            exit()

        except tweepy.TweepError:
            print("TWEEPY ERROR: Unable to retrieve followers from", user)
            exit()




    """ Returns a list containing most recent tweets containing the specified word (each 200 is a request) """
    def getUserTweets(self, user, word = None, depth = 1000):

        tweets_list = []

        try:
            for tweet in tweepy.Cursor(self.API.user_timeline, id = user, count = 200).items(depth):

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, "retweeted_status"):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text


                # If the tweet does not contain the specified word: continue
                if (word is not None) and (word.lower() not in tweet_text.lower()):
                    continue

                # If there is any URL or image link in the text: it is removed
                if (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)
                    tweet_text = tweet_text.strip()


                # The final text is added at the end of the list
                tweet_text = tweet_text.replace("\n", " ")
                tweets_list.append(tweet_text)


            # In case word is specified but there are not tweets with it
            if (word is not None) and (len(tweets_list) == 0):
                print("There are no tweets from", user, "containing '", word, "'")

            return tweets_list


        except tweepy.TweepError:

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
            for tweet in tweepy.Cursor(self.API.search, query, lang = language, count = 100).items(depth):

                # If it is a retweet: the original text is obtained
                if hasattr(tweet, "retweeted_status"):
                    tweet_text = tweet.retweeted_status.text
                else:
                    tweet_text = tweet.text

                # If there is any URL or image link in the text: it is removed
                if (len(tweet.entities['urls']) != 0) or (('media' in tweet.entities) == True):
                    tweet_text = re.sub("http\S+", "", tweet_text)
                    tweet_text = tweet_text.strip()


                # The final text is added at the end of the list
                tweet_text = tweet_text.replace("\n", " ")
                tweets_list.append(tweet_text)


            # In case there are not enough tweets: print message
            if len(tweets_list) < depth:
                print("There are not", depth, "tweets meeting query '", query, "' . Retrieving", len(tweets_list))

            return tweets_list


        except tweepy.TweepError:

            if len(tweets_list) == 0:
                print("TWEEPY ERROR: Unable to retrieve tweets from the specified search")
                exit()
            else:
                print("RATE LIMIT ERROR: Unable to retrieve", depth, "tweets. Returning", len(tweets_list))
                return tweets_list
