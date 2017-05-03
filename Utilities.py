# Created by Sinclert Perez (Sinclert@hotmail.com)

import re
from nltk.metrics import BigramAssocMeasures as BAM


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




""" Reads the stopwords from the specified language file """
def getStopWords(language = "english"):

	file_name = "./Stopwords/" + language + ".txt"

	try:
		file = open(file_name, 'r', encoding = "UTF8")
		lines = file.read().splitlines()
		file.close()

		# Storing the words line by line in a list
		stopwords = []
		for word in lines:
			stopwords.append(word)

		return stopwords

	except FileNotFoundError or PermissionError or IsADirectoryError:
		print("ERROR: The file", file_name, "cannot be opened")
		exit()




""" Finds the best 'n' elements based on their gain of information """
def getBestElements(l1_counter, l2_counter, percentage):

	# Counts the number of l1 and l2 elements as well as their sum
	l1_total = sum(l1_counter.values())
	l2_total = sum(l2_counter.values())
	total = l1_total + l2_total

	# Frequency distribution storing each element total appearances
	freq_dist = l1_counter + l2_counter
	scores = {}

	# Builds a dictionary of scores based on chi-squared test
	for elem, freq in freq_dist.items():
		scores[elem] = BAM.chi_sq(l1_counter[elem], (freq, l1_total), total)

	best_values = sorted(scores.items(),
	                     key = lambda pair: pair[1],
	                     reverse = True)

	# Retrieves the specified percentage of elements with highest scores
	values_cut = len(freq_dist) * percentage // 100
	best_elements = set(w for w, s in best_values[:values_cut])

	return best_elements




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
	if isinstance(tweets, list):
		sentences = []

		for tweet in tweets:
			tweet = tweet.lower()

			# Recursive call to obtain the sentences of each tweet
			for sentence in getSentences(tweet, word):
				sentences.append(sentence)

		return sentences

	# Base case: individual tweet
	elif isinstance(tweets, str):
		sentences = re.split("[.:!?]\s+", tweets)

		if word is not None:
			sentences[:] = [s for s in sentences if word.lower() in s]

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


	except PermissionError or IsADirectoryError:
		print("ERROR: The file '", file_name, "' cannot be opened")
		exit()
