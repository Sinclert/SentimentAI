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




""" Divides tweets into sentences and returns those containing the word """
def getSentences(tweets, word = None):

	# If there is a list of tweets as input
	if not isinstance(tweets, str):
		sentences = []

		for tweet in tweets:

			# Recursive call to obtain the sentences of each tweet
			for sentence in getSentences(tweet, word):
				sentences.append(sentence)

		return sentences

	# Base case: individual tweet
	elif isinstance(tweets, str):
		sentences = re.split("[.:!?]\s+", tweets)

		if word is not None:
			sentences = filter(lambda s: word.lower() in s, sentences)

		return sentences

	# If what we are processing is neither a list nor a string: error
	else:
		print("ERROR: Invalid value in one of the text inputs")
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
