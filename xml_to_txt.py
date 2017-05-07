#!/usr/bin/env python3

import argh
import os
import glob
import sys
import xml.etree.ElementTree as ET


def parse_text(review_file):
    tree = ET.parse(review_file)
    root = tree.getroot()
    text = root.find("review/text")
    return text.text

def write_text(output_file):
    pass

@argh.arg("review_files", nargs="+")
@argh.arg("-o", "--output-dir")
def main(review_files, output_dir="reviews", force=False):

    reviews = {}
    for review_file in review_files:
        basename = os.path.basename(review_file)
        movie = os.path.splitext(basename)[0]
        text = parse_text(review_file)
        reviews.setdefault(movie, []).append(text)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
        
    for movie, texts in reviews.items():
        outfile = os.path.join(output_dir, movie + ".txt")
        if not force:
            if os.path.exists(outfile):
                print("Warning: file ", outfile, " exists.")
                sys.exit(1)
                
        text = "\n".join(texts)
        with open(outfile, 'w') as out_handle:
            out_handle.write(text)


if __name__ == "__main__":
    argh.dispatch_command(main)
