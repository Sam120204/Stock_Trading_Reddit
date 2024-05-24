import praw
from datetime import datetime, timedelta
import pandas as pd
from config import reddit_client_id, reddit_client_secret, reddit_user_agent

def get_reddit_instance():
    reddit = praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent
    )
    return reddit

def fetch_posts_comments(tickers, buy_sell_keywords, days=30, limit=100):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    posts = []
    for ticker in tickers:
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=limit):
            submission_date = datetime.utcfromtimestamp(submission.created_utc)
            if submission_date >= cutoff_date:
                posts.append({
                    'title': submission.title,
                    'selftext': submission.selftext,
                    'created_utc': submission.created_utc,
                    'url': submission.url
                })
    
    # Ensure unique posts
    posts_df = pd.DataFrame(posts).drop_duplicates(subset='url')
    
    return posts_df
