# Created by Sinclert Perez (Sinclert@hotmail.com)

from matplotlib import pyplot, style


# Global variables
style.use("ggplot")
figure = pyplot.figure()

pie_colors = ["orangered", "green"]


""" Main method to animate live pie charts """
def animatePieChart(i, file, pie_labels):

    try:
        data = open(file, 'r').read()
        lines = data.split('\n')

        # Labels counters
        l1_counter = 0
        l2_counter = 0

        for line in lines:

            # Avoid last empty line
            if len(line) > 0:
                number = float(line)

                # Tweets between 0.45 and 0.55 are not considered
                if number > 0.55:
                    l1_counter += 1
                elif number < 0.45:
                    l2_counter += 1


        # Avoid empty pie chart when write is performed
        if (l1_counter + l2_counter) != 0:
            figure.clear()
            pyplot.pie([l1_counter, l2_counter], labels = pie_labels, colors = pie_colors)

    
    except FileNotFoundError or PermissionError or IsADirectoryError:
        print("ERROR: The file '", file, "' cannot be opened")
        exit()
