import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from reddit_client import get_reddit_instance
from apewisdom_client import get_trending_stocks, get_trending_cryptos, get_trending_4chan

def fetch_posts_comments(tickers, buy_sell_keywords):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')
    cutoff_date = datetime.utcnow() - timedelta(days=15)

    # Fetch and print posts within the last 15 days
    for ticker in tickers:
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=50):
            submission_date = datetime.utcfromtimestamp(submission.created_utc)
            if submission_date >= cutoff_date:
                if any(keyword in submission.title.lower() for keyword in buy_sell_keywords):
                    print(f"Title: {submission.title}\nURL: {submission.url}\nDate: {submission_date}\n")

    # Fetch and print comments within the last 15 days
    for comment in subreddit.comments(limit=1000):
        comment_date = datetime.utcfromtimestamp(comment.created_utc)
        if comment_date >= cutoff_date:
            if any(ticker in comment.body for ticker in tickers):
                if any(keyword in comment.body.lower() for keyword in buy_sell_keywords):
                    print(f"Comment: {comment.body}\nURL: https://www.reddit.com{comment.permalink}\nDate: {comment_date}\n")

def display_trending_items(items, title):
    print(f"\n{title}")
    print(f"{'Rank':<5}{'Ticker':<10}{'Name':<30}{'Mentions':<10}{'24h Change (%)':<15}")
    print("="*70)
    for i, item in enumerate(items, start=1):
        mentions = item['mentions']
        mentions_24h_ago = item.get('mentions_24h_ago', 0)
        change_24h = (mentions - mentions_24h_ago) / mentions_24h_ago * 100 if mentions_24h_ago else 0
        print(f"{i:<5}{item['ticker']:<10}{item['name']:<30}{mentions:<10}{change_24h:<15.2f}")

def visualize_trending_items(items, title):
    tickers = [item['ticker'] for item in items]
    mentions = [item['mentions'] for item in items]
    changes = [(item['mentions'] - item.get('mentions_24h_ago', 0)) / item.get('mentions_24h_ago', 0) * 100 if item.get('mentions_24h_ago', 0) else 0 for item in items]

    # Bar chart for mentions
    plt.figure(figsize=(10, 5))
    sns.barplot(x=tickers, y=mentions)
    plt.title(f'{title} - Mentions')
    plt.xlabel('Ticker')
    plt.ylabel('Mentions')
    plt.xticks(rotation=90)
    plt.show()

    # Bar chart for 24h change
    plt.figure(figsize=(10, 5))
    sns.barplot(x=tickers, y=changes)
    plt.title(f'{title} - 24h Change (%)')
    plt.xlabel('Ticker')
    plt.ylabel('24h Change (%)')
    plt.xticks(rotation=90)
    plt.show()

def main():
    buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']

    # Fetch and display trending stocks from Apewisdom
    trending_stocks = get_trending_stocks(filter='all-stocks')
    tickers_stocks = [stock['ticker'] for stock in trending_stocks]
    display_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
    visualize_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
    fetch_posts_comments(tickers_stocks, buy_sell_keywords)

    # Fetch and display trending cryptocurrencies from Apewisdom
    trending_cryptos = get_trending_cryptos(filter='all-crypto')
    tickers_cryptos = [crypto['ticker'] for crypto in trending_cryptos]
    display_trending_items(trending_cryptos, "Trending Cryptocurrencies on Reddit in the past 24 hours")
    visualize_trending_items(trending_cryptos, "Trending Cryptocurrencies on Reddit in the past 24 hours")
    fetch_posts_comments(tickers_cryptos, buy_sell_keywords)

    # Fetch and display trending items on 4Chan /biz from Apewisdom
    trending_4chan = get_trending_4chan(filter='4chan')
    tickers_4chan = [item['ticker'] for item in trending_4chan]
    display_trending_items(trending_4chan, "Most mentioned Stocks & Cryptos on 4Chan /biz in the last 24h (BETA)")
    visualize_trending_items(trending_4chan, "Most mentioned Stocks & Cryptos on 4Chan /biz in the last 24h (BETA)")
    fetch_posts_comments(tickers_4chan, buy_sell_keywords)

if __name__ == "__main__":
    main()
