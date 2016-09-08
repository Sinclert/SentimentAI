# Created by Sinclert Perez (Sinclert@hotmail.com) on 14/08/2016

import re


# Indicates de percentage of tweets that are disregarded
confidence_threshold = 0.10


""" Divides tweets into sentences and returns those containing the specified word """
def getSentences(tweets, word = None):

    sentences = []

    # If there is a list of tweets as input
    if type(tweets) is list:
        for tweet in tweets:

            # Recursive call to obtain the sentences of each individual tweet
            for sentence in getSentences(tweet, word):
                sentences.append(sentence)

    # Base case: individual tweet
    elif isinstance(tweets, str):
        sentences = re.split("[.:!?]\s+", str(tweets))

        if word is not None:
            sentences[:] = [sentence for sentence in sentences if word.lower() in sentence.lower()]

    # If what we are processing is neither a list nor a string: error
    else:
        print("ERROR: Invalid value in one of the text inputs")
        exit()

    return sentences




""" Gets the polarity of several probability pairs by calculating the averages """
def getPolarity(classifications):

    if len(classifications) > 0:

        # If the input list contains probabilities
        if isinstance(classifications[0], dict):

            # Calculating the positive average is enough
            pos_average = 0

            for prob_pair in classifications:
                pos_average += prob_pair['Positive']

            pos_average /= len(classifications)


            # CONFIDENCE THRESHOLD APPLICATION
            outliers = int(len(classifications) * confidence_threshold)

            # If there are outliers: they are subtracted from the mean
            if outliers > 0:

                differences = []
                for prob_pair in classifications:
                    differences.append([prob_pair['Positive'], abs(pos_average - prob_pair['Positive'])])

                differences.sort(key = lambda element: element[1], reverse = True)
                pos_average *= len(classifications)

                for i in range(0, outliers):
                    pos_average -= differences[i][0]

                pos_average /= (len(classifications) - outliers)


            # Finally: label classification result
            if pos_average >= 0.5:
                return ['Positive', round(pos_average, 2)]
            else:
                return ['Negative', round(1 - pos_average, 2)]


        # If the input list does not contain probabilities
        else:
            pos_counter = 0

            for classification in classifications:
                if classification == 'pos':
                    pos_counter += 1

            # Finally: label classification result
            if pos_counter >= (len(classifications) - pos_counter):
                return ['Positive', str(pos_counter) + ":" + str(len(classifications) - pos_counter)]
            else:
                return ['Negative', str(pos_counter) +":" + str(len(classifications) - pos_counter)]


    # In case of an empty list: return None
    else:
        print("The input probabilities list is empty")
        return None




""" Appends the specified tweets into the specified text file """
def storeTweets(tweets, file_name, min_length = 20):

    file = open(file_name, 'a', encoding = "UTF8")
    skipped = 0

    for tweet in tweets:

        # Subtracting user names
        tweet = re.sub("(^|\s*)@\w+($|\s)", "", tweet)

        # Store the tweet only if it has enough length
        if len(tweet) >= min_length:
            file.write(tweet)
            file.write("\n")
        else:
            skipped += 1


    file.close()
    print(len(tweets) - skipped, "tweets has been stored into '", file_name, "'")
