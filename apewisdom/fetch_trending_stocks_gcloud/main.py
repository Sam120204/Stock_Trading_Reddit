from database import MongoDBClient
import functions_framework
from apewisdom_client import get_trending_stocks
from datetime import datetime, timedelta
import logging
import traceback
import pytz


def round_to_nearest_half_hour(dt):
    minutes = dt.minute
    if minutes < 15:
        delta = timedelta(minutes=-minutes)
    elif minutes < 45:
        delta = timedelta(minutes=30 - minutes)
    else:
        delta = timedelta(minutes=60 - minutes)
    return (dt + delta).replace(second=0, microsecond=0)


def convert_to_edt(dt):
    utc_zone = pytz.utc
    edt_zone = pytz.timezone('US/Eastern')

    dt_utc = utc_zone.localize(dt)

    dt_edt = dt_utc.astimezone(edt_zone)

    return dt_edt


def fetch_and_store_trending_stocks(request):
    try:
        db_client = MongoDBClient(db_name="stock_trends", collection_name="trending_stocks")

        trending_stocks = get_trending_stocks(filter='all-stocks')

        for stock in trending_stocks:
            stock["fetch_date"] = convert_to_edt(round_to_nearest_half_hour(datetime.utcnow()))

        db_client.insert_data(trending_stocks)
        logging.info("Data inserted into the database successfully.")
        return "Data inserted into the database successfully."
    except Exception as e:
        logging.error("Error in gather_data function")
        logging.error(e)
        logging.error(traceback.format_exc())
        return "Error in gather_data function, trending data not inserted into the database.", 500


def main():
    fetch_and_store_trending_stocks("")


if __name__ == "__main__":
    main()
