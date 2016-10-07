# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, sys
from Classifier import Classifier
from DataMiner import DataMiner
from StreamListener import TwitterListener
from multiprocessing import Process


# Objects creation
miner = DataMiner()
classifier = Classifier()

# Folder paths
datasets_folder = "./Datasets/"
models_folder = "./Models/"




################# TRAIN TEST #################
# Arguments: "Train" <Classifier> <Label 1 file> <Label 2 file>

if (sys.argv[1].lower() == "train") and (len(sys.argv) == 5):

    l1_file_path = datasets_folder + sys.argv[3]
    l2_file_path = datasets_folder + sys.argv[4]

    # Divide execution depending on the specified classifier
    if "max-entropy" in sys.argv[2].lower():
        classifier.train("max-entropy", l1_file_path, l2_file_path, 1000, 10000)
        classifier.saveModel(models_folder + sys.argv[2] + ".pickle")

    elif "naive-bayes" in sys.argv[2].lower():
        classifier.train("naive-bayes", l1_file_path, l2_file_path, 1000, 10000)
        classifier.saveModel(models_folder + sys.argv[2] + ".pickle")

    elif "nu-svc" in sys.argv[2].lower():
        classifier.train("nu-svc", l1_file_path, l2_file_path, 1000, 10000)
        classifier.saveModel(models_folder + sys.argv[2] + ".pickle")

    else:
        print("ERROR: Invalid classifier")
        exit()




################# CLASSIFY TEST #################
# Arguments: "Classify" <Classifier> <Twitter account> <Word>

elif (sys.argv[1].lower() == "classify") and (len(sys.argv) == 5):

    # Mining process
    classifier.loadModel(models_folder + sys.argv[2] + ".pickle")
    tweets = miner.getUserTweets(sys.argv[3], sys.argv[4])

    # Obtaining probabilities of each tweet
    sentences = Utilities.getSentences(tweets, sys.argv[4])
    probabilities = classifier.classify(sentences)

    print(Utilities.getPolarity(probabilities, classifier.MODEL.labels()))




################## SEARCH TEST ##################
# Arguments: "Search" <Search query> <Language> <Search depth> <Storing file>

elif (sys.argv[1].lower() == "search") and (len(sys.argv) == 6):

    tweets = miner.searchTweets(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    Utilities.storeTweets(tweets, datasets_folder + sys.argv[5])




################## STREAM TEST ##################
# Arguments: "Stream" <Classifier> <Stream query> <Language> <Output file> <Coordinates>

elif (sys.argv[1].lower() == "stream") and (len(sys.argv) == 7):

    # Load a trained classifier
    classifier.loadModel(models_folder + sys.argv[2] + ".pickle")

    tracks = sys.argv[3].split(',')
    languages = sys.argv[4].split(',')
    coordinates = sys.argv[6].split(',')
    labels = classifier.MODEL.labels()

    if len(coordinates) % 4 != 0:
        print("ERROR: The number of coordinates must be a multiple of 4")
        exit()

    coordinates = [float(coord) for coord in coordinates]

    # Creates the stream object and start stream
    stream = TwitterListener()
    streamProcess = Process(target = stream.init, args = (classifier, tracks, languages, sys.argv[5], coordinates))
    streamProcess.start()

    from matplotlib import pyplot, animation
    from GraphAnimator import animatePieChart, figure

    # Animate the graph each milliseconds interval
    ani = animation.FuncAnimation(figure, animatePieChart, interval = 1000, fargs = (sys.argv[5], labels,))
    pyplot.show()

    # Finally: kill stream process
    if streamProcess is not None:
        streamProcess.terminate()




# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. Possible options:")
    print("Mode 1 arguments: 'Train' <Classifier> <Label 1 file> <Label 2 file>")
    print("Mode 2 arguments: 'Classify' <Classifier> <Twitter account> <Word>")
    print("Mode 3 arguments: 'Search' <Search query> <Language> <Search depth> <Storing file>")
    print("Mode 4 arguments: 'Stream' <Classifier> <Stream query> <Language> <Output file> <Coordinates>")
