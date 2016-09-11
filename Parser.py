# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, os, sys, signal
from Classifier import Classifier
from DataMiner import DataMiner
from StreamListener import TwitterListener
from tweepy import Stream


# Objects creation
miner = DataMiner()
classifier = Classifier()

# Folder paths
datasets_folder = "./Datasets/"
models_folder = "./Models/"




################# TRAIN TEST #################
# Arguments: "Train" <Classifier> <Positive file> <Negative file>

if (sys.argv[1].lower() == "train") and (len(sys.argv) == 5):

    pos_file_path = datasets_folder + sys.argv[3]
    neg_file_path = datasets_folder + sys.argv[4]

    # Divide execution depending on the specified classifier
    if sys.argv[2].lower() == "nu-svc":
        classifier.train("nu-svc", pos_file_path, neg_file_path, 2000, 10000)
        classifier.saveModel(models_folder + "Nu-SVC.pickle")

    elif sys.argv[2].lower() == "max-entropy":
        classifier.train("max-entropy", pos_file_path, neg_file_path, 500, 10000)
        classifier.saveModel(models_folder + "Max-Entropy.pickle")

    elif sys.argv[2].lower() == "naive-bayes":
        classifier.train("naive-bayes", pos_file_path, neg_file_path, 1000, 50000)
        classifier.saveModel(models_folder + "Naive-Bayes.pickle")

    else:
        print("ERROR: Invalid classifier")
        exit()




################# CLASSIFY TEST #################
# Arguments: "Classify" <Classifier model> <Twitter account> <Word>

elif (sys.argv[1].lower() == "classify") and (len(sys.argv) == 5):

    # Mining process
    classifier.loadModel(models_folder + sys.argv[2] + ".pickle")
    tweets = miner.getUserTweets(sys.argv[3], sys.argv[4])

    # Obtaining probabilities of each tweet
    sentences = Utilities.getSentences(tweets, sys.argv[4])
    probabilities = classifier.classify(sentences)

    print(Utilities.getPolarity(probabilities))




################## SEARCH TEST ##################
# Arguments: "Search" <Search query> <Language> <Search depth> <Storing file>

elif (sys.argv[1].lower() == "search") and (len(sys.argv) == 6):

    tweets = miner.searchTweets(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    Utilities.storeTweets(tweets, datasets_folder + sys.argv[5])




################## STREAM TEST ##################
# Arguments: "Stream" <Classifier> <Stream query> <Language> <Output file>

elif (sys.argv[1].lower() == "stream") and (len(sys.argv) == 6):

    # Creates the stream and authenticator objects
    stream = TwitterListener()
    userAuth = stream.getConnection()

    # Set stream classifier and output file
    classifier.loadModel(models_folder + sys.argv[2] + ".pickle")
    stream.init(classifier, sys.argv[5])

    # Creating a new process
    pid = os.fork()


    # Parent process: Graphical User Interface
    if pid:
        from matplotlib import pyplot, animation
        from GraphAnimator import animatePieChart, graph

        ani = animation.FuncAnimation(graph, animatePieChart, interval = 1000)
        pyplot.show()

        # Finally: kill child process
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass


    # Child process: update stream results
    else:
        twitterStream = Stream(userAuth, stream)
        twitterStream.filter(track = [sys.argv[3]], languages = [sys.argv[4]])




# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. Possible options:")
    print("Mode 1 arguments: 'Train' <Classifier> <Positive file> <Negative file>")
    print("Mode 2 arguments: 'Classify' <Classifier model> <Twitter account> <Word>")
    print("Mode 3 arguments: 'Search' <Search query> <Language> <Search depth> <Storing file>")
    print("Mode 4 arguments: 'Stream' <Classifier> <Stream query> <Language> <Output file>")
