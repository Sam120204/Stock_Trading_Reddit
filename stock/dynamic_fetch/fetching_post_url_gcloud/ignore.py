import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
POSTS_COLLECTION_NAME = os.getenv('POSTS_COLLECTION_NAME')

# Properly encode the username and password
encoded_username = quote_plus(MONGO_USERNAME)
encoded_password = quote_plus(MONGO_PASSWORD)

# Initialize MongoDB client
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@trendsage.svfhdvw.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&authSource=admin"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts_collection = db[POSTS_COLLECTION_NAME]

# List of terms to ignore as potential tickers
IGNORE_TERMS = [
    "YOLO", "LOL", "FOMO", "TBA", "CEO", "CFO", "PR", "ER", "TA", "ETF", "BTFD", 
    "DD", "ATH", "BULL", "BEAR", "HODL", "PUMP", "DUMP", "STOCKS", "OPTIONS", "TRADING", 
    "MOON", "DIAMOND", "HANDS", "GAINZ", "LOSS", "PROFIT", "CALL", "PUT", "SPAC",
    "WSB", "RED", "GREEN", "BUY", "SELL", "MARGIN", "SHORT", "LONG", "ROCKET", 
    "STONK", "STOCK", "TRADE", "FINANCE", "INVEST", "CRYPTO"
]

def clean_tickers_in_posts(collection):
    for post in collection.find({"tickers": {"$exists": True}}):
        cleaned_tickers = [ticker for ticker in post["tickers"] if ticker not in IGNORE_TERMS]
        collection.update_one({"_id": post["_id"]}, {"$set": {"tickers": cleaned_tickers}})
        print(f"Updated post {post['_id']} with cleaned tickers: {cleaned_tickers}")

def main():
    clean_tickers_in_posts(posts_collection)

if __name__ == "__main__":
    main()
