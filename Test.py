# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

from Analyzer import Analyzer
from Classifier import Classifier
from DataMiner import DataMiner


# Objects creation
miner = DataMiner()
classifier = Classifier()
analyzer = Analyzer()


# Train and mining processes
classifier.train("./Datasets/PosTweets.txt", "./Datasets/NegTweets.txt", 5000, 20000, False)
tweets = miner.getUserTweets("POTUS", "refugees")


# Obtaining probabilities of each tweet
sentences = analyzer.getSentences(tweets, "refugees")
probabilities = classifier.classify(sentences)

print(analyzer.getPolarity(probabilities))
