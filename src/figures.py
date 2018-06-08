# Created by Sinclert Perez (Sinclert@hotmail.com)




class FiguresDrawer(object):

	""" Represents a pie drawer static class """




	@staticmethod
	def draw_pie(counter: dict, labels: list, colors: list, title: str):

		""" Plots a pie graph with the desired parameters

		Arguments:
		----------
			counter: occurrences of each label
			labels: labels names
			colors: colors RGB codes
			title: name of the graph

		"""

		from matplotlib import pyplot

		sizes = [counter[label] for label in labels]

		pyplot.pie(
			x = sizes,
			labels = labels,
			colors = colors
		)

		pyplot.axis('equal')
		pyplot.title(title)
		pyplot.show()




	@staticmethod
	def update_pie(frame, axis, counter: dict, labels: list, colors: list):

		""" Plots a pie graph with the desired parameters (animation)

		Arguments:
		----------
			axis: space where the pie is drawn
			counter: occurrences of each label
			labels: labels names
			colors: colors RGB codes

		"""

		sizes = [counter[label] for label in labels]

		if sum(sizes) > 0:

			axis.clear()
			axis.pie(
				x = sizes,
				labels = labels,
				colors = colors
			)




	@staticmethod
	def animate_pie(counter: dict, labels: list, colors: list, title: str):

		""" Plots a pie graph with the desired parameters (animation)

		Arguments:
		----------
			counter: occurrences of each label
			labels: labels names
			colors: colors RGB codes
			title: name of the graph

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
