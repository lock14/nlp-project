#!/usr/bin/env python3

import argh
import scipy
from sklearn.feature_extraction.text import CountVectorizer
import pathlib


@argh.arg("--subtitles", nargs="+")
@argh.arg("--scripts", nargs="+")
def main(subtitles=None, scripts=None, max_ngram=3, debug=False):
    vectorizer = CountVectorizer(
        input="filename", ngram_range=(1, max_ngram), min_df=1, stop_words="english")


    if subtitles:
        vectorizer.fit(subtitles + scripts)

    subtitle_features = vectorizer.transform(subtitles)

    script_features = vectorizer.transform(scripts)

    features = scipy.sparse.hstack([subtitle_features, script_features]).toarray()
    if debug:
            print(subtitle_features.toarray())
            print(script_features.toarray())
            print()
            print(features)


if __name__ == "__main__":
    argh.dispatch_command(main)
