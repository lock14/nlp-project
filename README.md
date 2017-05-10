# nlp-project


## Setup
You'll need to download the data from Joshi et al.

       wget https://www.cs.cmu.edu/~ark/movie$-data/movies-data-v1.0.tar.gz
       tar xvzf movies-data-v1.0.tar.gz

You'll want to install this package with Python3.

       pip3 install . --user

And convert the reviews from xml into raw text.

    xml_to_txt.py movies-data-v1.0/reviews/*/*.xml -o data/reviews
    
## Run

To make a prediction about movie weekend gross using text, do:

   predict.py movies-data-v1.0/metacritic+starpower+holiday+revenue+screens+reviews/ -t data/reviews  --max-ngrams 1 --seed 1 --max-features 100 --count