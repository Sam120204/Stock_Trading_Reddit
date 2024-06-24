import yfinance as yf
import pandas as pd
from pymongo import MongoClient
import datetime
import pytz
import config
import logging
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

def round_to_nearest_half_hour(dt):
    minutes = dt.minute
    if minutes < 15:
        delta = datetime.timedelta(minutes=-minutes)
    elif minutes < 45:
        delta = datetime.timedelta(minutes=30 - minutes)
    else:
        delta = datetime.timedelta(minutes=60 - minutes)
    return (dt + delta).replace(second=0, microsecond=0)


def convert_to_edt(dt):
    utc_zone = pytz.utc
    edt_zone = pytz.timezone('US/Eastern')

    dt_utc = utc_zone.localize(dt)

    dt_edt = dt_utc.astimezone(edt_zone)

    return dt_edt


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
            'date': convert_to_edt(round_to_nearest_half_hour(datetime.datetime.utcnow()))
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
            logging.info(f"Error fetching data for {ticker}: {e}")

    logging.info(f"Real-time stock prices fetched successfully.")
    return pd.DataFrame(stock_prices)


def save_real_time_prices_to_mongo(prices_df):
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    collection = db['real_time_prices']
    records = prices_df.to_dict('records')
    collection.insert_many(records)
    logging.info(f"Real-time prices saved to MongoDB successfully.")
