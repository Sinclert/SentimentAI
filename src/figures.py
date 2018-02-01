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




	@staticmethod
	def update_pie(frame, axis, counter, labels, colors):

		""" Plots a pie graph with the desired parameters (animation)

		Arguments:
		----------
			axis:
				type: ¿?
				info: ¿?

			counter:
				type: dict
				info: occurrences of each label

			labels:
				type: list
				info: labels names

			colors:
				type: list
				info: colors RGB codes
		"""

		sizes = []
		for label in labels:
			sizes.append(counter[label])

		if sum(sizes) > 0:

			axis.clear()
			axis.pie(
				x = sizes,
				labels = labels,
				colors = colors
			)




	@staticmethod
	def animate_pie(counter, labels, colors, title):

		""" Plots a pie graph with the desired parameters (animation)

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
		from matplotlib.animation import FuncAnimation

		figure, axis = pyplot.subplots()

		pyplot.title(title)
		pyplot.axis('equal')

		ani = FuncAnimation(
			fig = figure,
			func = FiguresDrawer.update_pie,
			interval = 250,
			repeat = False,
			fargs = (axis, counter, labels, colors)
		)

		pyplot.show()
