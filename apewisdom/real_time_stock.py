import yfinance as yf
import pandas as pd
from pymongo import MongoClient
import config
import time

def get_real_time_stock_price(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period='1d')
    if not data.empty:
        price_data = {
            'ticker': ticker,
            'price': data['Close'][0],
            'volume': data['Volume'][0],
            'open': data['Open'][0],
            'high': data['High'][0],
            'low': data['Low'][0],
            'close': data['Close'][0],
            'date': data.index[0]
        }
        return price_data
    else:
        return None

def fetch_tickers_from_mongo():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db[config.COLLECTION_NAME]
    tickers = collection.distinct('ticker')
    return tickers

def update_real_time_prices():
    tickers = fetch_tickers_from_mongo()
    stock_prices = []
    for ticker in tickers:
        try:
            price_data = get_real_time_stock_price(ticker)
            if price_data:
                stock_prices.append(price_data)
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    return pd.DataFrame(stock_prices)

def save_real_time_prices_to_mongo(prices_df):
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db['real_time_prices']
    records = prices_df.to_dict('records')
    collection.insert_many(records)

def main():
    while True:
        real_time_prices = update_real_time_prices()
        save_real_time_prices_to_mongo(real_time_prices)
        time.sleep(1800)

if __name__ == "__main__":
    main()
