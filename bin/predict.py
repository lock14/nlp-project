#!/usr/bin/env python3

import argh
import itertools
import scipy
import glob
import os
import datetime
import random
import sklearn
from sklearn import feature_extraction
from sklearn import linear_model
import xml.etree.ElementTree as ET


def fit_vectorizer(datasets, min_ngrams, max_ngrams, max_features, stop_words, count):

    if count:
        vect = feature_extraction.text.CountVectorizer
    else:
        vect = feature_extraction.text.TfidfVectorizer
    vectorizer = vect(
        input="filename", ngram_range=(min_ngrams, max_ngrams), min_df=1,
        max_features=max_features, stop_words=stop_words,
        decode_error="ignore")

    vectorizer.fit(itertools.chain(*datasets))
    return vectorizer

def get_text_features(vectorizer, datasets):
    ngram_features = []
    for dataset in datasets:
        ngram_features.append(vectorizer.transform(dataset))
    return scipy.sparse.hstack(ngram_features)
        

def train(train_x, train_y):
    elastic_net = linear_model.ElasticNetCV(
        l1_ratio=[.1, .5, .7, .9, .95, .99, 1], n_jobs=-1, cv=3)
    elastic_net.fit(train_x, train_y)
    return elastic_net


def test(elastic_net, test_x, test_y):
    values = elastic_net.predict(test_x)
    for i in range(10):
        print(test_y[i], values[i])
    r2 = sklearn.metrics.r2_score(test_y, values)
    mae = sklearn.metrics.mean_absolute_error(test_y, values)
    return mae, r2
    
def get_metadata(xml_directory):
    earnings = {}
    metadata = {}
    for xml_file in glob.glob(os.path.join(xml_directory, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        revenue = root.find("weekend_gross")
        basename = os.path.basename(xml_file)
        movie = os.path.splitext(basename)[0]
        earnings[movie] = revenue.text
        date_str = root.find("release_date").text
        date = datetime.datetime.strptime(date_str, "%B %d, %Y")
        metadata[movie] = str(date.year)

    return earnings, metadata        

def get_texts(movies, text_directories):
    texts = []
    for dataset in text_directories:
        dataset_texts = {}
        for movie in movies:
            text_file = os.path.join(dataset, movie + ".txt")
            if os.path.exists(text_file):
                dataset_texts[movie] = text_file
        texts.append(dataset_texts)
    return texts

def check_data(earnings, movie_metadata, texts, metadata):
    complete = set(earnings.keys())
    for dataset in texts:
        complete = complete.intersection(dataset.keys())
    if metadata:
        complete = complete.intersection(movie_metadata.keys())
    return complete
        

def get_earning_features(earnings, order):
    features = []
    for movie in order:
        revenue_str = earnings[movie]
        clean_str = revenue_str.strip("$").replace(",", "")
        revenue = float(clean_str) 
        features.append(revenue)
    return features

def text_to_datasets(texts, order):
    features = [ [] for i in range(len(texts))]
    for movie in order:
        for i, dataset in enumerate(texts):
            feature = dataset[movie]
            features[i].append(feature)
            if not os.path.exists(feature):
                print("Missing file: {0}".format(feature))
    return features

def train_test_split(movies, metadata, test_years):
    test_movies = set()
    for movie in movies:
        data = metadata[movie]
        if data in test_years:
            test_movies.add(movie)
    train = movies.difference(test_movies)
    return list(train), list(test_movies)
        
@argh.arg("-t", "--text-directories", nargs="+")
def main(xml_directory, text_directories=None, use_metadata=False,
         max_ngrams=3, seed=1, min_ngrams=1, stop_words=None,
         max_features=20000, count=False):

    earnings, metadata = get_metadata(xml_directory)
    texts = get_texts(earnings.keys(), text_directories)
    complete_movies = check_data(earnings, metadata, texts, use_metadata)

    num_total = len(earnings.keys())
    num_complete = len(complete_movies)
    print("{0} movies used out of {1} total".format(num_complete, num_total))

    train_data, test_data = train_test_split(complete_movies, metadata, ["2009"])

    if seed:
        random.seed(seed)
        
    random.shuffle(list(train_data))
    random.shuffle(list(test_data))

    print("movies in training set: ", len(train_data))
    print("movies in test set: ", len(test_data))

    train_earning_features = get_earning_features(earnings, train_data)
    train_text_datasets = text_to_datasets(texts, train_data)

    print("fitting vectorizer...")
    vectorizer = fit_vectorizer(
        train_text_datasets, min_ngrams, max_ngrams, max_features,
        stop_words, count)

    print("extracting training features...")
    train_text_features = get_text_features(vectorizer, train_text_datasets)
    
    print("training...")
    trained_model = train(train_text_features, train_earning_features)

    print("extracting test features...")
    test_earning_features = get_earning_features(earnings, test_data)
    test_text_datasets = text_to_datasets(texts, test_data)
    test_text_features = get_text_features(vectorizer, test_text_datasets)

    print("testing...")
    mae, r2 = test(trained_model, test_text_features, test_earning_features)
    print("MAE: ", mae)
    print("r2: ", r2)

if __name__ == "__main__":
    argh.dispatch_command(main)
