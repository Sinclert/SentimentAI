# Created by Sinclert Perez (Sinclert@hotmail.com)

import re


################ FILTERS ################
emoji_filter = re.compile('['
                          u'\U00002600-\U000027B0'
                          u'\U0001F300-\U0001F64F'
                          u'\U0001F680-\U0001F6FF'
                          u'\U0001F910-\U0001F919]+',
                          re.UNICODE)

link_filter = re.compile('http\S+')
html_filter = re.compile('&\w+;')
spaces_filter = re.compile('\s+')
user_filter = re.compile('(^|\s+)@\w+')




""" Reads the contents of a file and returns them inside a list """
def getFileContents(file_path):

	try:
		file = open(file_path, 'r', encoding = "UTF8")
		contents = file.read().splitlines()
		file.close()

		return contents

	except (FileNotFoundError, PermissionError, IsADirectoryError):
		print("ERROR: The file", file_path, "cannot be opened")
		exit()




""" Returns the tweet text after applying some filters """
def getCleanTweet(tweet):
	tweet = tweet._json

	# If it is a retweet: the original tweet is obtained
	if tweet.get('retweeted_status'):
		tweet = tweet['retweeted_status']

	# Removing any URL or image link in the text
	tweet_text = link_filter.sub("", tweet['text'])

	# Other tweet cleaning steps
	tweet_text = tweet_text.replace("#", "")
	tweet_text = html_filter.sub("", tweet_text)
	tweet_text = emoji_filter.sub("", tweet_text)
	tweet_text = spaces_filter.sub(" ", tweet_text)
	tweet_text = tweet_text.lower()

	return tweet_text




""" Splits tweets into sentences and returns those containing the word """
def filterTweets(tweets, word):

	try:
		word = word.lower()

		for tweet in tweets:
			sentences = re.split("[.:!?]\s+", tweet)
			sentences = filter(lambda s: word in s, sentences)

			for sentence in sentences:
				yield sentence

	# If the word is not a string or tweets not a iterable
	except (AttributeError, TypeError):
		print("ERROR: Invalid arguments")
		exit()




""" Appends the specified tweets (list) at the end of a text file """
def storeTweets(tweets, file_name, min_length = 30):

	try:
		file = open(file_name, 'a', encoding = "UTF8")

		for tweet in tweets:

			# Subtracting user names before storing
			tweet = user_filter.sub(" USER", tweet)
			tweet = tweet.strip()

			# Store the tweet only if it has enough length
			if len(tweet) >= min_length:
				file.write(tweet)
				file.write("\n")

		file.close()


	except (FileNotFoundError, PermissionError, IsADirectoryError):
		print("ERROR: The file '", file_name, "' cannot be opened")
		exit()
