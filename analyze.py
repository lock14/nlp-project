#!/usr/bin/env python3


import scipy.io as sio
import numpy
from sklearn import linear_model
import argh



def train(train_x, train_y):
    elastic_net = linear_model.ElasticNetCV()
    elastic_net.fit(train_x, train_y)
    return elastic_net

def test(elastic_net, test_x, test_y):
    values = elastic_net.predict(test_x)
    mae = 0
    for index in range(len(values)):
        predicted_value = values[index]
        true_value = test_y[index]
        mae += abs(predicted_value - true_value)
    return mae/len(values)
    

def main(train_x, train_y, test_x, test_y):
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
    
if __name__ == "__main__":
    argh.dispatch_command(main)
