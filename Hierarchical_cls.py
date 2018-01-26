# Created by Sinclert Perez (Sinclert@hotmail.com)

import json
from Node_cls import Classifier


""" Class in charge of the hierarchical classification of sentences """
class Hierarchical_cls(object):


	""" Initiates variables when the instance is created """
	def __init__(self, cls_config_path):

		try:
			cls_config_file = open(cls_config_path)
			cls_config = json.load(cls_config_file)
			cls_config_file.close()

			self.cls_tree = cls_config
			self.__load_cls(node = self.cls_tree)

		except (FileNotFoundError, PermissionError, IsADirectoryError):
			print("ERROR: The file", cls_config_path, "cannot be opened")
			exit()




	""" Recursively loading classifier objects into dictionary keys """
	def __load_cls(self, node):

		node_cls = Classifier()
		node_cls.loadModel("Models", node['cls_name'])
		node['cls_object'] = node_cls

		try:
			for children in node['cls_children'].values():
				self.__load_cls(node = children)
		except KeyError:
			pass




	""" Predicts the final label of a sentence """
	def predict(self, sentence):

		node = self.cls_tree
		label = node['cls_object'].classify(sentence)

		# Keep traversing the tree until reaching a leaf node
		while label in node['cls_children'].keys():
			node = node['cls_children'][label]
			label = node['cls_object'].classify(sentence)

		if label is None:
			print(sentence, "(Tweet ignored)")

		return label
