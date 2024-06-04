import requests
import logging

logging.basicConfig(level=logging.INFO)

def get_trending_stocks(filter='all-stocks', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        logging.info(f"Fetched data: {data['results']}")
        return data['results']
    else:
        logging.error(f"Error fetching data: {response.status_code}")
        return []

# Similar logging can be added to get_trending_cryptos and get_trending_4chan if needed.

def get_trending_cryptos(filter='all-crypto', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def get_trending_4chan(filter='4chan', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        print(f"Error fetching data: {response.status_code}")
        return []
