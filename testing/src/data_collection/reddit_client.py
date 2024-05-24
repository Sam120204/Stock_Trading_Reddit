# reddit_client.py

import praw
import pandas as pd
from datetime import datetime, timedelta
from config import reddit_client_id, reddit_client_secret, reddit_user_agent

def get_reddit_instance():
    return praw.Reddit(
        client_id=reddit_client_id,
        client_secret=reddit_client_secret,
        user_agent=reddit_user_agent
    )

def fetch_posts_comments(tickers, buy_sell_keywords, days=15):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    data = []
    seen_urls = set()

    # Fetch posts within the last `days` days
    for ticker in tickers:
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=50):
            submission_date = datetime.utcfromtimestamp(submission.created_utc)
            if submission_date >= cutoff_date and submission.url not in seen_urls:
                seen_urls.add(submission.url)
                data.append({
                    'ticker': ticker,
                    'title': submission.title,
                    'url': submission.url,
                    'created_utc': submission_date,
                    'selftext': submission.selftext,
                    'mentions': sum(keyword in submission.title.lower() for keyword in buy_sell_keywords)
                })
                
    # Fetch comments within the last `days` days
    for comment in subreddit.comments(limit=1000):
        comment_date = datetime.utcfromtimestamp(comment.created_utc)
        if comment_date >= cutoff_date:
            body = comment.body.lower()
            for ticker in tickers:
                if ticker in body:
                    mentions = sum(keyword in body for keyword in buy_sell_keywords)
                    if mentions > 0:
                        data.append({
                            'ticker': ticker,
                            'title': '',
                            'url': f"https://www.reddit.com{comment.permalink}",
                            'created_utc': comment_date,
                            'selftext': '',
                            'mentions': mentions
                        })

    return pd.DataFrame(data)
