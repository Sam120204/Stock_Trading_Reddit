import os
import praw
import time
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import psycopg2

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

# PostgreSQL's connection details
# conn = psycopg2.connect(
#     dbname=os.getenv("DBNAME"),
#     user=os.getenv("USER"),
#     password=os.getenv("PASSWORD"),
#     host=os.getenv("HOST"),
#     port=os.getenv("DBPORT")
# )
# cur = conn.cursor()


def load_status():
    with open('fetch_status.json', 'r') as file:
        return json.load(file)


def update_status(status):
    with open('fetch_status.json', 'w') as file:
        json.dump(status, file, indent=4)


def fetch_and_store_posts(subreddit, start_epoch, end_epoch, ticker):
    status = load_status()
    search_terms = status[ticker]['search_terms']
    for term in search_terms:
        print(f"Fetching posts for {term} in r/{subreddit} from {datetime.fromtimestamp(start_epoch)} to {datetime.fromtimestamp(end_epoch)}")
        after = start_epoch
        while True:
            params = {
                "q": term,
                "subreddit": subreddit,
                "after": int(after),
                "before": int(end_epoch),
                "size": 100
            }
            response = requests.get(PULLPUSH_URL, params=params)
            posts = response.json().get('data', [])
            if not posts:
                print("end of posts")
                break

            for post in posts:
                print(post)
                break
                print(post['id'], subreddit, 'NVDA', post['title'], f"https://www.reddit.com{post['permalink']}",
                post['author'], datetime.fromtimestamp(post['created_utc']), post['score'], post['num_comments'])

                # # Check if post already exists in the database
                # cur.execute("SELECT EXISTS(SELECT 1 FROM reddit_posts WHERE post_id = %s)", (post['id'],))
                # exists = cur.fetchone()[0]
                #
                # if not exists:
                #     # Insert post into database if it does not exist
                #     cur.execute("""
                #         INSERT INTO reddit_posts (post_id, subreddit, ticker, title, url, author, post_time, score, num_comments)
                #         VALUES (%s, %s, %s, %s, %s, %s, to_timestamp(%s), %s, %s)
                #         """, (
                #             post['id'], subreddit, 'NVDA', post['title'], post['url'],
                #             post['author'], post['created_utc'], post['score'], post['num_comments']
                #         ))
                #     conn.commit()

            after = posts[0]['created_utc']

    # Update status after fetching all posts for each term
    current_day = datetime.fromtimestamp(start_epoch)
    while current_day < datetime.fromtimestamp(end_epoch):
        day_key = current_day.strftime('%Y-%m-%d')
        status[ticker][day_key] = 'fetch completed'
        current_day += timedelta(days=1)
    update_status(status)


# Specify the subreddit and time period
subreddit = 'wallstreetbets'
start_time = datetime(2024, 7, 2)  # Start time is inclusive
end_time = datetime(2024, 7, 3)  # End time is exclusive
start_epoch = int(start_time.timestamp())
end_epoch = int(end_time.timestamp())

# Start timing
start_timer = time.time()

all_posts = []

# while True:
#     data = fetch_pullpush_data(subreddit, start_epoch, end_epoch, size=100, after=after)
#     posts = data['data']
#     print(data)
#     if not posts:
#         break
#     all_posts.extend(posts)
#     after = posts[0]['created_utc']  # Use the last post's creation time as the 'after' parameter
#     print(f"Fetched {len(posts)} posts, total so far: {len(all_posts)}")  # Debug print
#
#     # Print URLs immediately after fetching
#     for post in posts:
#         print(datetime.fromtimestamp(post['created_utc']))
#         post_url = f"https://www.reddit.com{post['permalink']}"
#         print(f"URL: {post_url}")

fetch_and_store_posts(subreddit, start_epoch, end_epoch, "NVDA")

# print(f"Fetched {len(all_posts)} posts from r/{subreddit} in April first 2024.")

# End timing
end_timer = time.time()
elapsed_time = end_timer - start_timer
print(f"Total elapsed time: {elapsed_time:.2f} seconds")
