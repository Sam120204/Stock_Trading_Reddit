from pymongo import MongoClient
import config
import logging

def clean_up_real_time_prices():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db['real_time_prices']

    tickers = collection.distinct('ticker')
    
    for ticker in tickers:
        # Find the most recent entry for the ticker
        latest_entry = collection.find_one(
            {'ticker': ticker},
            sort=[('date', -1)]
        )
        
        # Delete all entries for the ticker except the most recent one
        collection.delete_many(
            {'ticker': ticker, '_id': {'$ne': latest_entry['_id']}}
        )

        logging.info(f"Cleaned up ticker: {ticker}, kept entry with date: {latest_entry['date']}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    clean_up_real_time_prices()
