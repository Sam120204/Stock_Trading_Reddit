# Import necessary libraries
import requests
import pandas as pd

# Fetch trending stocks
def fetch_trending_stocks():
    response = requests.get('https://apewisdom.io/api/v1.0/filter/all-stocks/page/1')
    if response.status_code == 200:
        return response.json()['results']
    else:
        return []

# Fetch real-time prices for these stocks (mock example, replace with real API)
def fetch_real_time_prices(tickers):
    prices = {}
    for ticker in tickers:
        prices[ticker] = {"price": 100, "open": 98, "high": 102, "low": 97, "close": 99}  # Mock data
    return prices

# Combine trending stocks and real-time prices
def get_combined_data():
    trending_stocks = fetch_trending_stocks()
    tickers = [stock['ticker'] for stock in trending_stocks]
    prices = fetch_real_time_prices(tickers)
    combined_data = pd.DataFrame(trending_stocks)
    price_data = pd.DataFrame(prices).T
    combined_data = combined_data.merge(price_data, left_on='ticker', right_index=True)
    return combined_data
