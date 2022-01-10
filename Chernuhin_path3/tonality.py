import nltk
import pickle
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_ru')
nltk.download('wordnet')
nltk.download('punkt')
import pymorphy2
from pymorphy2 import MorphAnalyzer
import pandas as pd
import os
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
from itertools import chain
import re, string, random
import numpy as np
import csv
from pymongo import MongoClient
import time

client = MongoClient('mongodb+srv://makeev:makeev@cluster0.38igd.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
collection = client["db"]["news"]
df_pos = pd.read_csv("pos.csv", sep=";", header=None, nrows=50000)
df_neg = pd.read_csv("neg.csv", sep=";", header=None, nrows=50000)

df_posEdited = df_pos.iloc[:, 3]
df_negEdited = df_neg.iloc[:, 3]

df_posEdited = df_posEdited.dropna().drop_duplicates()
df_negEdited = df_negEdited.dropna().drop_duplicates()

patterns = "[A-Za-z0-9!#$%&'()*+,./:;<=>?@[\]^_`{|}~—\"\-]+"
stopwords_ru = stopwords.words("russian")
morph = MorphAnalyzer()

def lemmatize(doc):
    doc = re.sub(patterns, ' ', doc)
    doc = re.sub(r'\n|\r|\t', ' ', doc)
    doc = re.sub(r'\s+', ' ', doc)
    tokens = []
    for token in doc.split():
        if token and token not in stopwords_ru:
            token = token.strip()
            token = morph.normal_forms(token)[0]
            tokens.append(token)
    if len(tokens) > 2:
        return tokens
    return ' '
    
tokens_positive = df_posEdited.apply(lemmatize)
tokens_negative = df_negEdited.apply(lemmatize)

tokens_positive_list = list(tokens_positive)
tokens_negative_list = list(tokens_negative)

positive_string_list = list(df_posEdited)
negative_string_list = list(df_negEdited)

def remove_noise(tweet_tokens, stop_words = ()):

    cleaned_tokens = []

    for token, tag in pos_tag(tweet_tokens, lang="rus"):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)

if __name__ == "__main__":

    positive_tweets = positive_string_list
    negative_tweets = negative_string_list
    tweet_tokens = tokens_positive_list[0]

    stop_words = stopwords.words("russian")

    positive_tweet_tokens = tokens_positive_list
    negative_tweet_tokens = tokens_negative_list

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens, stop_words))

    all_pos_words = get_all_words(positive_cleaned_tokens_list)

    freq_dist_pos = FreqDist(all_pos_words)
    print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset
    #print(dataset)

    train_data = dataset[:90000]
    test_data = dataset[10000:]

    classifier = NaiveBayesClassifier.train(train_data)
    
    print("Accuracy is:", classify.accuracy(classifier, test_data))

    print(classifier.show_most_informative_features(10))
    
    
for i in collection.find():
    custom_tweet = i["text_news"]
    custom_tokens = remove_noise(word_tokenize(custom_tweet))
    
    print(custom_tweet, classifier.classify(dict([token, True] for token in custom_tokens)))
    collection.update({
                "_id": i["_id"]
            }, {
                "$push": {
                "tonality": classifier.classify(dict([token, True] for token in custom_tokens)) 
                }
            }) 
    print("-------------------------------------------------------------")
    print("\n")
    time.sleep(1)
    
