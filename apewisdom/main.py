import logging
import traceback
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
from reddit_client import get_reddit_instance
from apewisdom_client import get_trending_stocks
from database import MongoDBClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
***REMOVED***
)

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
        mongo_uri = st.secrets["mongo"]["uri"]  # Ensure this is correctly set in your Streamlit secrets
        db_client = MongoDBClient(db_name="stock_trends", collection_name="trending_stocks", uri=mongo_uri)

        trending_stocks = get_trending_stocks(filter='all-stocks')
        logging.info(f"Trending stocks fetched: {trending_stocks}")
        tickers_stocks = [stock['ticker'] for stock in trending_stocks]

        for stock in trending_stocks:
            stock["fetch_date"] = datetime.utcnow()

        db_client.insert_data(trending_stocks)
        logging.info("Data inserted into the database successfully.")

        data = display_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
        fig_mentions, fig_changes = visualize_trending_items(trending_stocks, "Trending Stocks on Reddit in the past 24 hours")
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
