# Extracts Meta Data features from XML into an R data frame
# Requires current working directory to be the directory with all
# the xml files that contain the meta data features
# also extracts subtitles text. Assumed subtitles for the intersection
# of the joshi movies, and the subtitles movies we collected, was put
# in a directoy called "common_subs"

library(XML)
library(readr)

name = NULL
company = NULL
release_date = NULL
running_time = NULL
rating = NULL
US_Gross = NULL
weekend_gross = NULL
number_of_screens = NULL
subtitle_text =  NULL

for (file in list.files("./common_subs")) {
    # meta data features
    xml_file = paste("./metacritic+starpower+holiday+revenue+screens+reviews/", sub(".txt", ".xml", file), sep = "")
    xf <- xmlParse(xml_file)
    name <- c(name, xmlValue(getNodeSet(xf, "//name")[[1]]))
    company <- c(company, xmlValue(getNodeSet(xf, "//company")[[1]]))
    release_date <- c(release_date, xmlValue(getNodeSet(xf, "//release_date")[[1]]))
    running_time <- c(running_time, xmlValue(getNodeSet(xf, "//running_time")[[1]]))
    rating <- c(rating, xmlValue(getNodeSet(xf, "//rating")[[1]]))
    US_Gross <- c(US_Gross, as.numeric(gsub(',', '', sub('\\$','', xmlValue(getNodeSet(xf, "//US_Gross")[[1]])))))
    weekend_gross <- c(weekend_gross, as.numeric(gsub(',', '', sub('\\$','', xmlValue(getNodeSet(xf, "//weekend_gross")[[1]])))))
    number_of_screens <- c(number_of_screens, xmlValue(getNodeSet(xf, "//number_of_screens")[[1]]))                      
    
    # substitle file
    sub_file <- paste("./common_subs/", file, sep="")
    subtitle <- iconv(enc2utf8(read_file(sub_file)), sub = "byte")
    subtitle_text <- c(subtitle_text, subtitle)
}

meta_subtitle = data.frame(name, company, release_date, running_time, rating, US_Gross, weekend_gross, number_of_screens, subtitle_text, stringsAsFactors=FALSE)
