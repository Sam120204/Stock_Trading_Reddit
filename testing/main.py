import sys
import os

# Add src to sys.path to import modules from src directory
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from data_collection.reddit_client import fetch_posts_comments
from data_preprocessing.preprocessing import preprocess_data, add_sentiment
from feature_engineering.feature_engineering import create_features
from model_training.training import train_model
from database.database import save_data_to_mongo

def main():
    buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']
    tickers = ['AAPL', 'TSLA', 'AMZN']

    # Fetch and preprocess data
    raw_data = fetch_posts_comments(tickers, buy_sell_keywords)
    save_data_to_mongo(raw_data)
    processed_data = preprocess_data(raw_data)
    processed_data = add_sentiment(processed_data)

    # Create features and train model
    features_data = create_features(processed_data)
    train_model(features_data)

if __name__ == "__main__":
    main()
