import finnhub
from datetime import datetime

# Initialize the Finnhub client with your API key
api_key = 'key'
finnhub_client = finnhub.Client(api_key=api_key)

# Define the date range
start_date = '2024-10-01'
end_date = datetime.today().strftime('%Y-%m-%d')

# Fetch insider sentiment data
data = finnhub_client.stock_insider_sentiment('AAPL', start_date, end_date)

# Check if data is available
if 'data' in data and data['data']:
    print(f"Insider Sentiment for {data['symbol']} from {start_date} to {end_date}:")
    print("--------------------------------------------------")
    for entry in data['data']:
        year = entry['year']
        month = entry['month']
        change = entry['change']
        mspr = entry['mspr']
        date_str = f"{year}-{month:02d}"
        print(f"Date: {date_str}")
        print(f"  Net Change in Shares: {change}")
        print(f"  MSPR: {mspr}")
        print("----")
else:
    print(f"No insider sentiment data available for {symbol} in the specified date range.")
