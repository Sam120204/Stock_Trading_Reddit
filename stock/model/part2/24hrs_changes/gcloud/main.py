from track_top_ticker_24hr import analyze_and_update_posts
import os
import time
from flask import jsonify

def fetch_store_stock_prices_postgres(request):
    # Set the timezone to Toronto
    os.environ['TZ'] = 'America/Toronto'
    time.tzset()

    try:
        # Run the function to analyze and update posts
        analyze_and_update_posts(request)

        # Return a success response
        return jsonify({"status": "success", "message": "Post analysis and update completed."}), 200

    except Exception as e:
        # Return an error response in case of failure
        return jsonify({"status": "error", "message": str(e)}), 500


def main():
    fetch_store_stock_prices_postgres("")


if __name__ == "__main__":
    main()
