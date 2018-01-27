# Created by Sinclert Perez (Sinclert@hotmail.com)

from clf_model import Classifier
from utils import getFileJSON


""" Class in charge of the hierarchical classification of sentences """
class Hierarchical_cls(object):


	""" Initiates variables when the instance is created """
	def __init__(self, clf_profile_path):

		self.clf_tree = getFileJSON(clf_profile_path)
		self.__load_clf(node = self.clf_tree)





	""" Recursively loading classifier objects into dictionary keys """
	def __load_clf(self, node):

		clf_node = Classifier()
		clf_node.loadModel("models", node['clf_name'])
		node['clf_object'] = clf_node

		try:
			for children in node['clf_children'].values():
				self.__load_clf(node = children)
		except KeyError:
			pass




	""" Predicts the final label of a sentence """
	def predict(self, sentence):

		node = self.clf_tree
		label = node['clf_object'].classify(sentence)

		# Keep traversing the tree until reaching a leaf node
		while label in node['clf_children'].keys():
			node = node['clf_children'][label]
			label = node['clf_object'].classify(sentence)

		if label is None:
			print(sentence, "(Tweet ignored)")

		return label
