import requests

def get_trending_stocks(filter='all-stocks', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']  # Assuming the results are in 'results' key
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

# Example usage
if __name__ == "__main__":
    trending_stocks = get_trending_stocks()
    for stock in trending_stocks:
        print(f"Stock: {stock['ticker']}, Mentions: {stock['mentions']}")
