import os
import praw
import time
import pytz
import requests
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# PRAW setup for Reddit API
reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'),
                     username=os.getenv('REDDIT_USERNAME'),
                     password=os.getenv('REDDIT_PASSWORD'))

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

