# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import Utilities
from Classifier import Classifier
from DataMiner import DataMiner


# Objects creation
miner = DataMiner()
classifier = Classifier()


# Train and mining processes
classifier.train("./Datasets/PosTweets.txt", "./Datasets/NegTweets.txt", 5000, 20000, False)
tweets = miner.getUserTweets("POTUS", "refugees")


# Obtaining probabilities of each tweet
sentences = Utilities.getSentences(tweets, "refugees")
probabilities = classifier.classify(sentences)

print(Utilities.getPolarity(probabilities))


# tweets = miner.searchTrainTweets(":)", "en", 1000)
# Utilities.storeTweets(tweets, "Example.txt")
