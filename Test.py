# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities, sys, os.path
from Classifier import Classifier
from DataMiner import DataMiner


# Objects creation
miner = DataMiner()
classifier = Classifier()

# Datasets folder
folder = "./Datasets/"


################# TRAINING TEST #################
# Arguments: "Classify", positive file, negative file, debug mode, Twitter account, word

if (sys.argv[1].lower() == "classify") and (len(sys.argv) == 7):

    # Checking if the specified files exist
    if (os.path.isfile(folder + sys.argv[2]) is False) or (os.path.isfile(folder + sys.argv[3]) is False):
        print("ERROR: One of the train files does not exist")
        exit()

    debug_mode = None

    # Obtaining debug mode
    if sys.argv[4].lower() == 'true':
        debug_mode = True
    elif sys.argv[4].lower() == 'false':
        debug_mode = False
    else:
        print("ERROR: Invalid 'debug' argument value")
        exit()

    # Train and mining processes
    classifier.train(folder + sys.argv[2], folder + sys.argv[3], 500, 2000, debug_mode)
    tweets = miner.getUserTweets(sys.argv[5], sys.argv[6])

    # Obtaining probabilities of each tweet
    sentences = Utilities.getSentences(tweets, sys.argv[6])
    probabilities = classifier.classify(sentences)

    print(Utilities.getPolarity(probabilities))




################## SEARCH TEST ##################
# Arguments: "Search", search query, language, search depth, storing file

elif (sys.argv[1].lower() == "search") and (len(sys.argv) == 6):
    tweets = miner.searchTrainTweets(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    Utilities.storeTweets(tweets, folder + sys.argv[5])




# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. There are 2 possible options:")
    print("Mode 1 arguments: 'classify', positive file, negative file, debug mode, Twitter account, word")
    print("Mode 2 arguments: 'search', search query, language, search depth, storing file")
