# Created by Sinclert Perez (Sinclert@hotmail.com)


import json
import re

from matplotlib import pyplot


cleaning_filters = [
    {
        'pattern': 'http\S+',
        'replace': ''
    },
    {
        'pattern': '#',
        'replace': ''
    },{
        'pattern': '&\w+;',
        'replace': ''
    },
    {
        'pattern':
            '[\U00002600-\U000027B0'
            '\U0001F300-\U0001F64F'
            '\U0001F680-\U0001F6FF'
            '\U0001F910-\U0001F919]+',
        'replace': ''
    },
    {
        'pattern': '\s+',
        'replace': ' '
    },
]




def clean_text(text, filters = cleaning_filters):

	""" Cleans the text applying regex substitution specified by the filters

	Arguments
	---------
	text : string
		text in which the regex substitutions are going to be applied

	filters : list (optional)
		list containing dictionaries with the following keys:

		- pattern : regular expression
		- replace : string

	Returns
	---------
	text : string
		lowercase cleaned text
	"""

	for f in filters:
		text = re.sub(f['pattern'], f['replace'], text)

	text = text.lower()
	text = text.strip()
	return text




def draw_pie_chart(i, labels, colors, counters, title):

	""" Draws a pie chart

	Arguments
	---------
	i : int (not used)
		frame index indicated by the animator function

	labels : list
		labels in which the pie is going to be split

	colors: list
		hexadecimal colors in which the slices will be painted

	counters: list
		numerical values to indicate pie slices proportions

	title: string
		pie chart title
	"""

	try:

		# In case there is data to show
		if sum(counters) > 0:
			pyplot.figure().clear()

			pyplot.title(title)
			pyplot.pie(
				explode = counters,
				labels = labels,
				colors = colors
			)

	except BrokenPipeError:
		exit('The communication between threads was cut')




def filter_text(text, word):

	""" Filters the received text by returning sentences containing the word

	Arguments
	---------
	text : string (lowercase)
		text which may have several sentences

	word : string (lowercase)
		string which is going to be used to filter the text sentences

	Returns
	---------
	filtered_text : string
		text containing the sentences in which the word is present
	"""

	sentences = re.split('[.:!?]\s+', text)
	sentences = filter(lambda s: word in s, sentences)

	return '. '.join(sentences)




def get_file_lines(file_path):

	""" Reads the lines of a file and returns them inside a list

	Arguments
	---------
	file_path : string
		path to the readable file

	Returns
	---------
	lines : list
		lines of the file separated by the new line character
	"""

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		lines = file.read().splitlines()
		file.close()

		return lines

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')




def get_file_json(file_path):

	""" Reads a JSON file and returns it as a dictionary

	Arguments
	---------
	file_path : string
		path to the readable file

	Returns
	---------
	json_dict : dict
		dictionary containing the parsed JSON file
	"""

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		json_dict = json.load(file)
		file.close()

		return json_dict

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')




def get_tweet_text(tweet):

	""" Extracts the text from a tweet object (dictionary)

	Arguments
	---------
	tweet : dictionary
		dict object containing all the fields of a tweet

	Returns
	---------
	text : string
		original tweet text
	"""

	if tweet.get('retweeted_status'):
		tweet = tweet['retweeted_status']

	return tweet['text']




def store_texts(texts, file_path, min_length = 0):

	""" Appends the specified texts at the end of the given file

	Arguments
	---------
	texts : list
		contains the strings to be appended at the end of the file

	file_path : string
		path to the appendable file

	min_length : int (optional)
		minimum length to append a text to the file

	Returns
	---------
	num_of_skips : int
		number of text that did not fulfill the length requirement
	"""

	try:
		file = open(file_path, 'a', encoding = 'utf-8')
		num_of_skips = 0

		for text in texts:

			if len(text) >= min_length:
				file.write(text + '\n')
			else:
				num_of_skips += 1

		file.close()
		return num_of_skips

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')
