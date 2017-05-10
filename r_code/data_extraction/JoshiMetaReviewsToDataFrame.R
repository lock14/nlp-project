# Extracts Meta Data features from XML into an R data frame
# Requires current working directory to be the directory with all
# the xml files that contain the meta data features

library(XML)

name = NULL
company = NULL
release_date = NULL
running_time = NULL
rating = NULL
US_Gross = NULL
weekend_gross = NULL
number_of_screens = NULL
review_text =  NULL

for (file in list.files("./metacritic+starpower+holiday+revenue+screens+reviews")) {
    # meta data features
    xf <- xmlParse(paste("./metacritic+starpower+holiday+revenue+screens+reviews/", file, sep=""))
    name <- c(name, xmlValue(getNodeSet(xf, "//name")[[1]]))
    company <- c(company, xmlValue(getNodeSet(xf, "//company")[[1]]))
    release_date <- c(release_date, xmlValue(getNodeSet(xf, "//release_date")[[1]]))
    running_time <- c(running_time, xmlValue(getNodeSet(xf, "//running_time")[[1]]))
    rating <- c(rating, xmlValue(getNodeSet(xf, "//rating")[[1]]))
    US_Gross <- c(US_Gross, as.numeric(gsub(',', '', sub('\\$','', xmlValue(getNodeSet(xf, "//US_Gross")[[1]])))))
    weekend_gross <- c(weekend_gross, as.numeric(gsub(',', '', sub('\\$','', xmlValue(getNodeSet(xf, "//weekend_gross")[[1]])))))
    number_of_screens <- c(number_of_screens, xmlValue(getNodeSet(xf, "//number_of_screens")[[1]]))                      
    
    # reviews xml files
    review_concat <- ""

    review_file <- paste("./reviews/www.austinchronicle.com/", file, sep="")
    if (file.exists(review_file)) {
        au_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(au_xf, "//text")[[1]]), sep="")
    }
    
    review_file <- paste("./reviews/www.boston.com/", file, sep="")
    if (file.exists(review_file)) {
        bo_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(bo_xf, "//text")[[1]]), sep="")
    }
    
    review_file <- paste("./reviews/www.calendarlive.com/", file, sep="")
    if (file.exists(review_file)) {
        ca_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(ca_xf, "//text")[[1]]), sep="")
    }

    review_file <- paste("./reviews/www.ew.com/", file, sep="")
    if (file.exists(review_file)) {
        ew_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(ew_xf, "//text")[[1]]), sep="")
    }

    review_file <- paste("./reviews/www.nytimes.com/", file, sep="")
    if (file.exists(review_file)) {
        ny_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(ny_xf, "//text")[[1]]), sep="")
    }

    review_file <- paste("./reviews/www.variety.com/", file, sep="")
    if (file.exists(review_file)) {
        va_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(va_xf, "//text")[[1]]), sep="")
    }

    review_file <- paste("./reviews/www.villagevoice.com/", file, sep="")
    if (file.exists(review_file)) {
        vi_xf <- xmlParse(review_file)
        review_concat <- paste(review_concat, xmlValue(getNodeSet(vi_xf, "//text")[[1]]), sep="")
    }

    review_text <- c(review_text, review_concat)
}

meta_review = data.frame(name, company, release_date, running_time, rating, US_Gross, weekend_gross, number_of_screens, review_text, stringsAsFactors=FALSE)

