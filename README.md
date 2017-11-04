# SentimentAI
This project contains the code I used for the research in my CS Bachelor Degree thesis. Its main goal is to provide a simple sentiment analysis tool that can be used joinly with the Twitter API in order to classify tweets as <i>"positive"</i>, <i>"negative"</i> or <i>"neutral"</i>
<br><br>
The <a href="http://scikit-learn.org/stable/">Scikit-learn</a> python machine learning package includes a wide range of techniques that provides computers with the ability to learn without being explicitly programmed. Machine Learning (ML) plays a significant role in the analysis process because it help us to automate and generate a quicker response than the case of processing each piece of information (or tweet) individually by a person.
<br><br>
Additionally, there is a web application hosted in Google Cloud that uses some of the trained ML models using this code.
<br><br>
<a href="https://sentiment-ai-183521.appspot.com">Click here to use the web application</a>


## How does it work?
There is a lot to explain, so only the more important concepts will be explained

### General scheme:

On the one hand, trained ML models are required to perform the analysis.
1. ML training datasets: they are obtained from the NLTK corpus.<br>
2. Datasets preprocessing: remove stopwords, transform everything into lowcase...<br>
3. Relevant features extraction: using NLTK Chi-square scoring, get the most relevant features (indicate a percentage).<br>
4. Vectors of features: they are built and prepared to train an algorithm.<br>
5. Train the models: using algorithms such as: Bernouilli Naive Bayes, Logistic Regression, Linear SVM and Random Forest.
<br><br><br>
On the other hand, we need to extract the tweets we want to classify. The Twitter API has 2 major branches: <b>REST API</b> and <b>Streaming API</b>. The difference between them is that the first one provides historic tweets from a given account, and the second one provides real time tweets given a set of coordinates (location).
6. Tweets preprocessing: remove stopwords, transform everything into lowcase...<br>
7. Vectors of features: they are built and prepared to be classified.<br>
8. Classify them: give them to the trained model and obtain labels for them.<br>

<IMG>

### Classification process:
In order to classify tweets among 3 possible labels, the project is designed to perform a hierarchical classification, instead of a multilabel one. This approach make more sense considering the domain in which we are classifying:
<IMG>

### ML algorithms considered:
From all the algorithms offered by Scikit-learn, only a set of them were trained and tested. From better results to worse results, considering the <a href="https://en.wikipedia.org/wiki/F1_score">F-measure</a>:
1. Bernouilli Naive Bayes (%, %)
2. Linear SVM (%, %)
3. Logistic Regression (%, %)
4. Random Forest (%, %)


### How the ML algorithms are tested:
The comparison and testing process in order to select the best algorithm to solve tihs problem uses <b>10 Folds Cross Validation</b>, which divides the training sets in 10 folds, and performs 10 training iterations where 9 are used for training and ony 1 for testing.
<br><br>
Additionally, it is importatn to choose a good comparison metric. In this project the comparison metric is <b>F-measure</b>, also knwon as <b>F-score</b>. This measure is better than common accuracy because it considers unbalance classification between lables (<a href="https://www.r-bloggers.com/accuracy-versus-f-score-machine-learning-for-the-rna-polymerases/">Explanation here</a>)


## What is in the repository?
The repository contains:


## Usage:
The main file from which all functionalities are called is "Parser.py". The structure to execute it is the wolllowing:
```shell
$ python3 Parser.py <Functionality> <Arguments> 
```

Depending on the chosen functionality, the arguments are different. List of possible functionalities:

### Train a model:
The syntax will be the following:
```shell
$ python3 Parser.py train <classifier> <file1> <file 2> <words percentage> <bigrams percentage> <Output>
```
Example: $ ... train Logistic-Regression Positive.txt Negative.txt 5 1 Pos-Neg

### Expand / Create your own dataser:
The syntax will be the following:
```shell
$ python3 Parser.py search <query> <language> <depth> <output>
```
Example: $ ... search “#optimistic OR #happy” en 1000 PosTweets.txt

### Classify tweets from an account:
The syntax will be the following:
```shell
$ python3 Parser.py classify <polarity model> <sentiment model> <account> <filter word>
```
Example: $ ... classify Neu-Pol Pos-Neg David_Cameron brexit

### Classify real-time tweets from a location:
The syntax will be the following:
```shell
$ python3 Parser.py stream <polarity model> <sentiment model> <buffer size> <filter word> <location coordinates>
```
Example: $ ... stream Neu-Pol Pos-Neg 500 Obama en -122,36,-121,38

<b>Tip:</b> If you want to translate real word locations into coordinates, you can use the <a href="https://developers.google.com/maps/documentation/geocoding/intro">Google Geocoding API</a>


## Requirements:
This project uses the third version of Python (Python 3) in order to interpret the instructions. Furthermore, additional packages are needed to perform all the steps in the ML training model process. This packages are:
- <a href="https://matplotlib.org">Matplotlib</a>
- <a href="http://www.nltk.org">NLTK</a>
- <a href="http://www.numpy.org">Numpy</a>
- <a href="https://www.scipy.org">Scipy</a>
- <a href="http://scikit-learn.org/stable/">Scikit-learn</a>
- <a href="http://www.tweepy.org">Tweepy</a>
