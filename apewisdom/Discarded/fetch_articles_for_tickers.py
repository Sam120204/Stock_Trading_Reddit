# fetch_articles_for_tickers.py
from apewisdom.Discarded.fetch_tickers import fetch_tickers_from_mongo
from apewisdom.Discarded.fetch_articles import fetch_articles
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def fetch_articles_for_tickers():
    tickers = fetch_tickers_from_mongo()
    all_articles = {}
    for ticker in tickers:
        query = f"{ticker} stock news"
        articles = fetch_articles(query)
        all_articles[ticker] = articles
        logging.info(f"Fetched {len(articles)} articles for {ticker}")
    return all_articles

# Example usage
if __name__ == "__main__":
    articles = fetch_articles_for_tickers()
    for ticker, articles_list in articles.items():
        print(f"Articles for {ticker}:")
        for article in articles_list:
            print(article)
