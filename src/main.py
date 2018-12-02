# Created by Sinclert Perez (Sinclert@hotmail.com)


from argparse import ArgumentParser as Parser
from argparse import RawDescriptionHelpFormatter
from collections import Counter

from clf_node import NodeClassif
from clf_hierarchy import HierarchicalClassif

from figures import FiguresDrawer

from twitter_miner import TwitterMiner
from twitter_stream import TwitterListener
from twitter_keys import USER_KEYS as U_K

from utils import append_text
from utils import read_json
from utils import save_object


# Default CLI modes
modes = (
	'train_model',
	'search_data',
	'predict_user',
	'predict_stream',
)




def train_model(algorithm: str, feats_pct: int, lang: str, output: str, profile: str):

	""" Prepares arguments to train and saves a NodeClassif object

	Arguments:
	----------
		algorithm: name of the algorithm to train
		feats_pct: percentage of features to keep
		lang: language to perform the tokenizer process
		output: output file name including extension
		profile: JSON training profile file name

	"""

	if (feats_pct < 0) or (feats_pct > 100):
		exit('The specified features percentage is invalid')

	profile_data = read_json(
		file_name = profile,
		file_type = 'profile_t'
	)

	node_classif = NodeClassif(
		algorithm = algorithm.lower(),
		feats_pct = feats_pct,
		lang = lang,
	)

	node_classif.train(profile_data)
	save_object(node_classif, output, 'model')




def search_data(query: str, lang: str, depth: int, output: str):

	""" Prepares arguments to search tweets and save them in a file

	Arguments:
	----------
		query: string with logic operations (AND, OR...)
		lang: language abbreviation to filter the tweets
		depth: number of tweets to retrieve
		output: output file name including extension

	"""

	miner = TwitterMiner(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret']
	)

	text_producer = miner.search_tweets(
		query = query,
		lang = lang,
		depth = depth
	)

	text_consumer = append_text(output)
	next(text_consumer)

	for text in text_producer:
		text_consumer.send(text)

	text_consumer.close()




def predict_user(user_id: str, filter_word: str, profile: str):

	""" Prepares arguments to predict Twitter account tweets labels

	Arguments:
	----------
		user_id: Twitter user account without the '@'
		filter_word: word applied to filter all tweets sentences
		profile: JSON profile file name

	"""

	h_clf = HierarchicalClassif(profile)

	miner = TwitterMiner(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret']
	)

	tweets = miner.get_user_tweets(
		user = user_id,
		word = filter_word.lower()
	)

	results = Counter()

	for tweet in tweets:
		label = h_clf.predict(tweet)
		if label is not None: results[label] += 1

	FiguresDrawer.draw_pie(
		counter = results,
		labels = h_clf.get_labels(),
		colors = h_clf.get_colors(),
		title = user_id + ' on ' + filter_word
	)




def predict_stream(buffer_size: int, tracks: str, langs: str, coords: list, profile: str):

	""" Prepares arguments to predict Twitter stream tweets labels

	Arguments:
	----------
		buffer_size: labels circular buffer size
		tracks: words to filter
		langs: language codes to filter

		coords: list with multiples of 4 coordinates, where:
			1. South-West longitude
			2. South-West latitude
			3. North-East longitude
			4. North-East latitude

		profile: JSON profile file name

	"""

	h_clf = HierarchicalClassif(profile)

	listener = TwitterListener(
		token_key = U_K['token_key'],
		token_secret = U_K['token_secret'],
		buffer_size = buffer_size,
		clf = h_clf
	)

	# Start the stream
	tracks = tracks.split(', ')
	langs = langs.split(', ')
	listener.start_stream(tracks, langs, coords)

	FiguresDrawer.animate_pie(
		counter = listener.counters,
		labels = h_clf.get_labels(),
		colors = h_clf.get_colors(),
		title = 'Stream on ' + str(tracks)
	)

	# Finish the stream when the graph is closed
	listener.finish_stream()




if __name__ == '__main__':

	global_parser = Parser(
		usage = 'main.py [mode] [arguments]',
		description =
			'modes and arguments:\n'
			'  \n'
			'  train_model: trains and store the specified ML algorithm\n'
			'			-a <algorithm name>\n'
			'			-f <features percentage>\n'
			'			-l <language>\n'
			'			-o <output name>\n'
			'			-p <training profile name>\n'
			'  \n'
			'  search_data: stores query tweets into a new dataset\n'
			'			-q <search query>\n'
			'			-l <language code>\n'
			'			-d <search depth>\n'
			'			-o <output name>\n'
			'  \n'
			'  predict_user: analyses tweets of a Twitter account\n'
			'			-u <Twitter user>\n'
			'			-w <filter word>\n'
			'			-p <predicting profile name>\n'
			'  \n'
			'  predict_stream: analyses tweets of a Twitter stream\n'
			'			-s <buffer size>\n'
			'			-t <filter tracks>\n'
			'			-l <language codes>\n'
			'			-c <coord 1> <coord 2> <coord 3> <coord 4>\n'
			'			-p <predicting profile name>\n',
		formatter_class = RawDescriptionHelpFormatter
	)

	# Parsing the arguments in order to check the mode
	global_parser.add_argument('mode', choices = modes)
	arg, func_args = global_parser.parse_known_args()


	if arg.mode == 'train_model':

		parser = Parser(usage = "Use 'main.py -h' for help")
		parser.add_argument('-a', required = True)
		parser.add_argument('-f', required = True, type = int)
		parser.add_argument('-l', required = True)
		parser.add_argument('-o', required = True)
		parser.add_argument('-p', required = True)

		args = parser.parse_args(func_args)
		train_model(args.a, args.f, args.l, args.o, args.p)


	elif arg.mode == 'search_data':

		parser = Parser(usage = "Use 'main.py -h' for help")
		parser.add_argument('-q', required = True)
		parser.add_argument('-l', required = True)
		parser.add_argument('-d', required = True, type = int)
		parser.add_argument('-o', required = True)

		args = parser.parse_args(func_args)
		search_data(args.q, args.l, args.d, args.o)


	elif arg.mode == 'predict_user':

		parser = Parser(usage = "Use 'main.py -h' for help")
		parser.add_argument('-u', required = True)
		parser.add_argument('-w', required = True)
		parser.add_argument('-p', required = True)

		args = parser.parse_args(func_args)
		predict_user(args.u, args.w, args.p)


	elif arg.mode == 'predict_stream':

		parser = Parser(usage = "Use 'main.py -h' for help")
		parser.add_argument('-s', required = True, type = int)
		parser.add_argument('-t', required = True)
		parser.add_argument('-l', required = True)
		parser.add_argument('-c', required = True, type = float, nargs = '+')
		parser.add_argument('-p', required = True)

		args = parser.parse_args(func_args)
		predict_stream(args.s, args.t, args.l, args.c, args.p)
