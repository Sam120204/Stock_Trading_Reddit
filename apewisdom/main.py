import logging
import traceback
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import praw
from apewisdom_client import get_trending_stocks
from real_time_stock import update_real_time_prices, save_real_time_prices_to_mongo
from gpt_sentiment import analyze_correlation
from chatbot import handle_chat

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)

@st.cache_resource
def init_mongo_connection():
    return MongoClient(
        st.secrets["mongo"]["uri"],
        tls=True,
        tlsAllowInvalidCertificates=True
    )

client = init_mongo_connection()
db = client[st.secrets["mongo"]["db_name"]]

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

        # Fetch real-time stock prices
        real_time_prices = update_real_time_prices()
        save_real_time_prices_to_mongo(real_time_prices)

        # Combine trending stocks with real-time prices
        combined_data = pd.merge(pd.DataFrame(trending_stocks), real_time_prices, on='ticker', suffixes=('_trending', '_real_time'))

        data = {
            "trending_stocks": trending_stocks,
            "real_time_prices": real_time_prices,
            "combined_data": combined_data
        }

        logging.info("Data gathering completed successfully.")
        return data
    except Exception as e:
        logging.error("Error in gather_data function")
        logging.error(e)
        logging.error(traceback.format_exc())
        return None

def display_chatbot():
    st.title("Trending Stocks on Reddit")
    st.write("Displaying the trending stocks data fetched from Reddit in the past 24 hours.")

    if "data" not in st.session_state:
        st.session_state.data = gather_data()

    data = st.session_state.data

    if data:
        combined_data = data["combined_data"]
        columns = ["rank", "ticker", "name", "mentions", "rank_24h_ago", "mentions_24h_ago", "price", "volume"]
        df = pd.DataFrame(combined_data, columns=columns)

        df.set_index('rank', inplace=True)
        st.table(df)

        fig_mentions = px.bar(df, x='ticker', y='mentions', title='Mentions')
        fig_changes = px.bar(df, x='ticker', y='mentions_24h_ago', title='24h Change (%)')
        st.plotly_chart(fig_mentions)
        st.plotly_chart(fig_changes)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        with st.container():
            user_input = st.text_input("Ask a question about the data:")

            if user_input:
                response = handle_chat(user_input, combined_data.to_dict())
                st.session_state.chat_history.append(("user", user_input))
                st.session_state.chat_history.append(("bot", response))

        for i, (sender, message) in enumerate(st.session_state.chat_history):
            if sender == "user":
                st.markdown(f"**You:** {message}")
            else:
                st.markdown(f"**Chatbot:** {message}")

if __name__ == "__main__":
    display_chatbot()


# def fetch_posts_comments(tickers, buy_sell_keywords):
#     reddit = get_reddit_instance()
#     subreddit = reddit.subreddit('investing')
#     cutoff_date = datetime.utcnow() - timedelta(days=1)
#     seen_urls = set()

#     def fetch_posts(ticker):
#         results = []
#         query = f"{ticker} ({' OR '.join(buy_sell_keywords)})"
#         for submission in subreddit.search(query, limit=50):
#             submission_date = datetime.utcfromtimestamp(submission.created_utc)
#             if submission_date >= cutoff_date and submission.url not in seen_urls:
#                 if any(keyword in submission.title.lower() for keyword in buy_sell_keywords):
#                     results.append((submission.title, submission.url, submission_date))
#                     seen_urls.add(submission.url)
#         return results

#     def fetch_comments():
#         results = []
#         for comment in subreddit.comments(limit=1000):
#             comment_date = datetime.utcfromtimestamp(comment.created_utc)
#             comment_url = f"https://www.reddit.com{comment.permalink}"
#             if comment_date >= cutoff_date and comment_url not in seen_urls:
#                 if any(ticker in comment.body for ticker in tickers):
#                     if any(keyword in comment.body.lower() for keyword in buy_sell_keywords):
#                         results.append((comment.body, comment_url, comment_date))
#                         seen_urls.add(comment_url)
#         return results

#     with ThreadPoolExecutor(max_workers=10) as executor:
#         futures = [executor.submit(fetch_posts, ticker) for ticker in tickers]
#         for future in as_completed(futures):
#             for title, url, date in future.result():
#                 logging.info(f"Title: {title}\nURL: {url}\nDate: {date}\n")

#     for body, url, date in fetch_comments():
#         logging.info(f"Comment: {body}\nURL: {url}\nDate: {date}\n")