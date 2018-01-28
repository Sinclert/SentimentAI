# Created by Sinclert Perez (Sinclert@hotmail.com)


import json
import os
import pickle


project_paths = {
	'datasets': ['resources', 'datasets'],
	'models': ['models'],
	'profile_t': ['profiles', 'training'],
	'profile_p': ['profiles', 'predicting'],
	'stopwords': ['resources', 'stopwords'],
}




def get_abs_path(file_name, file_type):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_name:
			type: string
			info: desired file name

		file_type:
			type: string
			info: used to determine the proper path

	Returns:
	----------
		lines:
			type: string
			info: absolute path to the desired file
	"""

	try:
		project_root = str(os.path.dirname(os.getcwd()))

		path = [project_root]
		path = path + project_paths[file_type]
		path = path + file_name

		return os.path.join(*path)

	except KeyError:
		exit('The file type "' + file_type + '" is not defined')





def get_file_lines(file_name, file_type):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_name:
			type: string
			info: readable file name

		file_type:
			type: string
			info: used to determine the proper path

	Returns:
	----------
		lines:
			type: list
			info: file lines (separated by the new line character)
	"""

	file_path = get_abs_path(file_name, file_type)

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		lines = file.read().splitlines()
		file.close()

		return lines

	except IOError:
		exit('The file ' + file_name + ' cannot be opened')




def get_file_json(file_name, file_type):

	""" Reads the lines of a file and returns them inside a list

	Arguments:
	----------
		file_name:
			type: string
			info: readable file name

		file_type:
			type: string
			info: used to determine the proper path

	Returns:
	----------
		json_dict:
			type: dict
			info: dictionary containing the parsed JSON file
	"""

	file_path = get_abs_path(file_name, file_type)

	try:
		file = open(file_path, 'r', encoding = 'utf-8')
		json_dict = json.load(file)
		file.close()

		return json_dict

	except IOError:
		exit('The file ' + file_name + ' cannot be opened')




def load_object(file_name, file_type):

	""" Loads an object from the specified file

	Arguments:
		----------
		file_name:
			type: string
			info: saved object file name

		file_type:
			type: string
			info: used to determine the proper path

	Returns:
	----------
		obj:
			type: dict
			info: dictionary containing the object information
	"""

	file_path = get_abs_path(file_name, file_type)

	try:
		file = open(file_path, 'rb')
		obj = pickle.load(file)
		file.close()

		return obj

	except IOError:
		exit('The object could not be loaded from ' + file_path)




def save_object(obj, file_name, file_type):

	""" Saves an object in the specified path

	Arguments:
	----------
		obj:
			type: object
			info: instance of a class that will be serialized

		file_name:
			type: string
			info: saved object file name

		file_type:
			type: string
			info: used to determine the proper path
	"""

	file_path = get_abs_path(file_name, file_type)
	os.makedirs(file_path, exist_ok = True)

	try:
		file = open(file_path, 'wb')
		pickle.dump(obj.__dict__, file)
		file.close()

	except IOError:
		exit('The object could not be saved in ' + file_path)




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
