# combine_and_store.py
import pandas as pd
from pymongo import MongoClient
import config

def fetch_trending_data():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db[config.COLLECTION_NAME]
    trending_data = list(collection.find())
    return pd.DataFrame(trending_data)

def fetch_real_time_prices():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db['real_time_prices']
    real_time_data = list(collection.find())
    return pd.DataFrame(real_time_data)

def compare_and_store_prices():
    trending_data = fetch_trending_data()
    real_time_data = fetch_real_time_prices()
    
    # Merge data on ticker
    combined_data = pd.merge(trending_data, real_time_data, on='ticker', suffixes=('_trending', '_real_time'))
    
    # Calculate price changes
    combined_data['price_change'] = (combined_data['price_real_time'] - combined_data['price_trending']) / combined_data['price_trending'] * 100
    
    # Store combined data in MongoDB
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db['combined_data']
    collection.insert_many(combined_data.to_dict('records'))
    
    return combined_data

# Example usage
if __name__ == "__main__":
    combined_data = compare_and_store_prices()
    print(combined_data)
