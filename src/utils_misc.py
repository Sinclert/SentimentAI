# Created by Sinclert Perez (Sinclert@hotmail.com)


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




def check_keys(keys, data_struct, error):

	""" Checks if all the keys are present in the data structure

	Arguments:
	----------
		keys:
			type: list
			info: elements which must be in the data structure

		data_struct:
			type: set / dictionary
			info: data structure to check existence

		error:
			type: string
			info: error message to print
	"""

	if not all(k in data_struct for k in keys):
		exit(error)




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




def get_tweet_text(tweet):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		tweet:
			type: Status object
			info: contains all the attributes of a tweet

	Returns:
	----------
		text:
			type: string
			info: original tweet text
	"""

	if hasattr(tweet, 'retweeted_status'):
		tweet = tweet.retweeted_status

	try:
		return tweet.full_text
	except AttributeError:
		return tweet.text
