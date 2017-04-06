# Created by Sinclert Perez (Sinclert@hotmail.com)

import re
from nltk.classify import util
from nltk.metrics import BigramAssocMeasures as BAM
from multiprocessing import Pool, cpu_count
from functools import partial


################ FILTERS ################
emoji_filter = re.compile(u'['
                            u'\U00002600-\U000027B0'
                            u'\U0001F300-\U0001F64F'
                            u'\U0001F680-\U0001F6FF'
                            u'\U0001F910-\U0001F919]+',
                            re.UNICODE)

html_filter = re.compile('&\w+;')
spaces_filter = re.compile('\s+')
user_filter = re.compile('(^|\s+)@\w+')




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




""" Returns the tweet text as a common sentence after applying some filters """
def getCleanTweet(tweet):

	# If there is any URL or image link in the text: it is removed
	if (len(tweet['entities']['urls']) != 0) or (tweet['entities'].get('media') is not None):
		tweet_text = re.sub("http\S+", "", tweet['text'])
	else:
		tweet_text = tweet['text']

	# Tweet cleaning steps
	tweet_text = tweet_text.replace("#", "")
	tweet_text = html_filter.sub("", tweet_text)
	tweet_text = emoji_filter.sub("", tweet_text)
	tweet_text = spaces_filter.sub(" ", tweet_text)

	return tweet_text




""" Divides tweets into sentences and returns those containing the word """
def getSentences(tweets, word = None):

	# If there is a list of tweets as input
	if isinstance(tweets, list):
		sentences = []

		for tweet in tweets:

			# Recursive call to obtain the sentences of each individual tweet
			for sentence in getSentences(tweet, word):
				sentences.append(sentence)

		return sentences

	# Base case: individual tweet
	elif isinstance(tweets, str):
		sentences = re.split("[.:!?]\s+", str(tweets))

		if word is not None:
			sentences[:] = [s for s in sentences if word.lower() in s.lower()]

		return sentences

	# If what we are processing is neither a list nor a string: error
	else:
		print("ERROR: Invalid value in one of the text inputs")
		exit()




""" Tests the specified classifier applying cross validation """
def crossValidation(classifier, l1_features, l2_features, folds = 10):

	if folds > 1:

		# Calculating cut offs in both features lists
		l1_cutoff = len(l1_features) // folds
		l2_cutoff = len(l2_features) // folds

		func = partial(cvFold,
		               classifier,
		               l1_features,
		               l2_features,
		               l1_cutoff,
		               l2_cutoff,
		               folds)

		# Creating the pool of processes and mapping them to the folds
		processes = Pool(cpu_count())
		processes_output = processes.map(func = func, iterable = range(folds))
		processes.close()

		return round((sum(processes_output) / folds), 4)

	else:
		print("ERROR: The number of C.V. folds must be greater than 1")
		exit()




""" Performs a single iteration of the Cross Validation algorithm """
def cvFold(classifier, l1_features, l2_features, l1_cutoff, l2_cutoff, folds, i):

	# Calculating the required indices to split the features
	index1 = (folds - i - 1) * l1_cutoff
	index2 = (folds - i) * l1_cutoff
	index3 = (folds - i - 1) * l2_cutoff
	index4 = (folds - i) * l2_cutoff

	# Splitting the list of features into both train and test sets
	test_features = l1_features[index1:index2] + l2_features[index3:index4]

	train_features = l1_features[:index1] + l1_features[index2:] + \
					 l2_features[:index3] + l2_features[index4:]

	result = util.accuracy(classifier.train(train_features), test_features)
	print("Fold", i+1, "accuracy rate is", round(result, 4))

	return result




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
