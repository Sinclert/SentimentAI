# Created by Sinclert Perez (Sinclert@hotmail.com)

from typing import Union

from clf_node import NodeClassif

from utils import read_json
from utils import check_keys




class HierarchicalClassif(object):

	""" Represents a hierarchical classification tree

	Attributes:
	----------
		keys:
			type: list
			info: required keys in each JSON tree node

		tree:
			type: dict
			info: tree structure in which each node has:
				- clf_file (string)
				- clf_object (NodeClassif)
				- clf_children (dict)

		colors:
			type: dict
			info: RGB color (value) of each label (key)
	"""


	# Required JSON node keys (class attribute)
	keys = ['clf_file', 'clf_object', 'clf_children']




	def __init__(self, profile: str):

		""" Loads the JSON profile models into the tree attribute

		Arguments:
		----------
			profile: JSON predicting profile file name

		"""

		profile = read_json(
			file_name = profile,
			file_type = 'profile_p'
		)

		# Checking that the JSON structure is a dict
		assert isinstance(profile, dict)

		try:
			self.tree = profile['tree']
			self.colors = profile['colors']
			self.__load_clf(self.tree)

		except KeyError:
			exit('Invalid JSON keys')




	def __load_clf(self, node: dict):

		""" Recursively check and load classifier objects into 'clf_object'

		Arguments:
		----------
			node: current tree node to load the 'clf_file' classifier

		"""

		check_keys(
			data_keys = self.keys,
			data_struct = node,
			error = 'Invalid JSON keys'
		)

		node['clf_object'] = NodeClassif(node['clf_file'])

		try:
			clf_labels = node['clf_object'].get_labels()
			clf_child_names = node['clf_children'].keys()
			clf_child_nodes = node['clf_children'].values()

			check_keys(
				data_keys = clf_child_names,
				data_struct = clf_labels,
				error = 'Invalid JSON keys'
			)

			for child_node in clf_child_nodes:
				self.__load_clf(child_node)

		except AttributeError:
			exit('Invalid JSON values')




	def get_labels(self) -> list:

		""" Gets the label names

		Returns:
		----------
			labels: labels names

		"""

		try:
			return self.colors.keys()
		except AttributeError:
			exit('Invalid JSON labels structure')




	def get_colors(self) -> list:

		""" Gets the label colors

		Returns:
		----------
			colors: labels associated colors

		"""

		try:
			return self.colors.values()
		except AttributeError:
			exit('Invalid JSON labels structure')




	def predict(self, sentence: str) -> Union[str, None]:

		""" Predicts the label of a sentence using the loaded classifiers

		Arguments:
		----------
			sentence: text to classify

		Returns:
		----------
			label: predicted sentence label

		"""

		node = self.tree
		label = node['clf_object'].predict(sentence)

		while label in node['clf_children'].keys():
			node = node['clf_children'][label]
			label = node['clf_object'].predict(sentence)

		if label is None:
			print(sentence, '(Unknown label)')

		return label
