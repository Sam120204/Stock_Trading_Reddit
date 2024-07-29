import os
import praw
import time
import pytz
import requests
import json
from datetime import datetime, timedelta
from parse_post_url import fetch_reddit_post, parse_post
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

def load_status():
    with open('fetch_status.json', 'r') as file:
        return json.load(file)


def update_status(status):
    with open('fetch_status.json', 'w') as file:
        json.dump(status, file, indent=4)


def fetch_and_store_posts(subreddit, start_epoch, end_epoch, ticker, use_status=True):
    if use_status:
        status = load_status()
        search_terms = status[ticker]['search_terms']
    else:
        search_terms = ["NVIDIA", "nvida"]  # Default search terms for testing

    all_posts = []
    fetched_urls = set() 
    for term in search_terms:
        print(f"Fetching posts for {term} in r/{subreddit} from {datetime.fromtimestamp(start_epoch)} to {datetime.fromtimestamp(end_epoch)}")
        after = start_epoch
        while True:
            params = {
                "q": term,
                "subreddit": subreddit,
                "after": int(after),
                "before": int(end_epoch),
                "size": 500
            }
            response = requests.get(PULLPUSH_URL, params=params)
            posts = response.json().get('data', [])
            if not posts:
                print("end of posts")
                break
            
            for post in posts:
                url = f"https://www.reddit.com{post['permalink']}"
                if url in fetched_urls:
                    continue
                fetched_urls.add(url)
                html = fetch_reddit_post(url)
                post_details = parse_post(html) if html else {'score': 'N/A', 'comments': 'N/A'}
                
                post_data = {
                    'id': post['id'],
                    'title': post['title'],
                    'url': url,
                    'score': post_details['score'],
                    'num_comments': post_details['comments']
                }
                all_posts.append(post_data)
            
            with open('post_urls.txt', 'a') as url_file:  # Open the file in append mode
                for post in posts:
                    print(post['id'], subreddit, 'NVDA', post['title'], f"https://www.reddit.com{post['permalink']}", datetime.fromtimestamp(post['created_utc']))
                    url_file.write(f"https://www.reddit.com{post['permalink']}\n")
            after = posts[0]['created_utc']

    # Update status after fetching all posts for each term
    if use_status:
        current_day = datetime.fromtimestamp(start_epoch)
        while current_day < datetime.fromtimestamp(end_epoch):
            day_key = current_day.strftime('%Y-%m-%d')
            status[ticker][day_key] = 'fetch completed'
            current_day += timedelta(days=1)
        update_status(status)

    return all_posts

if __name__ == "__main__":
    # Set the timezone for Waterloo, Canada
    local_tz = pytz.timezone('America/Toronto')
    # Specify the subreddit and time period
    subreddit = 'wallstreetbets'

    end_time = datetime.now(local_tz)  # End time is exclusive
    start_time = end_time - timedelta(days=7)  # Start time is inclusive
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())

    # Fetch and store posts
    all_posts = fetch_and_store_posts(subreddit, start_epoch, end_epoch, "NVDA", use_status=False)
