# Sentiment AI 📊

This project contains some of the code I used in my CS Bachelor's thesis research. Its main goal is to provide a simple sentiment analysis tool that can be used joinly with the Twitter API in order to classify tweets, depending on the sentiment, as <i>"positive"</i>, <i>"negative"</i> or <i>"neutral"</i>.
<br><br>
The <a href="http://scikit-learn.org/stable/">Scikit-learn</a> Machine Learning package includes a wide range of techniques that provide computers with the ability to learn without being explicitly programmed. Machine Learning (ML) plays a significant role in the analysis process because it help us to automate and generate a quicker response than the case of processing each piece of information (or tweet) individually by a person.
<br><br>
Additionally, there is a hosted web application that uses Python packages such as <a href="http://flask.pocoo.org/docs/0.12/">Flask</a> and <a href="http://gunicorn.org">Gunicorn</a>, in addition to some trained ML models, to provide an accesible graphical interface.
<br><br>
<b><a target="_blank" href="https://sentiment-ai-183521.appspot.com">Check out the Web Application here!</a></b>

<br>

## How does it work?

### General scheme:
<img src="https://github.com/Sinclert/SentimentAI/blob/master/Images/Project%20scheme.png"/>

On the one hand, we need to train ML models:<br>
<b>1. Datasets:</b> they are obtained from the NLTK corpus.<br>
<b>2. Datasets Preprocessing:</b> remove stopwords, transform every word into lower case...<br>
<b>3. Features selection:</b> using NLTK Chi-square scoring, get the most relevant features (indicated by a percentage).<br>
<b>4. Features vectors:</b> they are built and prepared to train an algorithm.<br>
<b>5. Training:</b> using algorithms such as: Bernoulli Naïve Bayes, Logistic Regression, Linear SVM or Random Forest.<br>
<br>
On the other hand, we need to extract the tweets we want to classify:<br>
<b>6. Tweets preprocessing:</b> remove stopwords, transform everything into lowcase...<br>
<b>7. Features vectors:</b> they are built and prepared to be classified.<br>
<b>8. Classification:</b> give them to the trained model and obtain labels for them.<br>

<br>

### Classification process:
In order to classify tweets among 3 possible labels, the project is designed to perform a hierarchical classification, instead of a multilabel one. This approach make more sense considering the domain in which we are classifying:
<br>
<img src="https://github.com/Sinclert/SentimentAI/blob/master/Images/Classification%20scheme.png" width="500" height="400"/>

Using this method, it is important to differenciate the 2 types of ML models we can train:
- <b>Polarity models:</b> classify between <i>"Neutral"</i> and <i>"Polarized"</i> categories.
- <b>Sentiment models:</b> classify between <i>"Positive"</i> and <i>"Negative"</i> categories.

<br>

### Considered ML algorithms:
From all the ML algorithms, only a set of them were trained and compared to each other using their <a href="https://en.wikipedia.org/wiki/F1_score">F-scores</a>. These algorithms were considered <b>without modifying any of the Scikit learn default parameters</b>, but in the case of Random Forest (number of trees incresed up to 100):
1. Bernoulli Naïve Bayes.
2. Linear SVM.
3. Logistic Regression.
4. Random Forest (k = 100).

<br>

### ML algorithms evaluation:
The comparison in order to select the best algorithm to solve this problem uses <b>10 Folds Cross Validation</b>, which divides the training sets in 10 folds, performing 10 training iterations where 9 are used for training and only 1 for testing.
<br><br>
Additionally, choosing a good fitness metric is basic to perform a good comparison. In this project, the chosen metric has been the <b>F-score</b>. This measure is better than common accuracy because it considers unbalance classification between labels (<a href="https://www.r-bloggers.com/accuracy-versus-f-score-machine-learning-for-the-rna-polymerases/">Explanation here</a>)

<br>

## What is in the repository?
The repository contains:

- <b>Datasets folder:</b> contains the NLTK datasets.
- <b>Evaluations folder:</b> contains the F-scores of the different ML algorithms.
- <b>Stopwords folder:</b> contains the stop words of different languages.
- <b>Evaluate.sh:</b> shell script that performs the testing, saving the results in the <i>"Evaluations"</i> folder.
- <b>Python files:</b> contains the code supporting the functionalities. The most relevant file is <i>"Parser.py"</i> because is the one you will need to execute. The relation among them and the different folders is as follows:

<img src="https://github.com/Sinclert/SentimentAI/blob/master/Images/Architecture.png"/>

<br>

## Usage:
The main file from which all functionalities are called is <i>"Parser.py"</i>. The execute syntax is as follows:
```shell
$ python3 Parser.py <Functionality> <Arguments> 
```

Depending on the chosen functionality, the arguments are different. Here is the list of possible functionalities:

<br>

### Train a model:
Trained models are saved in the <i>"Models"</i> folder (created if it does not exist). The expected arguments are:
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

<br>

### Search for tweets:
In this case the Twitter API is used to search for tweets fulfilling a specific query and save them to build a different dataset. The expected arguments are:
1. <b>Query:</b> words or hashtags that the tweets must contain.
2. <b>Language:</b> language in which the tweets are searched.
3. <b>Depth:</b> number of tweets to retrieve.
4. <b>Output:</b> name of the output file containing all the tweets.

Example:
```shell
$ python3 Parser.py search '#optimistic OR #happy' en 1000 PosTweets.txt
```

<br>

### Classify account tweets:
In this case, the <a href="https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline">Twitter REST API</a> is used to extract historic tweets from one specific account, and classify them using a pair of ML models (one polarity model and one sentiment model). The expected arguments are:
1. <b>Model 1:</b> polarity trained model.
2. <b>Model 2:</b> sentiment trained model.
3. <b>Account:</b> account to analyse.
4. <b>Filter word:</b> word that has to be present in the retrieved tweets.

Example:
```shell
$ python3 Parser.py classify Neu-Pol Pos-Neg David_Cameron brexit
```

<br>

### Classify real-time tweets:
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

<br>

## Requirements:
This project uses the third version of Python (Python 3) in order to interpret the instructions. Furthermore, additional packages are needed to perform all the steps in the ML training model process. This packages are:
- <a href="https://matplotlib.org">Matplotlib</a>
- <a href="http://www.nltk.org">NLTK</a>
- <a href="http://www.numpy.org">Numpy</a>
- <a href="https://www.scipy.org">Scipy</a>
- <a href="http://scikit-learn.org/stable/">Scikit-learn</a>
- <a href="http://www.tweepy.org">Tweepy</a>
