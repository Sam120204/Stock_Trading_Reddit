# fetch_tickers.py
from pymongo import MongoClient
import config

def fetch_tickers_from_mongo():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db[config.COLLECTION_NAME]
    tickers = collection.distinct('ticker')
    return tickers

# Example usage
if __name__ == "__main__":
    tickers = fetch_tickers_from_mongo()
    print(tickers)
