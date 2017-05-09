#!/usr/bin/env bash

set -e -o pipefail -u

movies="/home/jon/Data/nlp/project/movies-data-v1.0/metacritic+starpower+holiday+revenue+screens+reviews"
reviews="data/reviews"
subtitles="data/subtitles"

cmd="predict.py ${movies} --seed 1 "
max_ngrams="1 2 3 2 3"
min_ngrams="1 1 1 2 3"
features="100 500 1000 2000 4000 10000"

parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${reviews}                             --max-features {3} > trace_py/reviews_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${subtitles}                           --max-features {3} > trace_py/subtitles_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} --use-metadata                            --max-features {3} > trace_py/metadata_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${reviews} ${subtitles}                --max-features {3} > trace_py/reviews_subtitles_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${reviews} --use-metadata              --max-features {3} > trace_py/reviews_metadata_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${subtitles} --use-metadata            --max-features {3} > trace_py/subtitles_metadata_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
parallel --gnu -j 1 "${cmd} --min-ngrams {1} --max-ngrams {2} -t ${reviews} ${subtitles} --use-metadata --max-features {3} > trace_py/reviews_subtitles_metadata_mingram_{1}_maxgram_{2}_max_features_{3}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features
