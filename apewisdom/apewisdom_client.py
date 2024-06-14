import logging
import requests  # Import the requests module

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
    
    """def get_trending_stocks(filter='all-stocks', pages=6):
    trending_stocks = []
    for page in range(1, pages + 1):
        url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logging.info(f"Fetched data from page {page}: {data['results']}")
            trending_stocks.extend(data['results'])
        else:
            logging.error(f"Error fetching data: {response.status_code}")
            break
    return trending_stocks
    """

def get_trending_cryptos(filter='all-crypto', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        logging.error(f"Error fetching data: {response.status_code}")
        return []

def get_trending_4chan(filter='4chan', page=1):
    url = f'https://apewisdom.io/api/v1.0/filter/{filter}/page/{page}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['results']
    else:
        logging.error(f"Error fetching data: {response.status_code}")
        return []
