import yfinance as yf

def fetch_stock_price_long_term(tickers, period="5y"):
    all_data = {}
    for ticker in tickers:
        data = yf.download(ticker, period=period)
        all_data[ticker] = data
        data.to_csv(f"{ticker}_long_term.csv")
        print(f"Data for {ticker} saved to {ticker}_long_term.csv")
    return all_data

if __name__ == "__main__":
    tickers = ["AAPL"]
    data = fetch_stock_price_long_term(tickers)
    for ticker, df in data.items():
        print(f"\n{ticker} data:")
        print(df.head())
