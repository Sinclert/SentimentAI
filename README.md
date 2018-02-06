# Sentiment AI 📊

This project is based on the code used in my CS Bachelor's thesis research. Its main goal is to provide a simple way of training ML models to perform classification over tweets (using Twitter APIs). The models can be combined using a JSON configuration file, in order to build a hierarchical classifier in the shape of a tree, where nodes are trained models and leaves are the final categories.

Althought the models could be trained using datasets of very different nature, one of the most straightforward applications is to build a <a href="https://en.wikipedia.org/wiki/Sentiment_analysis">sentiment analysis</a> hierarchical classifier. This particular classification example is hosted online using packages such as <i>Flask</i> and <i>Gunicorn</i>, to show the project potential capabilities.

<b><a target="_blank" href="https://sentiment-ai-183521.appspot.com">Check out the Web Application here!</a></b>


## How does it work?

### General scheme:
<img src="resources/images/project_steps.png"/>

First of all, the datasets are processed and the ML models trained:

<b>1. Datasets:</b> they are text files containing one sentence per row.<br>
<b>2. Sentences cleaning:</b> tokenize, remove stopwords and extract the lemma of each word.<br>
<b>3. Features vectors:</b> build feature vectors using unigrams (words) and bigrams (pairs of words).<br>
<b>4. Features selection:</b> get the most informative features (input percentage) using chi-square test.<br>
<b>5. Filter features:</b> filter the current features leaving only the most informative ones.<br>
<b>6. Train classifier:</b> use <a href="http://scikit-learn.org/stable/">Scikit-learn</a> algorithms:<br>
- <i>Bernoulli Naïve Bayes.</i><br>
- <i>Logistic Regression.</i><br>
- <i>Linear Support Vector Machine.</i><br>
- <i>Random Forest (100 trees).</i><br>

Secondly, the tweets are extracted and processed:

<b>7. Tweets extraction:</b> obtain tweets from Twitter APIs using <a href="http://www.tweepy.org">Tweepy</a>.<br>
<b>8. Tweets preprocessing:</b> tokenize, remove stopwords and extract the lemma of each word.<br>
<b>9. Features vectors:</b> build feature vectors using unigrams (words) and bigrams (pairs of words).<br>
<b>10. Filter features:</b> filter the current features leaving only the most informative ones.<br>

<br>

Finally, the classification is performed:<br>
<b>11. Classification:</b> the trained models classify the vector of features into one of the final categories.<br>


### Classification process:
The classification is performed in a hierarchical way. This means that the trained models are placed in the nodes of a tree, and depending on how the previous models have classified a given piece of information, it will follow one branch or another.

The advantages os this approach over a classic multi-label classification are:<br>
- There could be different model algorithms as nodes, depending on which one perform best.<br>
- The set of most informative features is specific for each label-to-label differentiation.<br>

Following with the sentiment analysis case, there are 3 possible categories: neutral, positive and negative. They are represented as leaves in the classification tree, so once the assigned category is one of those, the process is over. The classification tree would have this shape:<br>

<img src="resources/images/hierarchical_clf.png" width="500" height="500"/>

In order to build a this custom classification tree, a JSON file with the following structure is required:

```json
{
    "tree": {
        "clf_file": "subjetivity.pickle",
        "clf_object": null,
        "clf_children": {
            "polarized": {
                "clf_file": "sentiment.pickle",
                "clf_object": null,
                "clf_children": {}
            }
        }
    },
    "colors": {
        "neutral": [0.6, 0.6, 0.6],
        "negative": [0.8, 0.0, 0.0],
        "positive": [0.0, 0.8, 0.0]
    }
}
```


### Models evaluation:
The evaluation of the different models (defined by algorithm and percentage of informative features) is done using <b>10 Folds Cross Validation</b>. This method divides the datasets in 10 folds, performing 10 iterations where 9 are used for training and 1 for testing. Finally, the mean of the results is calculated.

However, the evaluation procedure is not the only relevant factor to decide, choosing a good fitness metric is crucial to perform a good comparison. In this project, the evaluation metric is the <b>F-score</b>, which is better than common accuracy because it considers unbalance classification among categories (<a href="https://www.r-bloggers.com/accuracy-versus-f-score-machine-learning-for-the-rna-polymerases/">Explanation here</a>).


## What is in the repository?
The repository contains:

- <b>Evaluation folder:</b> contains a shell script to evaluate algorithms with different features percentages.

- <b>Models folder:</b> contains the trained models.

- <b>Profiles folder:</b> contrains configuration files:
  - <b>Predicting folder:</b> contains files for building a hierarchical classifier from individual models.
  - <b>Training folder:</b> contains files for training a model from specific datasets.

- <b>Resources folder:</b>
  - <b>Datasets folder:</b> contains datasets to train models.
  - <b>Images folder:</b> constains the images for this README.
  - <b>Stopwords folder:</b> contains lists of language specific non-relevant words to filter.

- <b>Source folder:</b> contains the code. The files could be grouped into different categories depending on their responsability:
  - <b>Classification files:</b> using Scikit-learn.
    - <i> clf_hierarchy.py</i>
    - <i> clf_node.py</i>
  - <b>Data mining files:</b> using Tweepy
    - <i> twitter_miner.py</i>
    - <i> twitter_stream.py</i>
  - <b>Data representation:</b> using Matplotlib
    - <i> figures.py</i>
  - <b>Text_processing:</b> using NLTK
    - <i>text_processing.py</i>


## Usage:
<b>DISCLAIMER:</b> Before using some of the following functionalities, you need to provide Twitter application and user keys in the <i>"twitter_keys.py"</i> file. They can be obtained by <b>creating a Twitter Application</b>.

The main file from which all functionalities are called is <i>"main.py"</i>. The execution syntax is as follows:
```shell
$ python3 main.py <functionality> <args> 
```

Depending on the chosen functionality, the arguments are different. List of possible functionalities:

### Train a model:
Trains a models and saves it inside the <i>"models"</i> folder. The expected arguments are:
- <b>-a algorithm:</b> {naive-bayes, logistic-regression, linear-svm, random-forest}.
- <b>-f features percentage:</b> percentage of most informative features to keep.
- <b>-l language:</b> language of the datasets sentences.
- <b>-o output:</b> name of the output model.
- <b>-p training profile:</b> JSON file specifying the datasets name and associated label. The datasets must be placed inside the <i>"profiles/training"</i> folder. Example:

```json
[
   {
      "dataset_name": "neutral.txt",
      "dataset_label": "neutral"
   },
   {
      "dataset_name": "polarized.txt",
      "dataset_label": "polarized"
   }
]
```

Command line example:
```shell
$ ... main.py train_clf -a Logistic-Regression -f 2 -l english -o polarity.pickle -p polarity.json
```


### Search for tweets:
Retrieves tweets using Twitter Search API and saves them inside <i>resources/datasets</i>. The expected arguments are:
- <b>-q query:</b> words or hashtags that the tweets must contain.
- <b>-l language:</b> language of the retrieved tweets.
- <b>-d search_depth:</b> number of tweets to retrieve.
- <b>-o output:</b> name of the output file containing all the tweets.

Command line example:
```shell
$ ... search_data -q "#excited OR #happy -filter:retweets" -l en -d 1000 -o pos_search.txt
```


### Predict user tweets:
Predicts the category of historic user tweets filtered by word using the Twitter REST API. The prediction is performed using a hierarchical classifier defined by a profile file inside <i>profile/predicting</i>. The expected arguments are:
- <b>-u user:</b> user account name (without the '@').
- <b>-w filter word:</b> word that has to be present in the retrieved tweets.
- <b>-p profile:</b> JSON specifying the hierarhical classification tree (inside <i>profile/predicting</i>).

Command line example:
```shell
$ ... predict_user -u david_cameron -w brexit -p sentiment.json
```


### Predict real-time tweets:
Predicts the category of real time tweets filtered by word and location using the Twitter Streaming API. The prediction is performed using a hierarchical classifier tree. The expected arguments are:
- <b>-s buffer size:</b> number of tweets to represent in a live graph.
- <b>-t filtered word:</b> word that has to be present in the retrieved tweets.
- <b>-l language:</b> language of the retrieved tweets.
- <b>-c coord_1 coord_2 coord_3 coord_4:</b> coordinates of the desired location.
- <b>-p profile:</b> JSON specifying the hierarhical classification tree (inside <i>profile/predicting</i>).


Command line example:
```shell
$ ... predict_stream -s 500 -t Trump -l en -c -122.75 36.8 -121.75 37.8 -p sentiment.json
```


## Requirements:
This project requires Python 3.4 (or superior) 🐍 , as long as some additional packages such as:<br>
- <a href="https://matplotlib.org">Matplotlib</a>
- <a href="http://www.nltk.org">NLTK</a>
- <a href="http://www.numpy.org">Numpy</a>
- <a href="https://www.scipy.org">Scipy</a>
- <a href="http://scikit-learn.org/stable/">Scikit-learn</a>
- <a href="http://www.tweepy.org">Tweepy</a>
