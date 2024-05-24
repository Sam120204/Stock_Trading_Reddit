import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.data_collection.reddit_client import fetch_posts_comments
from src.data_preprocessing.preprocessing import preprocess_data, add_sentiment
from src.feature_engineering.feature_engineering import create_features
from src.model_training.training import train_model
from src.database.database import save_data_to_mongo

def main():
    tickers = ['AAPL', 'TSLA', 'AMZN']
    buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']
    
    # Fetch posts and comments
    raw_data = fetch_posts_comments(tickers, buy_sell_keywords)
    
    # Preprocess data
    processed_data = preprocess_data(raw_data)
    processed_data = add_sentiment(processed_data)
    
    # Create features
    features_data = create_features(processed_data)
    
    # Train model
    model = train_model(features_data)
    
    # Save data to MongoDB
    save_data_to_mongo(features_data)

if __name__ == "__main__":
    main()
