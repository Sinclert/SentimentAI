# Created by Sinclert Perez (Sinclert@hotmail.com)

import Utilities, sys
from Classifier import Classifier
from DataMiner import DataMiner
from StreamListener import TwitterListener
from multiprocessing import Process, Manager


# Folder paths
datasets_folder = "./Datasets/"
models_folder = "./Models/"

classifiers = ['logistic-regression', 'max-entropy', 'naive-bayes', 'nu-svc']




################# TRAIN TEST #################
# Arguments: "Train" <Classifier> <Label 1 file> <Label 2 file> <Words prop> <Bigrams prop> <Output file>

if (len(sys.argv) == 8) and (sys.argv[1].lower() == "train"):

    # Checks the specified classifier
    if sys.argv[2].lower() in classifiers:

        l1_file_path = datasets_folder + sys.argv[3]
        l2_file_path = datasets_folder + sys.argv[4]

        # Object creation
        classifier = Classifier()

        try:
            classifier.train(sys.argv[2].lower(), l1_file_path, l2_file_path, int(sys.argv[5]), int(sys.argv[6]))
            classifier.saveModel(models_folder + sys.argv[7] + ".pickle")

        except ValueError:
            print("ERROR: The words proportion and the bigrams proportion must be integer numbers")
            exit()

    else:
        print("ERROR: Invalid classifier")
        exit()




################# CLASSIFY TEST #################
# Arguments: "Classify" <Classifier> <Twitter account> <Word>

elif (len(sys.argv) == 5) and (sys.argv[1].lower() == "classify"):

    # Objects creation
    miner = DataMiner()
    classifier = Classifier()

    # Mining process
    classifier.loadModel(models_folder + sys.argv[2] + ".pickle")
    tweets = miner.getUserTweets(sys.argv[3], sys.argv[4])

    # Obtaining probabilities of each tweet
    sentences = Utilities.getSentences(tweets, sys.argv[4])
    classifications = dict()

    # Creating the results dictionary
    for label in sorted(classifier.MODEL.labels()):
        classifications[label] = 0

    # Storing the classification results
    for sentence in sentences:
        classifications[classifier.classify(sentence)] += 1

    print(classifications)




################## SEARCH TEST ##################
# Arguments: "Search" <Search query> <Language> <Search depth> <Output file>

elif (len(sys.argv) == 6) and (sys.argv[1].lower() == "search"):

    # Object creation
    miner = DataMiner()

    tweets = miner.searchTweets(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    Utilities.storeTweets(tweets, datasets_folder + sys.argv[5])




################## STREAM TEST ##################
# Arguments: "Stream" <Classifier 1> <Classifier 2> <Buffer size> <Query> <Language> <Coordinates>

elif (len(sys.argv) == 8) and (sys.argv[1].lower() == "stream"):

    # Load both trained classifiers
    classifier1 = Classifier()
    classifier2 = Classifier()
    classifier1.loadModel(models_folder + sys.argv[2] + ".pickle")
    classifier2.loadModel(models_folder + sys.argv[3] + ".pickle")
    labels = ['Negative', 'Neutral', 'Positive']

    # Parsing arguments
    buffer_size = int(sys.argv[4])
    tracks = sys.argv[5].split(',')
    languages = sys.argv[6].split(',')
    coordinates = sys.argv[7].split(',')

    if len(coordinates) % 4 != 0:
        print("ERROR: The number of coordinates must be a multiple of 4")
        exit()

    coordinates = [float(coord) for coord in coordinates]


    # Shared dictionary between both processes
    shared_dict = Manager().dict()
    shared_dict['Negative'] = 0
    shared_dict['Neutral'] = 0
    shared_dict['Positive'] = 0

    # Creates the stream object and start stream
    stream = TwitterListener()
    stream.setConnection()
    streamProcess = Process(target = stream.init,
                            args = (classifier1, classifier2, buffer_size, tracks, languages, coordinates, shared_dict))
    streamProcess.start()


    from matplotlib import pyplot, animation
    from GraphAnimator import animatePieChart, figure

    # Animate the graph each milliseconds interval
    ani = animation.FuncAnimation(figure, animatePieChart, interval = 500, fargs = (labels, tracks, shared_dict))
    pyplot.show()

    # Finally: kill stream process
    if streamProcess is not None:
        streamProcess.terminate()




# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. Possible options:")
    print("Mode 1: 'Train' <Classifier> <Label 1 file> <Label 2 file> <Words prop> <Bigrams prop> <Output file>")
    print("Mode 2: 'Classify' <Classifier> <Twitter account> <Word>")
    print("Mode 3: 'Search' <Search query> <Language> <Search depth> <Output file>")
    print("Mode 4: 'Stream' <Classifier 1> <Classifier 2> <Buffer size> <Query> <Language> <Coordinates>")
