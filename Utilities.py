# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re
from nltk.probability import FreqDist, ConditionalFreqDist
from nltk.metrics import BigramAssocMeasures as BAM


# Indicates tweets confidence percentage
confidence_threshold = 0.10


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
def getScores(pos_elements, neg_elements):

	# Build frequency and conditional distribution within the positive and negative labels
	freqDist = FreqDist()
	conditional_freqDist = ConditionalFreqDist()

	for element in pos_elements:
		freqDist[element] += 1
		conditional_freqDist['pos'][element] += 1

	for element in neg_elements:
		freqDist[element] += 1
		conditional_freqDist['neg'][element] += 1

	# Counts the number of positive and negative words, as well as the total number of them
	pos_count = conditional_freqDist['pos'].N()
	neg_count = conditional_freqDist['neg'].N()
	total_count = pos_count + neg_count


	scores = {}

	# Builds a dictionary of scores based on chi-squared test
	for elem, freq in freqDist.items():
		pos_score = BAM.chi_sq(conditional_freqDist['pos'][elem], (freq, pos_count), total_count)
		neg_score = BAM.chi_sq(conditional_freqDist['neg'][elem], (freq, neg_count), total_count)
		scores[elem] = pos_score + neg_score

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

	sentences = []

	# If there is a list of tweets as input
	if isinstance(tweets, list):
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




""" Gets the polarity of several probability pairs by calculating the averages """
def getPolarity(classifications):

	if len(classifications) > 0:

		# If the input list contains probabilities
		if isinstance(classifications[0], dict):

			# Calculating the positive average is enough
			pos_average = 0

			for prob_pair in classifications:
				pos_average += prob_pair['Positive']

			pos_average /= len(classifications)


			# CONFIDENCE THRESHOLD APPLICATION
			outliers = int(len(classifications) * confidence_threshold)

			# If there are outliers: they are subtracted from the mean
			if outliers > 0:

				differences = []
				for prob_pair in classifications:
					differences.append([prob_pair['Positive'], abs(pos_average - prob_pair['Positive'])])

				differences.sort(key = lambda element: element[1], reverse = True)
				pos_average *= len(classifications)

				for i in range(0, outliers):
					pos_average -= differences[i][0]

				pos_average /= (len(classifications) - outliers)


			# Finally: label classification result
			if pos_average >= 0.5:
				return ['Positive', round(pos_average, 2)]
			else:
				return ['Negative', round(1 - pos_average, 2)]


		# If the input list does not contain probabilities
		else:
			pos_counter = 0

			for classification in classifications:
				if classification == 'pos':
					pos_counter += 1

			# Finally: label classification result
			if pos_counter >= (len(classifications) - pos_counter):
				return ['Positive', str(pos_counter) + ":" + str(len(classifications) - pos_counter)]
			else:
				return ['Negative', str(pos_counter) +":" + str(len(classifications) - pos_counter)]


	# In case of an empty list: return None
	else:
		print("The input probabilities list is empty")
		return None




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
