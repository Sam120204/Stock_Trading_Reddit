import os
import praw
import time
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PRAW setup for Reddit API
reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'),
                     username=os.getenv('REDDIT_USERNAME'),
                     password=os.getenv('REDDIT_PASSWORD'))

# PullPush setup
PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/"

def fetch_pullpush_data(subreddit, start_epoch, end_epoch, size=100, after=None):
    params = {
        "q": "NVDA",
        "subreddit": subreddit,
        "after": int(start_epoch) if not after else int(after),
        "before": int(end_epoch),
        "size": size
    }
    response = requests.get(PULLPUSH_URL, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

# Specify the subreddit and time period
subreddit = 'wallstreetbets'
start_time = datetime(2024, 7, 1)
end_time = datetime(2024, 7, 3)
start_epoch = int(start_time.timestamp())
end_epoch = int(end_time.timestamp())

# Start timing
start_timer = time.time()

all_posts = []
after = None

while True:
    data = fetch_pullpush_data(subreddit, start_epoch, end_epoch, size=10, after=after)
    posts = data['data']
    if not posts:
        break
    all_posts.extend(posts)
    after = posts[0]['created_utc']  # Use the last post's creation time as the 'after' parameter
    print(f"Fetched {len(posts)} posts, total so far: {len(all_posts)}")  # Debug print
    
    # Print URLs immediately after fetching
    for post in posts:
        print(post['created_utc'])
        post_url = f"https://www.reddit.com{post['permalink']}"
        print(f"URL: {post_url}")

print(f"Fetched {len(all_posts)} posts from r/{subreddit} in April first 2024.")

# End timing
end_timer = time.time()
elapsed_time = end_timer - start_timer
print(f"Total elapsed time: {elapsed_time:.2f} seconds")
