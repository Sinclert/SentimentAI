# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re


""" Class in charge of dealing with Twitter opinions and their scores """
class Analyzer(object):


    """ Divides tweets into sentences and returns those containing the specified word """
    def getSentences(self, tweets, word = None):

        sentences = []

        # If there is a list of tweets as input
        if type(tweets) is list:
            for tweet in tweets:

                # Recursive call to obtain the sentences of each individual tweet
                for sentence in self.getSentences(tweet, word):
                    sentences.append(sentence)

        # Base case: individual tweet
        elif isinstance(tweets, str):
            sentences = re.split("[.:!?]\s+", str(tweets))

            if word is not None:
                sentences[:] = [sentence for sentence in sentences if word.lower() in sentence.lower()]

        # If what we are processing is neither a list nor a string: error
        else:
            print("ERROR: Invalid value in one of the text inputs")
            exit(-1)

        return sentences




    """ Gets the polarity of several probability pairs by calculating the averages """
    def getPolarity(self, probabilities):

        # Calculating the positive average is enough
        pos_average = 0

        for prob_pair in probabilities:
            pos_average += prob_pair['Positive']

        # The average is only computed if the input list is not empty
        if len(probabilities) > 0:
            pos_average /= len(probabilities)

            if pos_average >= 0.5:
                return ["Positive", round(pos_average, 2)]
            else:
                return ["Negative", round(1 - pos_average, 2)]

        # In case of an empty list: return None
        else:
            print("The input probabilities list is empty")
            return None
