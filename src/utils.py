# Created by Sinclert Perez (Sinclert@hotmail.com)


import json
import os
import pickle
import random
import re

from typing import Union


project_paths = {
	'dataset': ['resources', 'datasets'],
	'model': ['models'],
	'profile_p': ['profiles', 'predicting'],
	'profile_t': ['profiles', 'training'],
	'stopwords': ['resources', 'stopwords']
}


default_filters = [
	{
		'pattern': 'http\S+',
		'replace': '',
		'prob': 100
	},
	{
		'pattern': '(^|\s)@\w+',
		'replace': ' -USER-',
		'prob': 100
	},
	{
		'pattern': '#',
		'replace': '',
		'prob': 100
	},
	{
		'pattern': '&\w+;',
		'replace': '',
		'prob': 100
	},
	{
		'pattern':
			'[\U00002600-\U000027B0'
			'\U0001F300-\U0001F64F'
			'\U0001F680-\U0001F6FF'
			'\U0001F910-\U0001F919]+',
		'replace': '',
		'prob': 100
	},
	{
		'pattern': '\s+',
		'replace': ' ',
		'prob': 100
	},
]




def append_text(file_name: str, min_length: int = 0):

	""" Coroutine that appends the received text at the end of a file

	Arguments:
	----------
		file_name: appendable file name
		min_length: minimum length to append a text (optional)

	Yield:
	----------
		text: text to append in the file

	"""

	file_path = compute_path(file_name, 'dataset')

	os.makedirs(
		file_path.replace(file_name, ''),
		exist_ok = True
	)

	try:
		file = open(file_path, 'a', encoding = 'utf-8')

		try:
			while True:
				text = yield
				if len(text) >= min_length: file.write(text + '\n')

		finally:
			file.close()

	except IOError:
		exit('The file ' + file_path + ' cannot be opened')




def build_filters(words: iter, words_prob: int) -> list:

	""" Builds a list of probabilistic filters

	Arguments:
	----------
		words: what to subtract given a probability
		words_prob: probability percentage to remove words (optional)

	Returns:
	----------
		filters: list containing the probabilistic filters

	"""

	prob_filters = []

	for word in words:
		prob_filters.append({
			'pattern': '(^|\s)' + word + '(\W|$)',
			'replace': ' ',
			'prob': words_prob
		})

	return prob_filters




def check_keys(data_keys: list, data_struct: dict, error: str):

	""" Checks if all the keys are present in the data structure

	Arguments:
	----------
		data_keys: elements which must be in the data structure
		data_struct: dict to check existence
		error: message to print

	"""

	if not all(k in data_struct for k in data_keys):
		exit(error)




def clean_text(text: str, filters: list = default_filters) -> str:

	""" Cleans the text applying regex substitution specified by the filters

	Arguments:
	----------
		text: lowercase text where the regex substitutions will be applied
		filters: list containing dictionaries with the following keys (optional):
			- pattern (regex)
			- replace (string)
			- prob (int)

	Returns:
	----------
		text: lowercase cleaned text

	"""

	try:
		for f in filters:

			# In case the replacement must be performed
			if (f['prob'] == 100) or ((random.random() * 100) < f['prob']):
				text = re.sub(f['pattern'], f['replace'], text)

		return text.strip()

	except KeyError:
		exit('The filters do not have the correct format')




def compute_path(file_name: str, file_type: str) -> str:

	""" Builds the absolute path to the desired file given its file type

	Arguments:
	----------
		file_name: desired file name
		file_type: {'dataset', 'model', 'profile_p', 'profile_t', 'stopwords'}

	Returns:
	----------
		path: absolute path to the desired file

	"""

	try:
		project_root = str(os.path.dirname(os.getcwd()))

		path = [project_root]
		path = path + project_paths[file_type]
		path = path + [file_name]

		return os.path.join(*path)

	except KeyError:
		exit('The file type "' + file_type + '" is not defined')




def load_object(file_name: str, file_type: str) -> dict:

	""" Loads an object from the specified file

	Arguments:
	----------
		file_name: saved object file name
		file_type: used to determine the proper path

	Returns:
	----------
		obj: dictionary containing the object information

	"""

	file_path = compute_path(file_name, file_type)

	try:
		file = open(file_path, 'rb')
		obj = pickle.load(file)
		file.close()

		return obj

	except IOError:
		exit('The object could not be loaded from ' + file_path)




def save_object(obj: object, file_name: str, file_type: str):

	""" Saves an object in the specified path

	Arguments:
	----------
		obj: instance of a class that will be serialized
		file_name: saved object file name
		file_type: used to determine the proper path

	"""

	file_path = compute_path(file_name, file_type)

	os.makedirs(
		file_path.replace(file_name, ''),
		exist_ok = True
	)

	try:
		file = open(file_path, 'wb')
		pickle.dump(obj.__dict__, file)
		file.close()

	except IOError:
		exit('The object could not be saved in ' + file_path)




def read_json(file_name: str, file_type: str) -> Union[dict, list]:

	""" Reads a JSON file and returns it as a dictionary

	Arguments:
	----------
		file_name: readable file name
		file_type: used to determine the proper path

	Returns:
	----------
		json_dict: dictionary containing the parsed JSON file

	"""

	file_path = compute_path(file_name, file_type)

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		json_dict = json.load(file)
		file.close()

		return json_dict

	except IOError:
		exit('The file ' + file_name + ' cannot be opened')




def read_lines(file_name: str, file_type: str) -> list:

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_name: readable file name
		file_type: used to determine the proper path

	Returns:
	----------
		lines: file lines (separated by the new line character)

	"""

	file_path = compute_path(file_name, file_type)

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		lines = file.read().splitlines()
		file.close()

		return lines

	except IOError:
		exit('The file ' + file_name + ' cannot be opened')
