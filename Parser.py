# Created by Sinclert Perez (Sinclert@hotmail.com)

import os
from Classifier import Classifier, possible_classifiers
from DataMiner import DataMiner
from TwitterListener import TwitterListener
from Utilities import getSentences
from argparse import ArgumentParser, RawDescriptionHelpFormatter


# Folder paths
datasets_folder = "Datasets"
models_folder = "Models"

functions = ['classify', 'search', 'stream', 'train']
labels = ['Negative', 'Neutral', 'Positive']




""" Trains and stores the specified ML algorithm after been trained """
def train(classifier_name, l1_file, l2_file, features_pct, output):

	# Checks the validity of the percentages
	if (features_pct < 0) or (features_pct > 100):
		print("ERROR: The specified percentage is invalid")
		exit()

	# Checks the specified classifier
	if classifier_name.lower() in possible_classifiers.keys():

		l1_file = os.path.join(datasets_folder, l1_file)
		l2_file = os.path.join(datasets_folder, l2_file)

		classifier = Classifier()
		classifier.train(
			classifier_name = classifier_name.lower(),
			l1_file = l1_file,
			l2_file = l2_file,
			features_pct = features_pct
		)

		classifier.saveModel(models_folder, output)

	else:
		print("ERROR: Invalid classifier")
		exit()




""" Performs sentiment analysis over the specified Twitter account """
def classify(polarity_cls, sentiment_cls, account, filter_word):

	# Loading both trained classifiers
	classifier1 = Classifier()
	classifier2 = Classifier()
	classifier1.loadModel(models_folder, polarity_cls)
	classifier2.loadModel(models_folder, sentiment_cls)

	# Obtaining tweets
	miner = DataMiner()
	tweets = miner.getUserTweets(user = account)

	# Splitting the tweets into sentences
	sentences = getSentences(
		tweets = tweets,
		word = filter_word
	)

	# Creating the results dictionary
	results = dict.fromkeys(labels, 0)

	# Storing the classification results
	for sentence in sentences:
		label = classifier1.classify(sentence)

		if label == 'Polarized':
			label = classifier2.classify(sentence)

		# In case there is no relevant features it is ignored
		if label is None:
			print(sentence, "(Tweet ignored)")
		else:
			results[label] += 1

	print(results)




""" Search tweets using Twitter API storing them into the output file """
def search(search_query, language, search_depth, output):

	# Creating the storing output final path
	output_path = os.path.join(datasets_folder, output)

	# Obtaining tweets and storing them in a file
	miner = DataMiner()
	miner.searchTweets(
		query = search_query,
		language = language,
		file = output_path,
		depth = search_depth
	)




""" Performs sentiment analysis over a stream of tweets filter by location """
def stream(polarity_cls, sentiment_cls, buffer_size, filter_word, language, coordinates):

	# Loading both trained classifiers
	classifier1 = Classifier()
	classifier2 = Classifier()
	classifier1.loadModel(models_folder, polarity_cls)
	classifier2.loadModel(models_folder, sentiment_cls)

	# Transforming arguments
	tracks = [filter_word]
	languages = [language]

	if len(coordinates) % 4 != 0:
		print("ERROR: The number of coordinates must be a multiple of 4")
		exit()


	# Creates the stream object and start stream
	listener = TwitterListener(classifier1, classifier2, buffer_size, labels)
	listener.initStream(tracks, languages, coordinates)

	from matplotlib import pyplot, animation
	from GraphAnimator import animatePieChart, figure

	# Animate the graph each milliseconds interval
	ani = animation.FuncAnimation(
		fig = figure,
		func = animatePieChart,
		interval = 500,
		fargs = (labels, tracks, listener.stream_dict)
	)
	pyplot.show()

	# Finally: close the stream process
	listener.closeStream()




""" Main method to parse the arguments and call the proper function """
if __name__ == '__main__':

	# Creating the top-level parser
	global_parser = ArgumentParser(
		usage = "Parser.py [mode] [arguments]",
		description = "modes and arguments:\n"
		              "  \n"
		              "  classify: analyses tweets of a Twitter account\n"
		              "            -p <polarity classifier>\n"
		              "            -s <sentiment classifier>\n"
		              "            -a <Twitter account>\n"
		              "            -w <filter word>\n"
		              "  \n"
		              "  search: stores query tweets into a new dataset\n"
		              "            -q <query>\n"
		              "            -l <language>\n"
		              "            -d <search depth>\n"
		              "            -o <dataset output>\n"
		              "  \n"
		              "  stream: analyses tweets of a Twitter stream\n"
		              "            -p <polarity classifier>\n"
		              "            -s <sentiment classifier>\n"
		              "            -b <buffer size>\n"
		              "            -w <filter word>\n"
		              "            -l <language>\n"
		              "            -c <coord 1> <coord 2> <coord 3> <coord 4>\n"
		              "  \n"
		              "  train: trains and store the specified ML model\n"
		              "            -n <classifier name>\n"
		              "            -d <first dataset> <second dataset>\n"
		              "            -f <features percentage>\n"
		              "            -o <output name>\n",
		formatter_class = RawDescriptionHelpFormatter)


	# Parsing the arguments in order to check the mode
	global_parser.add_argument('mode', choices = functions)
	arg, func_args = global_parser.parse_known_args()


	# First mode: classify
	if arg.mode == "classify":

		classify_par = ArgumentParser(usage = "Use 'Parser.py -h' for help")
		classify_par.add_argument('-p', required = True)
		classify_par.add_argument('-s', required = True)
		classify_par.add_argument('-a', required = True)
		classify_par.add_argument('-w', required = True)

		args = classify_par.parse_args(func_args)
		classify(args.p, args.s, args.a, args.w)


	# Second mode: search
	elif arg.mode == "search":

		search_par = ArgumentParser(usage = "Use 'Parser.py -h' for help")
		search_par.add_argument('-q', required = True)
		search_par.add_argument('-l', required = True)
		search_par.add_argument('-d', required = True, type = int)
		search_par.add_argument('-o', required = True)

		args = search_par.parse_args(func_args)
		search(args.q, args.l, args.d, args.o)


	# Third mode: stream
	elif arg.mode == "stream":

		stream_par = ArgumentParser(usage = "Use 'Parser.py -h' for help")
		stream_par.add_argument('-p', required = True)
		stream_par.add_argument('-s', required = True)
		stream_par.add_argument('-b', required = True, type = int)
		stream_par.add_argument('-w', required = True)
		stream_par.add_argument('-l', required = True)
		stream_par.add_argument('-c', required = True, type = float, nargs = '+')

		args = stream_par.parse_args(func_args)
		stream(args.p, args.s, args.b, args.w, args.l, args.c)


	# Fourth mode: train
	elif arg.mode == "train":

		train_par = ArgumentParser(usage = "Use 'Parser.py -h' for help")
		train_par.add_argument('-n', required = True)
		train_par.add_argument('-d', required = True, nargs = 2)
		train_par.add_argument('-f', required = True, type = float)
		train_par.add_argument('-o', required = True)

		args = train_par.parse_args(func_args)
		train(args.n, args.d[0], args.d[1], args.f, args.o)
