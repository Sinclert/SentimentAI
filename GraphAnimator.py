# Created by Sinclert Perez (Sinclert@hotmail.com)

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
figure = pyplot.figure()

pie_colors = ['orangered', 'lightslategray', 'mediumseagreen']


""" Main method to animate live pie charts """
def animatePieChart(i, pie_labels, shared_dict):

    try:
        # Labels counters
        l1_counter = shared_dict[pie_labels[0]]
        l2_counter = shared_dict[pie_labels[1]]
        l3_counter = shared_dict[pie_labels[2]]

        # Avoid empty pie chart when write is performed
        if (l1_counter + l2_counter + l3_counter) != 0:
            figure.clear()
            pyplot.pie([l1_counter, l2_counter, l3_counter], labels = pie_labels, colors = pie_colors)


    except BrokenPipeError:
        print("ERROR: Communication between processes cut")
        exit()
