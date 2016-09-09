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
# Arguments: "Train" <Classifier> <Positive file> <Negative file>

if (sys.argv[1].lower() == "train") and (len(sys.argv) == 5):

    pos_file_path = datasets_folder + sys.argv[3]
    neg_file_path = datasets_folder + sys.argv[4]

    # Checking if the specified files exist
    if (os.path.isfile(pos_file_path) is False) or (os.path.isfile(neg_file_path) is False):
        print("ERROR: One of the training files does not exist inside 'Datasets' folder")
        exit()

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

    # Checking if the specified file exist
    if os.path.isfile(models_folder + sys.argv[2] + ".pickle") is False:
        print("ERROR: The specified classifier model has not been saved")
        exit()

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




# In case none of the possible options is selected: error
else:
    print("ERROR: Invalid arguments. There are 3 possible options:")
    print("Mode 1 arguments: 'Train' <Classifier> <Positive file> <Negative file>")
    print("Mode 2 arguments: 'Classify' <Classifier model> <Twitter account> <Word>")
    print("Mode 3 arguments: 'Search' <Search query> <Language> <Search depth> <Storing file>")
