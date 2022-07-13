# server.R

#* Return a chord diagram htmlwidget
#* @serializer htmlwidget
#* @param req
#* @post /chord
function(req) {
  df <- as.data.frame(jsonlite::fromJSON(req$postBody))
  df <- tidyr::drop_na(df)
  colnames(df) <- c("feature_x", "feature_y", "n")
  ct <- tidyr::spread(df, 2, 3)
  ct <- tibble::column_to_rownames(ct, var = "feature_x")
  # create data matrix
  dm <- ct# [-1]
  # row.names(dm) <- ct[1] # colnames(dm)
  chorddiag::chorddiag(data.matrix(dm), 
                       showTicks=F, 
                       # type="bipartite", 
                       palette="Set2", 
                       # palette2="Set3",
                       margin=150,
                       groupnameFontsize = 12,
                       groupnamePadding = 5)
}


#* Return a wordcloud htmlwidget
#* @serializer htmlwidget
#* @param req
#* @post /wordcloud
function(req) {
  df <- as.data.frame(jsonlite::fromJSON(req$postBody))
  df <- tidyr::drop_na(df)
  wordcloud::wordcloud(df$word, df$freq)
} 