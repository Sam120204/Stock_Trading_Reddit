import os
import praw
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
# Load environment variables from .env file
load_dotenv()

# PRAW setup for Reddit API
reddit = praw.Reddit(client_id=os.getenv('REDDIT_CLIENT_ID'),
                     client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                     user_agent=os.getenv('REDDIT_USER_AGENT'),
                     username=os.getenv('REDDIT_USERNAME'),
                     password=os.getenv('REDDIT_PASSWORD'))

def fetch_and_store_posts(subreddit, start_epoch, end_epoch, ticker):
    search_terms = ["NVDA", "AAPL", "TSLA"]  # Example search terms
    
    with open('post_urls.txt', 'a') as url_file:
        for term in search_terms:
            print(f"Fetching posts for {term} in r/{subreddit} from {datetime.fromtimestamp(start_epoch)} to {datetime.fromtimestamp(end_epoch)}")
            posts = reddit.subreddit(subreddit).search(term, time_filter='all', sort='new', limit=100)
            for post in posts:
                post_time = datetime.utcfromtimestamp(post.created_utc)
                if start_epoch <= post.created_utc <= end_epoch:
                    post_url = post.url
                    comment_url = post_url + ".json"
                    print(post.id, subreddit, term, post.title, post.selftext, post_url, post_time)
                    url_file.write(f"{post_url}\n")
                    url_file.write(f"{comment_url}\n")  # Append the comment URL to the file

# Specify the subreddit and time period
subreddit = 'wallstreetbets'
end_time = datetime.now()  # End time is the current time
start_time = end_time - timedelta(days=7)  # Start time is 7 days before the end time
start_epoch = int(start_time.timestamp())
end_epoch = int(end_time.timestamp())

# Start timing
start_timer = time.time()

fetch_and_store_posts(subreddit, start_epoch, end_epoch, "NVDA")

# End timing
end_timer = time.time()
elapsed_time = end_timer - start_timer
print(f"Total elapsed time: {elapsed_time:.2f} seconds")
