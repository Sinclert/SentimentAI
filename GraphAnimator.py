# Created by Sinclert Perez (Sinclert@hotmail.com)

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
figure = pyplot.figure()

pie_labels = ["Positive", "Negative"]
pie_colors = ["green", "orangered"]


""" Main method to animate live pie charts """
def animatePieChart(i, file):

    try:
        data = open(file, 'r').read()
    except FileNotFoundError:
        return

    lines = data.split('\n')

    # Labels counters
    pos_counter = 0
    neg_counter = 0

    for line in lines:

        # Avoid last empty line
        if len(line) > 0:
            number = float(line)

            # Tweets between 0.45 and 0.55 are not considered
            if number > 0.55:
                pos_counter += 1
            elif number < 0.45:
                neg_counter += 1


    # Avoid empty pie chart when write is performed
    if (pos_counter + neg_counter) != 0:
        figure.clear()
        pyplot.pie([pos_counter, neg_counter], labels = pie_labels, colors = pie_colors)
