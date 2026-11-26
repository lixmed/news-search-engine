# News Search Engine

A small web search engine built from scratch: it crawls international news sites, builds an inverted index, ranks pages with PageRank, and serves search results through a Flask API and a Streamlit search page.

## How it works

1. **Crawler** (`scraper.py`): a multithreaded crawler starts from world-news seed pages (CNN, NYT, Washington Post, DW, Global News, CBC, and more), follows links within the allowed domains, extracts article titles and bodies with BeautifulSoup, de-duplicates pages by hash, and stores them in SQLite.
2. **Word counts** (`word_count.py`): term frequencies across the crawled articles.
3. **Inverted index** (`indexer.py`, plus a Java version in `InvertedIndex.java`): maps every word to the documents that contain it, for fast lookups.
4. **PageRank** (`PageRank.py`): builds the link graph between crawled pages with NetworkX and scores each page by importance.
5. **Search API** (`app.py`): a Flask endpoint that looks up query terms in the index, ranks matches using PageRank, and returns titles, URLs, and snippets.
6. **Search UI** (`searchapp.py`): a styled Streamlit search page that calls the API.

## Run

```bash
pip install requests beautifulsoup4 fake-useragent tldextract networkx flask streamlit
python scraper.py        # crawl articles into articles.db
python word_count.py     # optional: term frequencies
python indexer.py        # build inverted_index_en.json
python PageRank.py       # compute pagerank.json
```

Then start both servers (on Windows, `run_all.bat` does this):

```bash
python app.py
streamlit run searchapp.py
```

The crawled database and generated index files are not included in this repo because of their size; the scripts above recreate them.

## Tech

Python · BeautifulSoup · SQLite · multithreading · inverted index · PageRank (NetworkX) · Flask · Streamlit · Java
