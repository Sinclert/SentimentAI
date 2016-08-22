# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re


""" Class in charge of dealing with Twitter opinions and their scores """
class Analyzer(object):


    """ Divides a text into sentences and return those containing the specified word """
    def getSentences(self, text, word = None):

        sentences = re.split("[.:!?]\s+", str(text))

        # If no word is specified: return all the sentences
        if word is not None:
            sentences = [sentence for sentence in sentences if word.lower() in sentence.lower()]

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
            return None




##### TESTING #####
test = "Whats up? I am doing fine. See you later, friend! #ByeBye"
a = Analyzer()
print(a.getSentences(test))
print(a.getSentences(test, "FINE"))
print(a.getPolarity([{"Positive": 0.4, "Negative": 0.6}, {"Positive": 0.2, "Negative": 0.8}]))
