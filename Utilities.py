# Created by Sinclert Perez (Sinclert@hotmail.com)

import math, re
from nltk.classify import util
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures as BAM
from multiprocessing import Pool, cpu_count
from functools import partial


################ FILTERS ################
emoji_filter  = re.compile(u'['
                             u'\U00002600-\U000027B0'
                             u'\U0001F300-\U0001F64F'
                             u'\U0001F680-\U0001F6FF'
                             u'\U0001F910-\U0001F919]+',
                             re.UNICODE)

spaces_filter = re.compile('\s+')

user_filter = re.compile('(^|\s+)@\w+')




""" Give score to every element taking into account the gain of information """
def getScores(l1_elements, l2_elements):

	# Build frequency and conditional distribution within the possible labels
	freqDist = FreqDist()
	conditional_freqDist = ConditionalFreqDist()

	for element in l1_elements:
		freqDist[element] += 1
		conditional_freqDist['label1'][element] += 1

	for element in l2_elements:
		freqDist[element] += 1
		conditional_freqDist['label2'][element] += 1

	# Counts the number of positive and negative words, as well as the total number of them
	l1_count = conditional_freqDist['label1'].N()
	l2_count = conditional_freqDist['label2'].N()
	total_count = l1_count + l2_count


	scores = {}

	# Builds a dictionary of scores based on chi-squared test
	for elem, freq in freqDist.items():
		l1_score = BAM.chi_sq(conditional_freqDist['label1'][elem], (freq, l1_count), total_count)
		l2_score = BAM.chi_sq(conditional_freqDist['label2'][elem], (freq, l2_count), total_count)
		scores[elem] = l1_score + l2_score

	return scores




""" Finds the best 'n' elements based on their scores """
def getBestElements(scores, number):
	best_values = sorted(scores.items(), key = lambda element: element[1], reverse = True)[:number]
	best_elements = set([w for w, s in best_values])

	return best_elements




""" Returns the tweet text as a common sentence after applying some filters """
def getCleanTweet(tweet):
	tweet = tweet.replace("#", "")
	tweet = emoji_filter.sub("", tweet)
	tweet = spaces_filter.sub(" ", tweet)

	return tweet




""" Divides tweets into sentences and returns those containing the specified word """
def getSentences(tweets, word = None):

	# If there is a list of tweets as input
	if isinstance(tweets, list):
		sentences = []

		for tweet in tweets:

			# Recursive call to obtain the sentences of each individual tweet
			for sentence in getSentences(tweet, word):
				sentences.append(sentence)

	# Base case: individual tweet
	elif isinstance(tweets, str):
		sentences = re.split("[.:!?]\s+", str(tweets))

		if word is not None:
			sentences[:] = [sentence for sentence in sentences if word.lower() in sentence.lower()]

	# If what we are processing is neither a list nor a string: error
	else:
		print("ERROR: Invalid value in one of the text inputs")
		exit()

	return sentences




""" Tests the specified classifier applying cross validation """
def crossValidation(classifier, l1_features, l2_features, folds = 10):

	if folds > 1:

		# Calculating cut offs in both features lists
		l1_cutoff = math.floor(len(l1_features) / folds)
		l2_cutoff = math.floor(len(l2_features) / folds)

		func = partial(crossValidationFold, classifier, l1_features, l1_cutoff, l2_features, l2_cutoff, folds)

		# Creating the pool of processes and mapping them to the number of iterations
		processes = Pool(cpu_count())
		processes_output = processes.map(func = func, iterable = range(folds))

		return round((sum(processes_output) / folds), 4)

	else:
		print("ERROR: The number of cross validation folds must be greater than 1")
		exit()




""" Perfoms a single iteration of the Cross Validation algorithm """
def crossValidationFold(classifier, l1_features, l1_cutoff, l2_features, l2_cutoff, folds, i):

	test_features = l1_features[((folds - i - 1) * l1_cutoff):((folds - i) * l1_cutoff)] + \
					l2_features[((folds - i - 1) * l2_cutoff):((folds - i) * l2_cutoff)]

	train_features = [feature for feature in (l1_features + l2_features) if feature not in test_features]

	model = classifier.train(train_features)
	return util.accuracy(model, test_features)




""" Appends the specified tweets at the end of a text file """
def storeTweets(tweets, file_name, min_length = 30):

	# If there is a list of tweets as input
	if isinstance(tweets, list):
		for tweet in tweets:
			storeTweets(tweet, file_name)

		print("Tweets stored into '", file_name, "'")

	# Base case: individual tweet
	elif isinstance(tweets, str):
		file = open(file_name, 'a', encoding = "UTF8")

		# Subtracting user names before storing
		tweets = user_filter.sub(" USER", tweets)
		tweets = tweets.strip()

		# Store the tweet only if it has enough length
		if len(tweets) >= min_length:
			file.write(tweets)
			file.write("\n")

		file.close()

	# If what we are processing is neither a list nor a string: error
	else:
		print("ERROR: Invalid value in one of the text inputs")
		exit()
