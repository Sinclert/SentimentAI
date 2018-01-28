# Created by Sinclert Perez (Sinclert@hotmail.com)


import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from collections import Counter

from clf_node import NodeClassif
from clf_hierarchy import HierarchicalClassif
from twitter_miner import TwitterMiner
from twitter_stream import TwitterListener

from twitter_keys import USER_KEYS as U_K

from utils import draw_pie_chart
from utils import filter_text
from utils import get_file_json
from utils import save_object
from utils import store_texts


# Default outputs folders
datasets_folder = "datasets"
models_folder = "models"

# Default function names
functions = [
	'classif_train',
	'miner_predict',
	'miner_search',
	'stream_predict'
]




def classif_train(algorithm, feats_pct, lang, output, profile_path):

	""" Prepares arguments to train and saves a NodeClassif object

	Arguments:
	----------
		algorithm:
			type: string
			info: name of the algorithm to train

		feats_pct:
			type: int
			info: percentage of features to keep

		lang:
			type: string
			info: language to perform the tokenizer process

		output:
			type: string
			info: output file name including extension

		profile_path:
			type: string
			info: relative path to the JSON profile file
	"""

	if (feats_pct < 0) or (feats_pct > 100):
		exit('The specified features percentage is invalid')

	profile_data = get_file_json(profile_path)

	node_classif = NodeClassif()
	node_classif.train(
		algorithm = algorithm.lower(),
		feats_pct = feats_pct,
		lang = lang,
		profile_data = profile_data
	)

	abs_path = os.path.join(models_folder, output)
	save_object(node_classif, abs_path)




def miner_predict(user, filter_word, profile_path):

	""" Prepares arguments to predict Twitter account tweets labels

	Arguments:
	----------
		user:
			type: string
			info: Twitter user account without the '@'

		filter_word:
			type: string
			info: word applied to filter all tweets sentences

		profile_path:
			type: string
			info: relative path to the JSON profile file
	"""

	h_clf = HierarchicalClassif(profile_path)

	miner = TwitterMiner(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret']
	)

	tweets = miner.get_user_tweets(user)
	results = Counter()

	for tweet in tweets:
		tweet = filter_text(tweet, filter_word)
		label = h_clf.predict(tweet)
		if label is not None: results[label] += 1

	print(results)




def miner_search(query, lang, depth, output):

	""" Prepares arguments to search tweets and save them in a file

	Arguments:
	----------
		query:
			type: string
			info: string with logic operations (AND, OR...)

		lang:
			type: string
			info: language abbreviation to filter the tweets

		depth:
			type: int
			info: number of tweets to retrieve

		output:
			type: string
			info: output file name including extension
	"""

	miner = TwitterMiner(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret']
	)

	miner.search_tweets(
		query = query,
		lang = lang,
		depth = depth
	)

	abs_path = os.path.join(datasets_folder, output)
	store_texts([], abs_path) # TODO




def stream_predict(buffer_size, tracks, langs, coordinates, profile_path):

	""" Prepares arguments to predict Twitter stream tweets labels

	Arguments:
	----------
		buffer_size:
			type: int
			info: size of the labels circular buffer

		tracks:
		    type: string
			info: words to filter

		langs:
		    type: string
		    info: language codes to filter

		coordinates
		    type: string
		    info: groups of 4 coordinates to filter, where:
		        1. South-West longitude
		        2. South-West latitude
		        3. North-East longitude
		        4. North-East latitude

		profile_path:
			type: string
			info: relative path to the JSON profile file
	"""

	h_cls = HierarchicalClassif(profile_path)

	listener = TwitterListener(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret'],
		buffer_size = buffer_size,
		clf = h_cls
	)

	# Start the Twitter stream
	tracks = tracks.split(', ')
	langs = langs.split(', ')
	listener.start_stream(tracks, langs, coordinates)


	from matplotlib import pyplot, animation

	# Animate the graph each milliseconds interval
	# ani = animation.FuncAnimation(
	# 	fig = figure,
	# 	func = draw_pie_chart,
	# 	interval = 500,
	# 	fargs = (labels, tracks, listener.stream_dict)
	# )
	# pyplot.show()

	listener.finish_stream()




if __name__ == '__main__':

	global_parser = ArgumentParser(
		usage = 'main.py [mode] [arguments]',
		description =
			'modes and arguments:\n'
		    '  \n'
		    '  classif_train: trains and store the specified ML alg\n'
		    '            -a <algorithm name>\n'
		    '            -f <features percentage>\n'
		    '            -l <language>\n'
		    '            -o <output name>\n'
			'            -p <training profile path>\n'
			'  \n'
		    '  miner_predict: analyses tweets of a Twitter account\n'
		    '            -u <Twitter user>\n'
		    '            -w <filter word>\n'
		    '            -p <predicting profile path>\n'
		    '  \n'
		    '  miner_search: stores query tweets into a new dataset\n'
		    '            -q <search query>\n'
		    '            -l <language code>\n'
		    '            -d <search depth>\n'
		    '            -o <output name>\n'
		    '  \n'
		    '  stream_predict: analyses tweets of a Twitter stream\n'
		    '            -s <buffer size>\n'
		    '            -t <filter tracks>\n'
		    '            -l <language codes>\n'
		    '            -c <coord 1> <coord 2> <coord 3> <coord 4>\n'
			'            -p <predicting profile path>\n',
		formatter_class = RawDescriptionHelpFormatter
	)

	# Parsing the arguments in order to check the mode
	global_parser.add_argument('mode', choices = functions)
	arg, func_args = global_parser.parse_known_args()


	if arg.mode == 'classif_train':

		train_par = ArgumentParser(usage = "Use 'main.py -h' for help")
		train_par.add_argument('-a', required = True)
		train_par.add_argument('-f', required = True, type = int)
		train_par.add_argument('-l', required = True)
		train_par.add_argument('-o', required = True)
		train_par.add_argument('-p', required = True)

		args = train_par.parse_args(func_args)
		classif_train(args.a, args.f, args.l, args.o, args.p)


	elif arg.mode == 'miner_predict':

		classify_par = ArgumentParser(usage = "Use 'main.py -h' for help")
		classify_par.add_argument('-u', required = True)
		classify_par.add_argument('-w', required = True)
		classify_par.add_argument('-p', required = True)

		args = classify_par.parse_args(func_args)
		miner_predict(args.u, args.w, args.p)


	elif arg.mode == 'miner_search':

		search_par = ArgumentParser(usage = "Use 'main.py -h' for help")
		search_par.add_argument('-q', required = True)
		search_par.add_argument('-l', required = True)
		search_par.add_argument('-d', required = True, type = int)
		search_par.add_argument('-o', required = True)

		args = search_par.parse_args(func_args)
		miner_search(args.q, args.l, args.d, args.o)


	elif arg.mode == 'stream_predict':

		stream_par = ArgumentParser(usage = "Use 'main.py -h' for help")
		stream_par.add_argument('-s', required = True, type = int)
		stream_par.add_argument('-t', required = True)
		stream_par.add_argument('-l', required = True)
		stream_par.add_argument('-c', required = True, type = float, nargs = '+')
		stream_par.add_argument('-p', required = True)

		args = stream_par.parse_args(func_args)
		stream_predict(args.s, args.t, args.l, args.c, args.p)
