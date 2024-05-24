from src.data_collection.reddit_client import fetch_posts_comments
from src.data_preprocessing.preprocessing import preprocess_data, add_sentiment
from src.feature_engineering.feature_engineering import create_features
from src.model_training.training import train_model
from src.database.database import save_data_to_mongo

def main():
    buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']
    tickers = ['AAPL', 'TSLA', 'AMZN', 'MSFT', 'GOOGL', 'FB', 'NFLX', 'NVDA', 'AMD', 'INTC']


    # Step 1: Fetch posts and comments
    raw_data = fetch_posts_comments(tickers, buy_sell_keywords, days=30, limit=100)
    print(f"Fetched {len(raw_data)} posts and comments.")

    # Check if raw_data has enough samples
    if len(raw_data) < 10:  # Adjust this number based on your requirement
        print("Not enough data fetched. Please ensure more data is collected.")
        return

    # Step 2: Preprocess the data
    processed_data = preprocess_data(raw_data)
    processed_data = add_sentiment(processed_data)
    
    # Display processed data
    # print("Processed Data:")
    # print(processed_data.head())

    # Step 3: Create features and add target column
    features_data = create_features(processed_data)

    # Display feature data
    print("Features Data:")
    print(features_data.head())
    
    
    # Check if features_data has enough samples
    if len(features_data) < 10:  # Adjust this number based on your requirement
        print("Not enough processed data. Please ensure more data is available after preprocessing.")
        return

    # Step 4: Train model
    model = train_model(features_data)

    # Step 5: Save data to MongoDB
    save_data_to_mongo(features_data)

if __name__ == "__main__":
    main()
