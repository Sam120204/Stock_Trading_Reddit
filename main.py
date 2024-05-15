from reddit_client import get_reddit_instance
from apewisdom_client import get_trending_stocks

def fetch_posts_comments(trending_stocks, tickers, buy_sell_keywords):
    # Fetch posts and comments related to trending stocks
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')

    # Fetch and print posts
    for ticker in tickers:
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=50):
            if any(keyword in submission.title.lower() for keyword in buy_sell_keywords):
                print(f"Title: {submission.title}\nURL: {submission.url}\n")

    # Fetch and print comments
    for comment in subreddit.comments(limit=1000):
        if any(ticker in comment.body for ticker in tickers):
            if any(keyword in comment.body.lower() for keyword in buy_sell_keywords):
                print(f"Comment: {comment.body}\nURL: https://www.reddit.com{comment.permalink}\n")

def display_trending_stocks(stocks):
    print(f"{'Rank':<5}{'Ticker':<10}{'Name':<30}{'Mentions':<10}{'24h Change (%)':<15}")
    print("="*70)
    for i, stock in enumerate(stocks, start=1):
        mentions = stock['mentions']
        mentions_24h_ago = stock.get('mentions_24h_ago', 0)
        change_24h = (mentions - mentions_24h_ago) / mentions_24h_ago * 100 if mentions_24h_ago else 0
        print(f"{i:<5}{stock['ticker']:<10}{stock['name']:<30}{mentions:<10}{change_24h:<15.2f}")

def main():
    # Fetch trending stocks from Apewisdom
    trending_stocks = get_trending_stocks(filter='all-stocks')
    tickers = [stock['ticker'] for stock in trending_stocks]
    buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']
    display_trending_stocks(trending_stocks)

if __name__ == "__main__":
    main()
