# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
graph = pyplot.figure()

pie_labels = ["Very positive", "Positive", "Negative", "Very negative"]
pie_colors = ["green", "yellowgreen", "orange", "red"]




""" Main method to animate live pie charts """
def animatePieChart(i, file):

    try:
        data = open(file, "r").read()
    except FileNotFoundError:
        return

    lines = data.split('\n')

    # Labels counters
    vpos_counter = 0
    pos_counter = 0
    neg_counter = 0
    vneg_counter = 0

    for line in lines:

        # Avoid last empty line
        if len(line) > 0:
            number = float(line)

            if number >= 0.8:
                vpos_counter += 1
            elif (number > 0.5) and (number < 0.8):
                pos_counter += 1
            elif (number > 0.2) and (number < 0.5):
                neg_counter += 1
            elif number <= 0.2:
                vneg_counter += 1

    graph.clear()
    pyplot.pie([vpos_counter, pos_counter, neg_counter, vneg_counter], labels = pie_labels, colors = pie_colors)
