import psycopg2
import yfinance as yf
from datetime import datetime

# PostgreSQL connection details
conn = psycopg2.connect(
    dbname="postgres",
    user="real_priceDB",
    password="12345678",
    host="database-1.cf6gq4cgqxg7.ca-central-1.rds.amazonaws.com",
    port="5432"
)
cur = conn.cursor()

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
           'ES', 'AVGO', 'MSFT', 'HPE', 'SPLG', 'SP', 'GOOG', 'LLY', 'IBM', 'MA', 'NKE', 
           'CPA', 'WAY', 'DELL', 'SNOW']

# Fetch and store stock prices
for ticker in tickers:
    try:
        price = get_stock_price(ticker)
        timestamp = datetime.now()
        insert_stock_price(ticker, price, timestamp)
        print(f"Inserted {ticker}: {price} at {timestamp}")
    except Exception as e:
        print(f"Failed to fetch or insert data for {ticker}: {e}")

# Closing the connection
cur.close()
conn.close()
