import os
import praw
import time
import pytz
import requests
import json
import requests
from datetime import datetime, timedelta
from parse_post_url import fetch_reddit_post, parse_post
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PRAW setup for Reddit API
reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'),
                     username=os.getenv('REDDIT_USERNAME'),
                     password=os.getenv('REDDIT_PASSWORD'))

# # PullPush setup
# PULLPUSH_URL = "https://api.pullpush.io/reddit/search/submission/"

def load_status():
    try:
        with open('fetch_status.json', 'r') as file:
            data = file.read().strip()
            if not data:
                return {}
            return json.loads(data)
    except FileNotFoundError:
        return {}

def update_status(status):
    with open('fetch_status.json', 'w') as file:
        json.dump(status, file, indent=4)

# def fetch_and_store_posts(subreddit, start_epoch, end_epoch, tickers, use_status=True):
#     all_posts = []
#     fetched_urls = set()  # To track fetched URLs and avoid duplicates
#
#     status = load_status()
#
#     for ticker in tickers:
#         if ticker not in status:
#             status[ticker] = {'search_terms': [ticker]}  # Use ticker as the default search term if not found
#             update_status(status)  # Save the updated status immediately
#
#         search_terms = status[ticker]['search_terms']
#
#         for term in search_terms:
#             print(f"Fetching posts for {term} in r/{subreddit} from {datetime.fromtimestamp(start_epoch)} to {datetime.fromtimestamp(end_epoch)}")
#             after = start_epoch
#             while True:
#                 params = {
#                     "q": term,
#                     "subreddit": subreddit,
#                     "after": int(after),
#                     "before": int(end_epoch),
#                     "size": 500
#                 }
#                 response = requests.get(PULLPUSH_URL, params=params)
#                 posts = response.json().get('data', [])
#                 if not posts:
#                     print("end of posts")
#                     break
#
#                 for post in posts:
#                     url = f"https://www.reddit.com{post['permalink']}"
#                     if url in fetched_urls:
#                         continue
#                     fetched_urls.add(url)
#                     html = fetch_reddit_post(url)
#                     post_details = parse_post(html) if html else {'score': 'N/A', 'comments': 'N/A'}
#
#                     post_data = {
#                         'id': post['id'],
#                         'title': post['title'],
#                         'url': url,
#                         'score': post_details['score'],
#                         'num_comments': post_details['comments']
#                     }
#                     all_posts.append(post_data)
#
#                 with open('post_urls.txt', 'a') as url_file:  # Open the file in append mode
#                     for post in posts:
#                         print(post['id'], subreddit, ticker, post['title'], f"https://www.reddit.com{post['permalink']}", datetime.fromtimestamp(post['created_utc']))
#                         url_file.write(f"https://www.reddit.com{post['permalink']}\n")
#                 after = posts[0]['created_utc']
#
#         # Update status after fetching all posts for each term
#         if use_status:
#             current_day = datetime.fromtimestamp(start_epoch)
#             while current_day < datetime.fromtimestamp(end_epoch):
#                 day_key = current_day.strftime('%Y-%m-%d')
#                 status[ticker][day_key] = 'fetch completed'
#                 current_day += timedelta(days=1)
#             update_status(status)
#
#     return all_posts

# def fetch_and_store_all_posts(subreddit, start_epoch, end_epoch, use_status=True):
#     all_posts = []
#     fetched_urls = set()  # To track fetched URLs and avoid duplicates
#
#     # status = load_status() if use_status else {}
#
#     current_start = start_epoch
#     day_seconds = 86400*2  # Number of seconds in a day
#
#     while current_start < end_epoch:
#         count = 0
#         daily_end = min(current_start + day_seconds, end_epoch)  # End at either the next day or the end_epoch
#
#         print(f"Fetching posts for r/{subreddit} from {datetime.fromtimestamp(current_start)} to {datetime.fromtimestamp(daily_end)}")
#         params = {
#             "subreddit": subreddit,
#             "after": int(current_start),
#             "before": int(daily_end),
#             "size": 1000
#         }
#         response = requests.get(PULLPUSH_URL, params=params)
#         posts = response.json().get('data', [])
#         if not posts:
#             print("No more posts")
#         else:
#             for post in posts:
#                 url = f"https://www.reddit.com{post['permalink']}"
#                 count += 1
#                 if url not in fetched_urls:
#                     fetched_urls.add(url)
#                     html = fetch_reddit_post(url)
#                     post_details = parse_post(html) if html else {'score': 'N/A', 'comments': 'N/A'}
#
#                     post_data = {
#                         'id': post['id'],
#                         'title': post['title'],
#                         'url': url,
#                         'score': post_details['score'],
#                         'num_comments': post_details['comments']
#                     }
#                     all_posts.append(post_data)
#
#             # Move the start to the next day
#             print(f"Fetched {count} posts")
#             current_start += day_seconds
#
#     # if use_status:
#     #     current_day = datetime.fromtimestamp(start_epoch)
#     #     while current_day < datetime.fromtimestamp(end_epoch):
#     #         day_key = current_day.strftime('%Y-%m-%d')
#     #         status[day_key] = 'fetch completed'
#     #         current_day += timedelta(days=1)
#     #     update_status(status)
#
#     return all_posts

def fetch_prev_day_posts(subreddit_name, start_epoch, end_epoch):
    subreddit = reddit.subreddit(subreddit_name)
    fetched_urls = set()

    print(f"Fetching posts for r/{subreddit_name} from {datetime.fromtimestamp(start_epoch)} to {datetime.fromtimestamp(end_epoch)}")

    all_posts = []
    # Fetch posts
    for submission in subreddit.new(limit=None):
        if start_epoch <= submission.created_utc < end_epoch:
            url = f"https://www.reddit.com{submission.permalink}"
            if url in fetched_urls:
                continue
            fetched_urls.add(url)
            html = fetch_reddit_post(url)
            post_details = parse_post(html) if html else {'score': 'N/A', 'comments': 'N/A'}

            post_data = {
                'id': submission.id,
                'title': submission.title,
                'url': f"https://www.reddit.com{submission.permalink}",
                'score': submission.score,
                'num_comments': submission.num_comments,
            }

            all_posts.append(post_data)

    print(len(all_posts))
    return all_posts

def fetch_all_comments_from_url(urls, post_upvote):
    all_comments_by_post = []

    for url in urls:
        # Extract the submission ID from the URL
        parts = url.split('/')
        submission_id = parts[6] if 'comments' in parts else None

        if not submission_id:
            print("Invalid URL or Submission ID not found:", url)
            continue  # Skip to the next URL

        submission = reddit.submission(id=submission_id)

        # Fetch only the top-level comments; do not expand "MoreComments"
        for comment in submission.comments:
            if isinstance(comment, praw.models.MoreComments):
                continue  # Skip "MoreComments" objects
            if abs(comment.score) >= 10 and abs(comment.score) >= abs(post_upvote/10):
                comment_data = {
                    'post_url': url,
                    'id': comment.id,
                    'comment_url': f"https://www.reddit.com{comment.permalink}",
                    'comment_scores': comment.score
                }
                all_comments_by_post.append(comment_data)

    return all_comments_by_post

if __name__ == "__main__":
    with open('post_urls.txt', 'r') as f:
        urls = [url.strip() for url in f.readlines()]

    # Set the timezone for Waterloo, Canada
    local_tz = pytz.timezone('America/Toronto')
    # Specify the subreddit and time period
    subreddit = 'wallstreetbets'

    end_time = datetime.now(local_tz)  # End time is exclusive
    start_time = end_time - timedelta(days=1)  # Start time is inclusive
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())

    # List of tickers
    tickers = ["NVIDIA", "nvida", "meta", "SPY", "ASTS", "AMD", "Tesla"]  # Add more tickers as needed

    # Fetch and store posts
    # all_posts = fetch_and_store_posts(subreddit, start_epoch, end_epoch, tickers, use_status=True)
    # print(fetch_prev_day_posts(subreddit, "2024-07-29"))
    # print(fetch_all_comments_from_url(urls[:50]))
