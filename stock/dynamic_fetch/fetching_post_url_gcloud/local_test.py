from flask import Flask, request
from fetch_post_url_from_pullpush import fetch_and_store_posts
from datetime import datetime, timedelta
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    return "Please go to /test_fetch_reddit_posts to test the function."

@app.route('/test_fetch_reddit_posts', methods=['GET'])
def test_fetch_reddit_posts():
    # Set the timezone for Waterloo, Canada
    local_tz = pytz.timezone('America/Toronto')

    # Specify the subreddit and time period
    subreddit = 'wallstreetbets'

    end_time = datetime.now(local_tz)  # End time is exclusive
    start_time = end_time - timedelta(days=7)  # Start time is inclusive
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())

    all_posts = fetch_and_store_posts(subreddit, start_epoch, end_epoch, "NVDA")

    return f"Fetched and stored {len(all_posts)} posts."

if __name__ == "__main__":
    app.run(port=8080)
