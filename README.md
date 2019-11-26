# nlp-project
Do to our inexperience with using regression tools we intially built protypes in both
R and python. We used the protypes to test if they were giving similar results. Once
we were confident that our protypes were working correctly we abandoned the R code
and refined the python code to support the full range of experiments we wanted to
perform. The R code has been included, as a novelty mostly, in the "r_code" directory
along with some of the trace files for the intial R experiments we did. Since the
main project uses the python code we will only discuss how to setup and run that
version of the code.

## Setup
To download the data from Joshi et al:
```
$ wget "https://www.cs.cmu.edu/~ark/movie\$-data/movies-data-v1.0.tar.gz"
$ tar xvzf movies-data-v1.0.tar.gz
```
Next, convert the reviews from xml into raw text:
```
$ ./bin/xml_to_txt.py movies-data-v1.0/reviews/*/*.xml -o data/reviews
```

To download the subtitle data:
```
$ svn export https://github.com/lock14/nlp-project/trunk/data/subtitles data/subtitles
```

To install the necessary python dpenedencies run the following command:
```
$ pip3 install . --user
```
    
## Run

To make a prediction about movie weekend gross using text, do:

   predict.py movies-data-v1.0/metacritic+starpower+holiday+revenue+screens+reviews/ -t data/reviews  --max-ngrams 1 --seed 1 --max-features 100 --count

The script "./run_experiments.sh" runs the experiments. It requires Gnu parallel as a dependecy. Installation of Gnu parallel will dpeend on your distribution.
To run the experiments:
```
$ ./run_experiments.sh
```

A copy of the trace files from running the experiments has been included in the "trace_files" directory.
