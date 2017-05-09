#!/usr/bin/env bash

set -e -o pipefail -u

movies="/home/jon/Data/nlp/project/movies-data-v1.0/metacritic+starpower+holiday+revenue+screens+reviews"
reviews="data/reviews"
subtitles="data/subtitles"

cmd="predict.py ${movies} --seed 1 --max-features 4000"
max_ngrams="1 2 3 2 3"
min_ngrams="1 1 1 2 3"


parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${reviews} > trace_py/reviews_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${subtitles} > trace_py/subtitles_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} --use-metadata > trace_py/metadata_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${reviews} ${subtitles} > trace_py/reviews_subtitles_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${reviews} --use-metadata > trace_py/reviews_metadata_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${subtitles} --use-metadata > trace_py/subtitles_metadata_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
parallel --gnu "${cmd} --min-ngrams {1} --max-ngrams {2} {3} -t ${reviews} ${subtitles} --use-metadata > trace_py/reviews_subtitles_metadata_mingram_{1}_maxgram_{2}.txt" ::: $min_ngrams :::+ $max_ngrams
