import praw
import config
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

def get_reddit_instance():
    reddit = praw.Reddit(
        client_id=config.REDDIT_CLIENT_ID,
        client_secret=config.REDDIT_SECRET,
        user_agent=config.REDDIT_USER_AGENT,
        username=config.REDDIT_USERNAME,
        password=config.REDDIT_PASSWORD
    )
    return reddit

def fetch_posts_comments(tickers, buy_sell_keywords, days=15):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    seen_urls = set()
    posts = []

    def fetch_posts(ticker):
        results = []
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=50):
            submission_date = datetime.utcfromtimestamp(submission.created_utc)
            if submission_date >= cutoff_date and submission.url not in seen_urls:
                if any(keyword in submission.title.lower() for keyword in buy_sell_keywords):
                    results.append({
                        'ticker': ticker,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'created_utc': submission_date,
                        'url': submission.url
                    })
                    seen_urls.add(submission.url)
        return results

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_posts, ticker) for ticker in tickers]
        for future in as_completed(futures):
            posts.extend(future.result())

    return pd.DataFrame(posts)
