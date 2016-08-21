# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re


""" Class in charge of dealing with Twitter opinions and their scores """
class Analyzer(object):


    """ Divides a text into sentences and return those containing the specified word """
    def getSentences(self, text, word = None):

        sentences = re.split("[.:!?]\s+", text)

        # If no word is specified: return all the sentences
        if word is not None:
            sentences = [sentence for sentence in sentences if word.lower() in sentence.lower()]

        return sentences




##### TESTING #####
test = "Whats up? I am doing fine. See you later, friend! #ByeBye"
a = Analyzer()
print(a.getSentences(test))
print(a.getSentences(test, "FINE"))