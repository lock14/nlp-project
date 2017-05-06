library(text2vec)
library(data.table)
library(glmnet)

load(file="data/rdata/meta+review.RData")
setDT(meta_review)

# allocate train, dev, and test sets
meta_train <- meta_review[grep("200[567]", meta_review$release_date)]
meta_dev <- meta_review[grep("2008", meta_review$release_date)]
meta_test <- meta_review[grep("2009", meta_review$release_date)]

# create document term matrix (dtm) for train set
stop_words = c("a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to", "was", "were", "will", "with")
prep_fun = tolower
tok_fun = word_tokenizer

it_train = itoken(meta_train$review_text, preprocessor = prep_fun, tokenizer = tok_fun, progressbar = FALSE)
vocab = create_vocabulary(it_train, ngram = c(1L, 2L), stopwords = stop_words)
vocab = vocab %>% prune_vocabulary(term_count_min = 10, doc_proportion_max = 0.5)
bigram_vectorizer = vocab_vectorizer(vocab)
dtm_train = create_dtm(it_train, bigram_vectorizer)

# create document term matrix (dtm) for test set
it_test = itoken(meta_test$review_text, preprocessor = prep_fun, tokenizer = tok_fun, progressbar = FALSE)
dtm_test = create_dtm(it_test, bigram_vectorizer)

# do regression. Fencepost situation, do first training outside of loop
min_fit = cv.glmnet(x = dtm_train, y = meta_train[['US_Gross']], family = "gaussian", alpha = 0.05, type.measure = "mae")
print(sprintf("min MAE (alpha %f) = %f", 0.05, round(min(min_fit$cvm), 4)))
for (i in c(0.1, 0.15, 0.2, 0.25,  0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1)) {
    fit = cv.glmnet(x = dtm_train, y = meta_train[['US_Gross']], family = "gaussian", alpha = i, type.measure = "mae")
    print(sprintf("min MAE (alpha %f) = %f", i, round(min(fit$cvm), 4)))
    if (min(fit$cvm) <= min(min_fit$cvm)) {
        min_fit <- fit
    }
}

# prediction: Metrics libary conflicts with others,
# load it here instead of at beginning to avoid conflicts
library(Metrics)
preds = predict(min_fit, dtm_test, type = 'response')[,1]
pred_mae = mae(meta_test$US_Gross, preds)
print(sprintf("Predicttion MAE: %f", pred_mae))
