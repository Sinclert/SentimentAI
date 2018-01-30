# Created by Sinclert Perez (Sinclert@hotmail.com)




class FiguresDrawer(object):

	""" Represents a pie drawer static class """




	@staticmethod
	def draw_pie(counter, labels, colors, title):

		""" Plots a pie graph with the desired parameters

		Arguments:
		----------
			counter:
				type: dict
				info: occurrences of each label

			labels:
				type: list
				info: labels names

			colors:
				type: list
				info: colors RGB codes

			title:
				type: string
				info: name of the graph
		"""

		from matplotlib import pyplot

		sizes = []
		for label in labels:
			sizes.append(counter[label])

		pyplot.pie(
			x = sizes,
			labels = labels,
			colors = colors
		)

		pyplot.axis('equal')
		pyplot.title(title)
		pyplot.show()
