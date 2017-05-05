library(text2vec)
libraty(data.table)
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

# do regression
glmnet_classifier = cv.glmnet(x = dtm_train, y = meta_train[['US_Gross']], family = "gaussian", alpha = 1, type.measure = "mae", nfolds = 10, thresh = 1e-3, maxit = 1e3)

# not sure what to do now (here's some random stuff)
plot(glmnet_classifier)
print(paste("max MAE =", round(max(glmnet_classifier$cvm), 4)))

# prediction
preds = predict(glmnet_classifier, dtm_test, type = 'response')[,1]
glmnet:::auc(meta_test$US_Gross, preds)
