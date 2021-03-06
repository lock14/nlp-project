#!/usr/bin/env bash

set -e -o pipefail -u

movies="/home/jon/Data/nlp/project/movies-data-v1.0/metacritic+starpower+holiday+revenue+screens+reviews"
reviews="data/reviews"
subtitles="data/subtitles"

cmd="predict.py ${movies} --seed 1 --import-movies data/movie_subset/minimal_set.txt"
max_ngrams="1 2 3 2 3"
min_ngrams="1 1 1 2 3"
features="10000"

dryrun=""
same_options=" --min-ngrams {1} --max-ngrams {2} --max-features {3} --predict {4}"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${reviews}                              > trace_py/reviews_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${subtitles}                            > trace_py/subtitles_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} --use-metadata                             > trace_py/metadata_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${reviews} ${subtitles}                 > trace_py/reviews_subtitles_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${reviews} --use-metadata               > trace_py/reviews_metadata_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${subtitles} --use-metadata             > trace_py/subtitles_metadata_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
parallel --gnu -j 1 $dryrun "${cmd} ${same_options} -t ${reviews} ${subtitles} --use-metadata  > trace_py/reviews_subtitles_metadata_mingram_{1}_maxgram_{2}_max_features_{3}_{4}.txt" ::: $min_ngrams :::+ $max_ngrams ::: $features ::: "US_Gross" "weekend_gross"
