# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, os, sys
from Classifier import Classifier
from DataMiner import DataMiner


# Objects creation
miner = DataMiner()
classifier = Classifier()

# Folder paths
datasets_folder = "./Datasets/"
models_folder = "./Models/"


################# TRAIN TEST #################
# Arguments: "Train" <Positive file> <Negative file> <Debug mode> <Model file>

if (sys.argv[1].lower() == "train") and (len(sys.argv) == 6):

    # Checking if the specified files exist
    if (os.path.isfile(datasets_folder + sys.argv[2]) is False) or (os.path.isfile(datasets_folder + sys.argv[3]) is False):
        print("ERROR: One of the train files does not exist")
        exit()

    debug_mode = None

    # Obtaining debug mode
    if sys.argv[4].lower() == 'true':
        debug_mode = True
    elif sys.argv[4].lower() == 'false':
        debug_mode = False
    else:
        print("ERROR: Invalid 'debug mode' argument value")
        exit()

    # Training and model storing
    classifier.train(datasets_folder + sys.argv[2], datasets_folder + sys.argv[3], 500, 5000, debug_mode)
    classifier.saveModel(models_folder + sys.argv[5])





################# CLASSIFY TEST #################
# Arguments: "Classify" <Model file> <Twitter account> <Word>

elif (sys.argv[1].lower() == "classify") and (len(sys.argv) == 5):

    # Checking if the specified file exist
    if os.path.isfile(models_folder + sys.argv[2]) is False:
        print("ERROR: The specified model does not exist")
        exit()

    # Mining process
    classifier.loadModel(models_folder + sys.argv[2])
    tweets = miner.getUserTweets(sys.argv[3], sys.argv[4])

    # Obtaining probabilities of each tweet
    sentences = Utilities.getSentences(tweets, sys.argv[4])
    probabilities = classifier.classify(sentences)

    print(Utilities.getPolarity(probabilities))





################## SEARCH TEST ##################
# Arguments: "Search" <Search query> <Language> <Search depth> <Storing file>

elif (sys.argv[1].lower() == "search") and (len(sys.argv) == 6):
    tweets = miner.searchTrainTweets(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    Utilities.storeTweets(tweets, datasets_folder + sys.argv[5])





# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. There are 3 possible options:")
    print("Mode 1 arguments: 'Train' <Positive file> <Negative file> <Debug mode> <Model file>")
    print("Mode 2 arguments: 'Classify' <Model file> <Twitter account> <Word>")
    print("Mode 3 arguments: 'Search' <Search query> <Language> <Search depth> <Storing file>")
