# Created by Sinclert Perez (Sinclert@hotmail.com)


from clf_node import NodeClassif
from utils import get_file_json




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
				- clf_name (string)
				- clf_object (NodeClassif)
				- clf_children (dict)

		labels:
			type: dict
			info: labels with their hexadecimal colors
	"""


	# Class attribute containing the required JSON nodes keys
	keys = ['clf_name', 'clf_object', 'clf_children']




	def __init__(self, profile_path):

		""" Loads the JSON profile models into the tree attribute

		Arguments:
		----------
			profile_path:
				type: string
				info: relative path to the JSON profile file
		"""

		profile = get_file_json(profile_path)

		try:
			self.tree = profile['tree']
			self.labels = profile['labels']

			self.__load_clf(self.tree)

		except KeyError:
			exit('Invalid JSON keys')




	def __load_clf(self, node):

		""" Recursively check and load classifier objects into 'clf_object'

		Arguments:
		----------
			node:
				type: dict
				info: current tree node to load the 'clf_name' classifier
		"""

		if not all(k in node for k in self.keys):
			exit('Invalid JSON keys')

		node['clf_object'] = NodeClassif(node['clf_name'])


		try:
			clf_labels = node['clf_object'].get_labels()
			clf_children_names = node['clf_children'].keys()
			clf_children_nodes = node['clf_children'].values()

			if not all(n in clf_labels for n in clf_children_names):
				exit('Invalid JSON children names')

			for child_node in clf_children_nodes:
				self.__load_clf(child_node)

		except AttributeError:
			exit('Invalid JSON values')




	def get_labels(self):

		""" Gets the label names

		Returns:
		----------
			labels:
				type: list
				info: labels names
		"""

		try:
			return self.labels.keys()
		except AttributeError:
			exit('Invalid JSON labels structure')




	def get_colors(self):

		""" Gets the label colors

		Returns:
		----------
			colors:
				type: list
				info: labels associated colors
		"""

		try:
			return self.labels.values()
		except AttributeError:
			exit('Invalid JSON labels structure')




	def predict(self, sentence):

		""" Predicts the label of a sentence using the loaded classifiers

		Arguments:
		----------
			sentence:
				type: string
				info: text to classify

		Returns:
		----------
			label:
				type: string / None
				info: predicted sentence label
		"""

		node = self.tree
		label = node['clf_object'].predict(sentence)

		while label in node['clf_children'].keys():
			node = node['clf_children'][label]
			label = node['clf_object'].predict(sentence)

		if label is None: print(sentence, "(Unknown label)")
		return label
