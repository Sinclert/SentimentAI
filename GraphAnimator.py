# Created by Sinclert Perez (Sinclert@hotmail.com)

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
figure = pyplot.figure()

pie_colors = ["orangered", "green"]


""" Main method to animate live pie charts """
def animatePieChart(i, pie_labels, prob_buffer):

    # Labels counters
    l1_counter = 0
    l2_counter = 0

    for prob in prob_buffer:

        # Tweets between 0.45 and 0.55 are not considered
        if prob > 0.55:
            l1_counter += 1
        elif prob < 0.45:
            l2_counter += 1


    # Avoid empty pie chart when write is performed
    if (l1_counter + l2_counter) != 0:
        figure.clear()
        pyplot.pie([l1_counter, l2_counter], labels = pie_labels, colors = pie_colors)
