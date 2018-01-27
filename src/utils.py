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
    },
	{
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

	Arguments:
	----------
		text:
		    type: string
		    info: text where the regex substitutions will be applied

		filters:
		    type: list
		    info: list containing dictionaries with the following keys:
		        1. pattern (regular expression)
				2. replace (string)

	Returns:
	----------
		text:
			type: string
			info: lowercase cleaned text
	"""

	for f in filters:
		text = re.sub(f['pattern'], f['replace'], text)

	text = text.lower()
	text = text.strip()
	return text




def draw_pie_chart(i, labels, colors, counters, title):

	""" Draws a pie chart

	Arguments:
	----------
		i:
			type: int (not used)
			info: animator function frame index

		labels:
			type: list
			info: pie slices ordered labels

		colors:
			type: list
			info: pie slices ordered hexadecimal colors

		counters:
			type: list
			info: pie slices proportions

		title:
			type: string
			info: pie chart title
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

	""" Filters the text sentences given a word

	Arguments:
	----------
		text:
			type: string (lowercase)
			info: text which may have several sentences

		word:
			type: string (lowercase)
			info: string which is going to be used to filter

	Returns:
	----------
		text:
			type: string
			info: text containing the sentences in which the word is present
	"""

	sentences = re.split('[.:!?]\s+', text)
	sentences = filter(lambda s: word in s, sentences)

	return '. '.join(sentences)




def get_file_lines(file_path):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_path:
			type: string
			info: relative path to the readable file

	Returns:
	----------
		lines:
			type: list
			info: file lines (separated by the new line character)
	"""

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		lines = file.read().splitlines()
		file.close()

		return lines

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')




def get_file_json(file_path):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_path:
			type: string
			info: relative path to the readable file

	Returns:
	----------
		json_dict:
			type: dict
			info: dictionary containing the parsed JSON file
	"""

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		json_dict = json.load(file)
		file.close()

		return json_dict

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')




def get_tweet_text(tweet):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		tweet:
			type: dict
			info: dictionary containing all the fields of a tweet

	Returns:
	----------
		text:
			type: string
			info: original tweet text
	"""

	if tweet.get('retweeted_status'):
		tweet = tweet['retweeted_status']

	return tweet['text']




def store_texts(texts, file_path, min_length = 0):

	""" Appends the specified texts at the end of the given file

	Arguments:
	----------
		texts:
			type: list
			info: strings to be appended at the end of the file

		file_path:
			type: string
			info: relative path to the appendable file

		min_length:
			type: int (optional)
			info: minimum length to append a text to the file

	Returns:
	----------
		skipped_num:
			type: int
			info: number of text that did not fulfill the length requirement
	"""

	try:
		file = open(file_path, 'a', encoding = 'utf-8')
		skipped_num = 0

		for text in texts:

			if len(text) >= min_length:
				file.write(text + '\n')
			else:
				skipped_num += 1

		file.close()
		return skipped_num

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')
