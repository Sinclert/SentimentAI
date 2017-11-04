# SentimentAI
This project contains the code I used in my CS Bachelor's thesis research. Its main goal is to provide a simple sentiment analysis tool that can be used joinly with the Twitter API in order to classify tweets, depending on the sentiment, as <i>"positive"</i>, <i>"negative"</i> or <i>"neutral"</i>.
<br><br>
The <a href="http://scikit-learn.org/stable/">Scikit-learn</a> Machine Learning package includes a wide range of techniques that provide computers with the ability to learn without being explicitly programmed. Machine Learning (ML) plays a significant role in the analysis process because it help us to automate and generate a quicker response than the case of processing each piece of information (or tweet) individually by a person.
<br><br>
Additionally, there is a web application hosted in Google Cloud that uses some of the trained ML models using this code.
<br><br>
<a href="https://sentiment-ai-183521.appspot.com">Click here to use the web application</a>


## How does it work?
This section will be divided in smaller subsections in order to explain the most important concepts:

### General scheme:
<img src="../Images/Project%20scheme.png" width="600" height="450"/>

On the one hand, trained ML models are required to perform the analysis.
1. Training datasets: they are obtained from the NLTK corpus.
2. Datasets preprocessing: remove stopwords, transform every word into lower case...
3. Features selection: using NLTK Chi-square scoring, get the most relevant features (indicated by a percentage).
4. Vectors of features: they are built and prepared to train an algorithm.
5. Train the models: using algorithms such as: Bernoulli Naïve Bayes, Logistic Regression, Linear SVM or Random Forest.
<br><br>
On the other hand, we need to extract the tweets we want to classify. The Twitter API has 2 major branches: <b>REST API</b> and <b>Streaming API</b>. The difference between them is that the first one provides historic tweets from a given account, and the second one provides real time tweets given a set of coordinates (location).
6. Tweets preprocessing: remove stopwords, transform everything into lowcase...<br>
7. Vectors of features: they are built and prepared to be classified.<br>
8. Classify them: give them to the trained model and obtain labels for them.<br>

<IMG>

### Classification process:
In order to classify tweets among 3 possible labels, the project is designed to perform a hierarchical classification, instead of a multilabel one. This approach make more sense considering the domain in which we are classifying:
<img src="../Images/Classification%20scheme.png" width="600" height="450"/>

Using this method, it is important to differenciate the 2 types of ML models we can train:
- <b>Polarity models:</b> classify between "Neutral" and "Polarized" categories.
- <b>Sentiment models:</b> classify between "Positive" and "Negative" categories.

### ML algorithms considered:
From all the algorithms offered by Scikit-learn, only a set of them were trained and tested. They were tested and compared to each other using their <a href="https://en.wikipedia.org/wiki/F1_score">F-scores</a>. The results can be checked in the <i>"Evaluations"</i> folder. In a nutshell:
1. Bernoulli Naïve Bayes.
2. Linear SVM.
3. Logistic Regression.
4. Random Forest.


### How the ML algorithms are tested:
The comparison and testing process in order to select the best algorithm to solve tihs problem uses <b>10 Folds Cross Validation</b>, which divides the training sets in 10 folds, performing 10 training iterations where 9 are used for training and ony 1 for testing.
<br><br>
Additionally, choosing a good fitness metric is basic to perform a good comparison. In this project, the chosen metric has been the <b>F-score</b>. This measure is better than common accuracy because it considers unbalance classification between labels (<a href="https://www.r-bloggers.com/accuracy-versus-f-score-machine-learning-for-the-rna-polymerases/">Explanation here</a>)


## What is in the repository?
The repository contains:

- <b>Datasets folder:</b> contains the NLTK datasets.
- <b>Evaluations folder:</b> contains the F-scores of the different ML algorithms.
- <b>Stopwords folder:</b> contains the stop words of different languages (only English ones are used).
- <b>Evaluate.sh:</b> shell script that performs the testing, saving the results in the <i>"Evaluations"</i> folder.
- <b>Python files:</b> contains the code supporting the functionalities. The most relevant file is "Parser.py" because is the one you will need to execute. The relation among them and the different folders is as follows:

<img src="../Images/Architecture.png" width="600" height="450"/>


## Usage:
The main file from which all functionalities are called is "Parser.py". The execute syntax is as follows:
```shell
$ python3 Parser.py <Functionality> <Arguments> 
```

Depending on the chosen functionality, the arguments are different. List of possible functionalities with their expected arguments:

### Train a model:
In this case a trained model will be saved into the <i>"Models"</i> folder. This folder will be created in case it does not exist. The expected arguments are:
1. <b>Classifier:</b> {Naive-Bayes, Logistic-Regression, Linear-SVM, Random-Forest}
2. <b>File 1:</b> File inside "Datasets" containing the label 1 training examples.
3. <b>File 2:</b> File inside "Datasets" containing the label 2 training examples.
4. <b>Words percentage:</b> Percentage of words to keep.
5. <b>Bigrams percentage:</b> Percentage of bigrams (pairs of words) to keep.
6. <b>Output:</b> Name of the output model.

Example:
```shell
$ python3 Parser.py train Logistic-Regression Positive.txt Negative.txt 5 1 Pos-Neg
```

### Search for tweets:
In this case the Twitter API is used to search for tweets fulfilling a specific query and save them to build a different dataset. The expected arguments are:
1. <b>Query:</b> words or hashtags that the tweets must contain.
2. <b>Language:</b> language in which the tweets are searched.
3. <b>Depth:</b> number of tweets to retrieve.
4. <b>Output:</b> name of the output file containing all the tweets.

Example:
```shell
$ python3 Parser.py search “#optimistic OR #happy” en 1000 PosTweets.txt
```

### Classify tweets from an account:
In this case, the <a href="https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline">Twitter REST API</a> is used to extract historic tweets from one specific account, and classify them using a pair of ML models (one polarity model and one sentiment model). The expected arguments are:
1. <b>Model 1:</b> polarity trained model.
2. <b>Model 2:</b> sentiment trained model.
3. <b>Account:</b> account to analyse.
4. <b>Filter word:</b> word that has to be present in the retrieved tweets.

Example:
```shell
$ python3 Parser.py classify Neu-Pol Pos-Neg David_Cameron brexit
```

### Classify real-time tweets from a location:
In this case, the <a href="https://developer.twitter.com/en/docs/tweets/filter-realtime/api-reference/post-statuses-filter">Twitter Streaming API</a> is used to extract real time tweets from one specific location, and classify them using a pair of ML models (one polarity model and one sentiment model). The expected arguments are:
1. <b>Model 1:</b> polarity trained model.
2. <b>Model 2:</b> sentiment trained model.
3. <b>Buffer size:</b> number of tweets to represent into a live graph.
4. <b>Filter word:</b> word that has to be present in the retrieved tweets.
5. <b>Language:</b> language of the retrieved tweets.
6. <b>Coordinates:</b> coordinates of the desired location. <b>Tip:</b> use <a href="https://developers.google.com/maps/documentation/geocoding/intro">Google Geocoding API</a>

Example:
```shell
$ python3 Parser.py stream Neu-Pol Pos-Neg 500 Obama en -122,36,-121,38
```


## Requirements:
This project uses the third version of Python (Python 3) in order to interpret the instructions. Furthermore, additional packages are needed to perform all the steps in the ML training model process. This packages are:
- <a href="https://matplotlib.org">Matplotlib</a>
- <a href="http://www.nltk.org">NLTK</a>
- <a href="http://www.numpy.org">Numpy</a>
- <a href="https://www.scipy.org">Scipy</a>
- <a href="http://scikit-learn.org/stable/">Scikit-learn</a>
- <a href="http://www.tweepy.org">Tweepy</a>
