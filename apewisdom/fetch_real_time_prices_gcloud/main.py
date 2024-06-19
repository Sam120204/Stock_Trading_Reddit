import real_time_stock
import functions_framework
import logging


@functions_framework.http
def fetch_real_time_prices(request):
    try:
        real_time_prices = real_time_stock.update_real_time_prices()
        real_time_stock.save_real_time_prices_to_mongo(real_time_prices)
        return "Real time prices fetched and stored successfully."
    except Exception as e:
        logging.error("Error when fetching and storing real-time prices.")
        logging.error(e)
        return "Error fetching and storing data", 500

