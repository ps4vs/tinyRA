# tinyRA
# TODO make it asyncronous

# given a search topic, extract relevant authors from twitter, and rank authors

# get all the relevant tweets from the authors, and extract the claims made in each tweet.

# given the claims, create the graph based on these claims, and associated query.

# can make crawl and extract asyncronous, look into it.


# change the prompt accordinly to allow extracting claims made the particular author alone, instead of all the claims.

# we can launch the chromadb collection on docker container.

# start your chromadb client using
`chroma run --path ./data/[research_topic]`