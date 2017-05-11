#!/usr/bin/env python3

import os
import argh
import glob
import csv
import matplotlib.pyplot as plt
import itertools
import seaborn as sns


def plot(curves, labels, outfile, xlabel, ylabel, x_is_label=False):
    sns.set_palette("colorblind")
    figure = plt.figure()
    for i, curve in enumerate(curves):
        label = labels[i]
        x, y = curve
        if x_is_label:
            x_labels = x
            x = range(len(y))
            plt.xticks(x, x_labels)
        print(label, x, y, xlabel, ylabel)
        plt.plot(x, y, label=label)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout(rect=[0,0,0.65,1])
    plt.savefig(outfile, dpi=900)

def get_data_types(parts):
    data_types = []
    for part in parts:
        if part == "mingram":
            break
        data_types.append(part)
    return data_types

def get_ngrams(parts):
    prev = mingram = maxgram = None    
    for part in parts:
        if prev == "mingram":
            mingram = int(part)
        if prev == "maxgram":
            maxgram = int(part)
        prev = part
    return mingram, maxgram

def get_predict_type(parts):
    predict = None
    prev = None
    for part in parts:
        if "ross.txt" in part:
            return prev
        prev = part

def get_results(filename):
    with open(filename) as handle:
        for line in handle:
            if "MAE" in line:
                mae = float(line.split()[1])
            if "r2" in line:
                r2 = float(line.split()[1])
    return mae, r2

def get_feature_size(parts):
    

def get_experiment_data(trace_dir):
    search = os.path.join(trace_dir, "*.txt")
    data = []
    for filename in glob.glob(search):
        basename = os.path.basename(filename)
        parts = basename.split("_")
        data_type = get_data_types(parts)
        mae, r2 = get_results(filename)
        mingram, maxgram = get_ngrams(parts)
        predict = get_predict_type(parts)

        data_obj = DataObj(data_type, mingram, maxgram)
        data_obj.add_result(predict, mae, r2)
        
        seen = False
        for prev_obj in data:
            if prev_obj.name == data_obj.name:
                if prev_obj.mingram == data_obj.mingram:
                    if prev_obj.maxgram == data_obj.maxgram:
                        prev_obj.add_result(predict, mae, r2)
                        seen = True
        if not seen:
            data.append(data_obj)
    
    return data

class DataObj:

    def __init__(self, data_types, mingram, maxgram, feature_size):
        self.data_types = tuple(data_types)
        self.name = self.make_name()
        self.mingram = mingram
        self.maxgram = maxgram
        self.weekend_mae = None
        self.weekend_r2 = None
        self.us_mae = None
        self.us_r2 = None
        
    def make_name(self):
        return "+".join(self.data_types)

    def add_result(self, predict_type, mae, r2):
        if predict_type == "weekend":
            self.weekend_mae = mae
            self.weekend_r2 = r2
        elif predict_type == "US":
            self.us_mae = mae
            self.us_r2 = r2

    def show_data(self):
        data = []
        data.append(self.name)
        data.append(self.mingram)
        data.append(self.maxgram)
        data.append(self.weekend_mae)
        data.append(self.weekend_r2)
        data.append(self.us_mae)
        data.append(self.us_r2)
        return data

def output_csv(data, csv_file):
    if csv_file:
        with open(csv_file, "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for row in data:
                if row.mingram == 1 and row.maxgram == 3:
                    writer.writerow(row.show_data())

def plot_ngram(data, ngram_output, gross, value):
    data_types = set()
    
    for obj in data:
        # only metadata type has no ngram
        if obj.data_types == ["metadata"]:
            continue
        dt = obj.data_types
        data_types.add(dt)

    curves = []
    labels = []
    for data_type in data_types:
        labels.append("+".join(data_type))
        x = []
        y = []
        for mingram in range(1, 4):
            for maxgram in range(mingram, 4):
                if mingram == 2 and maxgram == 3:
                    continue
                x.append("-".join([str(mingram), str(maxgram)]))
                for data_obj in data:
                    if data_obj.data_types != data_type:
                        continue
                    if data_obj.mingram != mingram:
                        continue
                    if data_obj.maxgram != maxgram:
                        continue
                    if gross == "weekend":
                        if value == "r2":
                            y.append(data_obj.weekend_r2)
                        if value == "MAE":
                            y.append(data_obj.weekend_mae)
                    if gross == "US":
                        if value == "r2":
                            y.append(data_obj.us_r2)
                        if value == "MAE":
                            y.append(data_obj.us_mae)
        curves.append([x, y])
    if value == "r2":
        value = r'$r^2$'
    plot(curves, labels, ngram_output, "ngrams used", " ".join([value, "with", gross, "gross"]), x_is_label=True)

def plot_features(data, feature_prefix):
    if not feature_prefix:
        return

    curves = []
    label = []

    for feature_size in [100, 500, 1000, 2000, 4000, 10000]:
        pass
    
def plot_ngrams(data, ngrams_prefix):
    if not ngrams_prefix:
        return
    curves = []
    label = []

    for gross in ["weekend", "US"]:
        for value in ["MAE", "r2"]:
            template = ngrams_prefix + "_{0}_{1}.png"
            ngram_output  = template.format(gross, value)
            plot_ngram(data, ngram_output, gross, value)
                    
def main(trace_dir, csv_file=None, ngrams_prefix=None):
    data = get_experiment_data(trace_dir)
    output_csv(data, csv_file)
    plot_ngrams(data, ngrams_prefix)
    #parse_and_plot(trace_dir, experiment="train")

if __name__ == "__main__":
    argh.dispatch_command(main)
