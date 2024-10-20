import requests

# Your Finnhub API key
api_key = 'key'

# The Finnhub API endpoint for insider transactions
url = 'https://finnhub.io/api/v1/stock/insider-transactions'

# Company symbol for which you want to retrieve insider transactions
symbol = 'MSFT'  # Change this to any other symbol if needed

# Parameters for the API request
params = {
    'symbol': symbol,
    'token': api_key
}

# Make the API request
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    data = response.json()
    print(f"Insider Transactions for {data.get('symbol')}:")
    print("--------------------------------------------------")
    # Process and print the data
    for transaction in data.get('data', []):
        print(f"Name: {transaction['name']}")
        print(f"Transaction Date: {transaction['transactionDate']}")
        print(f"Transaction Code: {transaction['transactionCode']}")
        print(f"Shares Changed: {transaction['change']}")
        print(f"Transaction Price: {transaction['transactionPrice']}")
        print(f"Remaining Shares: {transaction['share']}")
        print(f"Filing Date: {transaction['filingDate']}")
        print("----")
else:
    print(f"Error: {response.status_code}, {response.text}")
