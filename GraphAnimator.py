# Created by Sinclert Perez (Sinclert@hotmail.com)

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
figure = pyplot.figure()
colors = ['orangered', 'lightslategray', 'mediumseagreen']




""" Main method to animate live pie charts """
def animatePieChart(i, labels, tracks, shared_dict):

    try:
        # Labels counters
        counters = [shared_dict[labels[0]], shared_dict[labels[1]], shared_dict[labels[2]]]

        # In case there is data to show
        if sum(counters) > 0:
            figure.clear()
            pyplot.title(tracks)
            pyplot.pie(counters, labels = labels, colors = colors)


    except BrokenPipeError:
        print("ERROR: Communication between processes cut")
        exit()
