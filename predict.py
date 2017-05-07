#!/usr/bin/env python3


import scipy.io as sio
import numpy
from sklearn import linear_model
import argh
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import xml.etree.ElementTree as ET
import itertools
import scipy
import glob
import os


def get_text_features(datasets, max_ngram):

    vectorizer = TfidfVectorizer(
        input="filename", ngram_range=(1, max_ngram), min_df=1, max_features=20000,
        decode_error="ignore")

    vectorizer.fit(itertools.chain(*datasets))
    
    ngram_features = []
    for dataset in datasets:
        ngram_features.append(vectorizer.transform(dataset))

    return scipy.sparse.hstack(ngram_features)
        

def train(train_x, train_y):
    elastic_net = linear_model.ElasticNetCV()
    elastic_net.fit(train_x, train_y)
    return elastic_net


def test(elastic_net, test_x, test_y):
    values = elastic_net.predict(test_x)
    mae = 0
    mean = sum(test_y) / len(test_y)
    mae_null = 0
    for index in range(len(values)):
        predicted_value = values[index]
        true_value = test_y[index]
        mae += abs(predicted_value - true_value)
        mae_null += abs(true_value - mean)
    print("mae null: ", mae_null)
    return mae/len(values)
    

def read_data(train_x, train_y, test_x, test_y):
    train_x_data = sio.mmread(train_x)
    train_y_data = numpy.fromfile(train_y, sep="\n")

    test_x_data = sio.mmread(test_x)
    test_y_data = numpy.fromfile(test_y, sep="\n")

    print("data have been read")

    trained_elastic_net = train(train_x_data, train_y_data)
    print("trained on training data")

    mae = test(trained_elastic_net, test_x_data, test_y_data)
    print("tested on test data")
    print("MAE: ", mae)
    return revenue

def get_metadata(xml_directory):
    earnings = {}
    metadata = {}
    for xml_file in glob.glob(os.path.join(xml_directory, "*.xml")):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        revenue = root.find("US_Gross")
        basename = os.path.basename(xml_file)
        movie = os.path.splitext(basename)[0]
        earnings[movie] = revenue.text
        metadata[movie] = None
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
    num_total = len(earnings.keys())
    num_complete = len(complete)
    print("{0} movies used out of {1} total".format(num_complete, num_total))
    return complete
        

def get_earning_features(earnings, order):
    features = []
    for movie in order:
        revenue_str = earnings[movie]
        clean_str = revenue_str.strip("$").replace(",", "")
        revenue = float(clean_str)
        features.append(revenue)
    return features

def text_to_features(texts, order, ngrams):
    features = [ [] for i in range(len(texts))]
    for movie in order:
        for i, dataset in enumerate(texts):
            feature = dataset[movie]
            features[i].append(feature)
            if not os.path.exists(feature):
                print("Missing file: {0}".format(feature))
    matrix = get_text_features(features, ngrams)
    return matrix

@argh.arg("-t", "--text-directories", nargs="+")
def main(xml_directory, text_directories=None, metadata=False, ngrams=3):
    earnings, movie_metadata = get_metadata(xml_directory)
    texts = get_texts(earnings.keys(), text_directories)
    complete_movies = check_data(earnings, movie_metadata, texts, metadata)
    order = sorted(complete_movies)

    print("extracting features...")
    earning_features = get_earning_features(earnings, order)
    text_features = text_to_features(texts, order, ngrams)
    print("training...")
    train(text_features, earning_features)


if __name__ == "__main__":
    argh.dispatch_command(main)
