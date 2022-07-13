FROM rstudio/plumber

# install pandoc for htmlwidgets
RUN apt-get update -q && apt-get install -y pandoc
      
# change working directory
WORKDIR /app

# R packages
RUN R -e "install.packages('tidyr')"
RUN R -e "remotes::install_github('mattflor/chorddiag')"

# copy files
COPY . .

CMD ["server.R"]
