# fetch_articles.py
from newsapi import NewsApiClient
import logging
import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key=config.NEWSAPI_KEY)

def fetch_articles(query):
    try:
        response = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=20)
        if response['status'] != 'ok':
            logging.error(f"Error fetching articles for {query}: {response['message']}")
            return []

        articles = []
        for article in response['articles']:
            articles.append({
                'title': article['title'],
                'snippet': article['description'],
                'link': article['url']
            })

        logging.info(f"Fetched {len(articles)} articles for {query}")
        return articles
    except Exception as e:
        logging.error(f"Exception occurred while fetching articles for {query}: {e}")
        return []

# Example usage
if __name__ == "__main__":
    query = "Apple stock news"
    articles = fetch_articles(query)
    for article in articles:
        print(article)
