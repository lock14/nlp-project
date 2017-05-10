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
import sys
import pandas
import math



def fit_vectorizers(datasets, min_ngrams, max_ngrams, max_features, stop_words, count):

    if count:
        vect = feature_extraction.text.CountVectorizer
    else:
        vect = feature_extraction.text.TfidfVectorizer

    vectorizers = []
    for ngram in range(min_ngrams, max_ngrams + 1):
        vectorizer = vect(
            input="filename", ngram_range=(ngram, ngram), min_df=1,
            max_features=max_features, stop_words=stop_words,
            decode_error="ignore")

        vectorizer.fit(itertools.chain(*datasets))
        vectorizers.append(vectorizer)
    return vectorizers

def get_text_features(vectorizers, datasets):
    text_features = []
    for dataset in datasets:
        ngram_features = []
        for vectorizer in vectorizers:
            ngram_features.append(vectorizer.transform(dataset))
        text_features.append(scipy.sparse.hstack(ngram_features))
    return scipy.sparse.hstack(text_features)
        

def train(train_x, train_y, dev_x, dev_y):
    best_score = -(float("inf"))
    best_elastic_net = None
    best_tol = 0
    for tol in [0.0001, 0.001, 0.01, 0.1, 0.15, 0.2, 0.25, 0.5]:
        print("training with tol: ", tol)
        elastic_net = linear_model.ElasticNetCV(
            l1_ratio=[.1, .5, .7, .9, .95, .99, .999, .9999, 1], n_jobs=-1,
            tol=tol, selection="random")

        elastic_net.fit(train_x, train_y)
        dev_prediction = elastic_net.predict(dev_x)
        score = sklearn.metrics.r2_score(dev_y, dev_prediction)
        print("score: ", score)
        if score > best_score:
            best_elastic_net = elastic_net
            best_tol = tol
            best_score = score
            
    print("elastic net params: ", "alpha: ", best_elastic_net.alpha_,
          "l1_ratio: ", best_elastic_net.l1_ratio_,
          "tol:", best_tol)

    return best_elastic_net


def test(elastic_net, test_x, test_y):
    values = elastic_net.predict(test_x)
    print("First 5 predictions:")
    for i in range(5):
        print("\t", test_y[i], values[i])
    r2 = sklearn.metrics.r2_score(test_y, values)
    mae = sklearn.metrics.mean_absolute_error(test_y, values)
    return mae, r2
    
def get_metadata(xml_directory, predict):
    earnings = {}
    metadata = pandas.DataFrame()
    for xml_file in glob.glob(os.path.join(xml_directory, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        revenue = root.find(predict)

        basename = os.path.basename(xml_file)
        movie = os.path.splitext(basename)[0]
        
        earnings[movie] = money_to_float(revenue.text)

        date_str = root.find("release_date").text
        date = datetime.datetime.strptime(date_str, "%B %d, %Y")
        origin = root.find("origins/origin")
        budget = root.find("production_budget")
        num_screens = root.find("number_of_screens")
        genre = root.find("genres/genre")
        rating = root.find("rating")
        running_time = root.find("running_time")
        running_time = running_time.text.replace("minutes", "").replace(",","")

        if budget is not None:
            budget = math.log(money_to_float(budget.text))
        else:
            budget = 0
            
        if origin.text == "USA":
            origin  = "USA"
        else:
            origin = "foreign"

        try:
            running_time = int(running_time)
        except:
            running_time = 0

        metadata.at[movie, "date"] = str(date.year)
        metadata.at[movie, "origin"] = origin
        metadata.at[movie, "budget"] = budget
        metadata.at[movie, "screens"] = int(num_screens.text.replace(",", ""))
        metadata.at[movie, "genre"] = genre.text
        metadata.at[movie, "rating"] = rating.text
        metadata.at[movie, "running_time"] = running_time

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

def check_data(earnings, texts, metadata, use_metadata):
    complete = set(earnings.keys())
    if texts:
        for dataset in texts:
            complete = complete.intersection(dataset.keys())
    if use_metadata:
        missing_data = metadata[metadata.isnull().any(axis=1)]
        complete = complete.difference(list(missing_data.index))
    return complete
        

def money_to_float(money):
    clean_str = money.strip("$").replace(",", "")
    return float(clean_str)

def get_earning_features(earnings, order):
    features = []
    for movie in order:
        revenue = earnings[movie]
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
        date = metadata.loc[movie, "date"]
        if date in test_years:
            test_movies.add(movie)
    train = movies.difference(test_movies)
    return list(train), list(test_movies)

def get_metadata_features(movies, metadata):
    features = []
    dummies = pandas.get_dummies(
        metadata, columns=["date", "origin", "genre", "rating"]
    )

    for movie in movies:
        feature = dummies.loc[movie]
        features.append(scipy.sparse.csr_matrix(feature.values))
    return scipy.sparse.vstack(features)

@argh.arg("-t", "--text-directories", nargs="+")
def main(xml_directory, text_directories=None, use_metadata=False,
         max_ngrams=3, seed=1, min_ngrams=1, stop_words=None,
         max_features=20000, count=False, dump_movies=None,
         import_movies=None, predict="weekend_gross"):

    print(sys.argv[1:])

    if not text_directories and not use_metadata:
        print("need to use either text or metadata")
        sys.exit(0)
    
    earnings, metadata = get_metadata(xml_directory, predict)

    texts = []
    if text_directories:
        texts = get_texts(earnings.keys(), text_directories)
        
    complete_movies = check_data(earnings, texts, metadata, use_metadata)

    if import_movies:
        complete_movies = set()
        with open(import_movies) as handle:
            for line in handle:
                complete_movies.add(line.rstrip())

    if dump_movies:
        with open(dump_movies, 'w') as handle:
            for movie in complete_movies:
                print(movie, file=handle)
                
    num_total = len(earnings.keys())
    num_complete = len(complete_movies)
    print("{0} movies used out of {1} total".format(num_complete, num_total))

    train_data, test_data = train_test_split(complete_movies, metadata, ["2009"])

    if seed:
        random.seed(seed)
        
    random.shuffle(list(train_data))
    random.shuffle(list(test_data))

    dev_size = int(len(train_data)/5)

    dev_data = train_data[:dev_size]
    train_data = train_data[dev_size:]


    print("movies in training set: ", len(train_data))
    print("movies in dev set: ", len(dev_data))
    print("movies in test set: ", len(test_data))

    
    train_earning_features = get_earning_features(earnings, train_data) 
    dev_earning_features = get_earning_features(earnings, dev_data)
    test_earning_features = get_earning_features(earnings, test_data)

    if text_directories:
        train_text_datasets = text_to_datasets(texts, train_data)
        dev_text_datasets = text_to_datasets(texts, dev_data)
        test_text_datasets = text_to_datasets(texts, test_data)    
    
        print("fitting vectorizer...")
        vectorizer = fit_vectorizers(
            train_text_datasets, min_ngrams, max_ngrams, max_features,
            stop_words, count)

        print("extracting text features...")
        
        train_text_features = get_text_features(vectorizer, train_text_datasets)
        dev_text_features = get_text_features(vectorizer, dev_text_datasets)
        test_text_features = get_text_features(vectorizer, test_text_datasets)

    if use_metadata:
        print("extracting metadata features...")
        train_metadata_features = get_metadata_features(train_data, metadata)    
        dev_metadata_features = get_metadata_features(dev_data, metadata)        
        test_metadata_features = get_metadata_features(test_data, metadata)

    if use_metadata and text_directories:
        train_features = scipy.sparse.hstack([train_metadata_features, train_text_features])
        dev_features = scipy.sparse.hstack([dev_metadata_features, dev_text_features])
        test_features = scipy.sparse.hstack([test_metadata_features, test_text_features])

    elif text_directories:
        train_features = train_text_features
        dev_features = dev_text_features
        test_features = test_text_features

    elif use_metadata:
        train_features = train_metadata_features
        dev_features = dev_metadata_features
        test_features = test_metadata_features
        
    print("training...")
    trained_model = train(train_features, train_earning_features,
                          dev_features, dev_earning_features)

    print("testing...")
    mae, r2 = test(trained_model, test_features, test_earning_features)
    print("MAE: ", mae)
    print("r2: ", r2)

if __name__ == "__main__":
    argh.dispatch_command(main)
