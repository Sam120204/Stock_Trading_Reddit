# combined_data_preparation.py
import pandas as pd
from pymongo import MongoClient
from real_time_stock import update_real_time_prices
from gpt_sentiment import analyze_sentiment
import config

def fetch_sentiment_data():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db[config.COLLECTION_NAME]
    data = list(collection.find())
    for item in data:
        text = item.get('text', '')
        sentiment = analyze_sentiment(text)
        item['sentiment'] = sentiment
    return pd.DataFrame(data)

def combine_data():
    real_time_prices = update_real_time_prices()
    sentiment_data = fetch_sentiment_data()
    # Merge on ticker symbol
    combined_data = pd.merge(real_time_prices, sentiment_data, on='ticker', how='inner')
    return combined_data

# Example usage
if __name__ == "__main__":
    combined_data = combine_data()
    print(combined_data)
