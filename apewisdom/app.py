import logging
import traceback
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import praw
from apewisdom_client import get_trending_stocks  # Make sure this import is correct

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)

# Initialize MongoDB connection
@st.cache_resource
def init_mongo_connection():
    return MongoClient(st.secrets["mongo"]["uri"])

client = init_mongo_connection()
db = client[st.secrets["mongo"]["db_name"]]

# Initialize Reddit connection
@st.cache_resource
def get_reddit_instance():
    reddit = praw.Reddit(
        client_id=st.secrets["reddit"]["client_id"],
        client_secret=st.secrets["reddit"]["client_secret"],
        user_agent=st.secrets["reddit"]["user_agent"],
        username=st.secrets["reddit"]["username"],
        password=st.secrets["reddit"]["password"]
    )
    return reddit

def fetch_posts_comments(tickers, buy_sell_keywords):
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit('investing')
    cutoff_date = datetime.utcnow() - timedelta(days=1)
    seen_urls = set()

    def fetch_posts(ticker):
        results = []
        query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
        for submission in subreddit.search(query, limit=50):
            submission_date = datetime.utcfromtimestamp(submission.created_utc)
            if submission_date >= cutoff_date and submission.url not in seen_urls:
                if any(keyword in submission.title.lower() for keyword in buy_sell_keywords):
                    results.append((submission.title, submission.url, submission_date))
                    seen_urls.add(submission.url)
        return results

    def fetch_comments():
        results = []
        for comment in subreddit.comments(limit=1000):
            comment_date = datetime.utcfromtimestamp(comment.created_utc)
            comment_url = f"https://www.reddit.com{comment.permalink}"
            if comment_date >= cutoff_date and comment_url not in seen_urls:
                if any(ticker in comment.body for ticker in tickers):
                    if any(keyword in comment.body.lower() for keyword in buy_sell_keywords):
                        results.append((comment.body, comment_url, comment_date))
                        seen_urls.add(comment_url)
        return results

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_posts, ticker) for ticker in tickers]
        for future in as_completed(futures):
            for title, url, date in future.result():
                logging.info(f"Title: {title}\nURL: {url}\nDate: {date}\n")

    for body, url, date in fetch_comments():
        logging.info(f"Comment: {body}\nURL: {url}\nDate: {date}\n")

def display_trending_items(items, title):
    logging.info(f"\n{title}")
    logging.info(f"{'Rank':<5}{'Ticker':<10}{'Name':<30}{'Mentions':<10}{'24h Change (%)':<15}")
    logging.info("="*70)
    data = []
    for i, item in enumerate(items, start=1):
        mentions = item['mentions']
        mentions_24h_ago = item.get('mentions_24h_ago', 0)
        change_24h = (mentions - mentions_24h_ago) / mentions_24h_ago * 100 if mentions_24h_ago else 0
        data.append([i, item['ticker'], item['name'], mentions, change_24h])
        logging.info(f"{i:<5}{item['ticker']:<10}{item['name']:<30}{mentions:<10}{change_24h:<15.2f}")
    return data

def visualize_trending_items(items, title):
    tickers = [item['ticker'] for item in items]
    mentions = [item['mentions'] for item in items]
    changes = [(item['mentions'] - item.get('mentions_24h_ago', 0)) / item.get('mentions_24h_ago', 0) * 100 if item.get('mentions_24h_ago', 0) else 0 for item in items]

    fig_mentions = px.bar(x=tickers, y=mentions, labels={'x': 'Ticker', 'y': 'Mentions'}, title=f'{title} - Mentions')
    fig_changes = px.bar(x=tickers, y=changes, labels={'x': 'Ticker', 'y': '24h Change (%)'}, title=f'{title} - 24h Change (%)')

    return fig_mentions, fig_changes

def gather_data():
    try:
        buy_sell_keywords = ['buy', 'sell', 'purchase', 'short', 'long', 'hold', 'trade']
        trending_stocks = get_trending_stocks(filter='all-stocks')
        logging.info(f"Trending stocks fetched: {trending_stocks}")
        tickers_stocks = [stock['ticker'] for stock in trending_stocks]

        for stock in trending_stocks:
            stock["fetch_date"] = datetime.utcnow()

        # Insert data into MongoDB
        db[st.secrets["mongo"]["collection_name"]].insert_many(trending_stocks)
        logging.info("Data inserted into the database successfully.")

        data = display_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
        fig_mentions, fig_changes = visualize_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
        logging.info(f"Data for display: {data}")
        return data, fig_mentions, fig_changes
    except Exception as e:
        logging.error("Error in gather_data function")
        logging.error(e)
        logging.error(traceback.format_exc())
        return [], None, None

def main():
    st.title("Trending Stocks on Reddit")
    st.write("Displaying the trending stocks data fetched from Reddit in the past 24 hours.")

    # Fetch the data
    data, fig_mentions, fig_changes = gather_data()

    # Define column names
    columns = ["Rank", "Ticker", "Name", "Mentions", "24h Change (%)"]

    # Display data in a table
    if data:
        df = pd.DataFrame(data, columns=columns)
        df.set_index('Rank', inplace=True)
        st.table(df)
    else:
        st.write("No data available.")

    # Display the visualizations using Plotly
    if fig_mentions:
        st.plotly_chart(fig_mentions)

    if fig_changes:
        st.plotly_chart(fig_changes)

if __name__ == "__main__":
    main()
