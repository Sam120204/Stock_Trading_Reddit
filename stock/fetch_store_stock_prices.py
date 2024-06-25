import psycopg2
import yfinance as yf
import dotenv
import os
from datetime import datetime, timedelta

dotenv.load_dotenv()

# PostgreSQL's connection details
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT")
)
cur = conn.cursor()


# Function to round the timestamp to the nearest half-hour
def round_to_nearest_half_hour(dt):
    minutes = dt.minute
    if minutes < 15:
        delta = timedelta(minutes=-minutes)
    elif minutes < 45:
        delta = timedelta(minutes=30 - minutes)
    else:
        delta = timedelta(minutes=60 - minutes)
    return (dt + delta).replace(second=0, microsecond=0)


# Function to get real-time stock price using yfinance
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    todays_data = stock.history(period='1d')
    return todays_data['Close'].iloc[0]


# Function to insert stock price data into PostgreSQL
def insert_stock_price(ticker, price, timestamp):
    cur.execute(
        "INSERT INTO stock_prices (ticker, price, timestamp) VALUES (%s, %s, %s)",
        (ticker, price, timestamp)
    )
    conn.commit()


# List of stock tickers
tickers = ['RDDT', 'GME', 'NVDA', 'RC', 'TSLA', 'AAPL', 'AMZN', 'SPY', 'GOOGL', 'BA', 
           'META', 'ASML', 'MSFT', 'MU', 'INTC', 'NKE', 'HOOD', 'RAMP', 'SPOT', 'QQQ', 
           'VOO', 'AMD', 'PPL', 'ONTO', 'TOON', 'ARM', 'SPY', 'ASML', 'MU', 'EU', 'ICE', 
           'ES', 'AVGO', 'MSFT', 'HPE', 'SPLG', 'GOOG', 'LLY', 'IBM', 'MA', 'NKE',
           'CPA', 'WAY', 'DELL', 'SNOW']

# Fetch and store stock prices
for ticker in tickers:
    try:
        price = get_stock_price(ticker)
        timestamp = round_to_nearest_half_hour(datetime.now())
        insert_stock_price(ticker, price, timestamp)
        print(f"Inserted {ticker}: {price} at {timestamp}")
    except Exception as e:
        print(f"Failed to fetch or insert data for {ticker}: {e}")

# Closing the connection
cur.close()
conn.close()
