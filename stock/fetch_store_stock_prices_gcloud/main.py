from fetch_store_stock_prices import fetch_store_stock_prices
import os
import time


def fetch_store_stock_prices_postgres(request):
    os.environ['TZ'] = 'America/Toronto'
    time.tzset()
    return fetch_store_stock_prices(request)


def main():
    fetch_store_stock_prices_postgres("")


if __name__ == "__main__":
    main()
