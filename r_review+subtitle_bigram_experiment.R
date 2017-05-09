library(text2vec)
library(data.table)
library(glmnet)
library(tm)

trace_file <- "./trace_files/r_review+subtitle_bigram_experiment.txt"

load(file="data/rdata/meta+review.RData")
load(file="data/rdata/meta+subtitle.RData")
name <- meta_review$name
company <- meta_review$company
release_date <- meta_review$release_date
running_time <- meta_review$running_time
rating <- meta_review$running_time
US_Gross <- meta_review$US_Gross
weekend_gross <- meta_review$weekend_gross
number_of_screens <- meta_review$number_of_screen
review_subtitle <- paste(meta_review$review_text, meta_subtitle$subtitle_text)
meta_review_subtitle <- data.frame(name, company, release_date, running_time, rating, US_Gross, weekend_gross, number_of_screens, review_subtitle, stringsAsFactors=FALSE)
setDT(meta_review_subtitle)

# allocate train, dev, and test sets
write("Allocating train and test sets...", file = trace_file, append = TRUE)
meta_train <- meta_review_subtitle[grep("200[5678]", meta_review_subtitle$release_date)]
meta_test <- meta_review_subtitle[grep("2009", meta_review_subtitle$release_date)]

# create document term matrix (dtm) for train set
stop_words = c("a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were", "will", "with")
prep_fun <- function(x) {
    x <- removePunctuation(x)
    x <- tolower(x)
    x <- stemDocument(x)
    x
} 
tok_fun = word_tokenizer

write("Creating vocabulary...", file = trace_file, append = TRUE)
it_train = itoken(meta_train$review_subtitle, preprocessor = prep_fun, tokenizer = tok_fun, progressbar = FALSE)
vocab = create_vocabulary(it_train, ngram = c(2L, 2L), stopwords = stop_words)
vocab = vocab %>% prune_vocabulary(max_number_of_terms = 10000)
bigram_vectorizer = vocab_vectorizer(vocab)
write("Creating train document term matrix...", file = trace_file, append = TRUE)
dtm_train = create_dtm(it_train, bigram_vectorizer)

# create document term matrix (dtm) for test set
it_test = itoken(meta_test$review_subtitle, preprocessor = prep_fun, tokenizer = tok_fun, progressbar = FALSE)
write("Creating test document term matrix...", file = trace_file, append = TRUE)
dtm_test = create_dtm(it_test, bigram_vectorizer)

# do regression. Fencepost situation, do first training outside of loop
write("Begin Training:", file = trace_file, append = TRUE)
alpha = 0.05
min_fit = cv.glmnet(x = dtm_train, y = meta_train[['weekend_gross']], family = "gaussian", alpha = 0.05, type.measure = "mae")
write(sprintf("min MAE (alpha %f) = %f", 0.05, round(min(min_fit$cvm), 4)), file = trace_file, append = TRUE)
for (i in c(0.1, 0.15, 0.2, 0.25,  0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1)) {
    fit = cv.glmnet(x = dtm_train, y = meta_train[['weekend_gross']], family = "gaussian", alpha = i, type.measure = "mae")
    write(sprintf("min MAE (alpha %f) = %f", i, round(min(fit$cvm), 4)), file = trace_file, append = TRUE)
    if (min(fit$cvm) <= min(min_fit$cvm)) {
        alpha <- i
        min_fit <- fit
    }
}
write(sprintf("Best Model: alpha = %f, lambda = %f", alpha, min_fit$lambda.min), file = trace_file, append = TRUE)

# prediction: Metrics libary conflicts with others,
# load it here instead of at beginning to avoid conflicts
library(Metrics)
y_actual = meta_test$weekend_gross
write("Creating predictions on test data", file = trace_file, append = TRUE)
y_prediction = predict(min_fit, dtm_test, type = 'response', s = "lambda.min")[,1]
prediction_mae = mae(y_actual, y_prediction)
write(sprintf("Prediction MAE: %f", prediction_mae), file = trace_file, append = TRUE)

# compute r^2
sst <- sum((y_actual - mean(y_actual))^2)
sse <- sum((y_prediction - y_actual)^2)
r_squared <- 1 - sse / sst
write(sprintf("r^2: %f", r_squared), file = trace_file, append = TRUE)
write(sprintf("r: %f", sqrt(r_squared)), file = trace_file, append = TRUE)
