import logging
import traceback
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import praw
from apewisdom_client import get_trending_stocks
from real_time_stock import update_real_time_prices, save_real_time_prices_to_mongo
from chatbot import StockChatBot

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("streamlit_app.log"),
        logging.StreamHandler()
    ]
)

st.set_page_config(page_title="TrendSage", layout="wide")

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

@st.cache_data(ttl=3600)
def fetch_historical_mentions(tickers, days=30):
    historical_mentions = {}
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    for ticker in tickers:
        mentions = list(db['trending_stocks'].find(
            {"ticker": ticker, "fetch_date": {"$gte": start_date, "$lte": end_date}},
            {"mentions": 1, "fetch_date": 1}
        ))
        if mentions:
            historical_mentions[ticker] = sorted(mentions, key=lambda x: x['fetch_date'])
    return historical_mentions

def compute_trend(mentions):
    return [mention['mentions'] for mention in mentions]

@st.cache_data(ttl=3600)
def gather_data():
    try:
        trending_stocks = []
        for page in range(1, 2):  # Fetch 6 pages of trending stocks
            trending_stocks.extend(get_trending_stocks(filter='all-stocks', page=page))
        
        logging.info(f"Trending stocks fetched: {len(trending_stocks)}")
        tickers_stocks = [stock['ticker'] for stock in trending_stocks]

        for stock in trending_stocks:
            stock["fetch_date"] = datetime.utcnow()

        db[st.secrets["mongo"]["collection_name"]].insert_many(trending_stocks)
        logging.info("Data inserted into the database successfully.")

        real_time_prices = update_real_time_prices()
        save_real_time_prices_to_mongo(real_time_prices)

        combined_data = pd.merge(pd.DataFrame(trending_stocks), real_time_prices, on='ticker', suffixes=('_trending', '_real_time'))

        historical_mentions = fetch_historical_mentions(tickers_stocks)
        combined_data['trend'] = combined_data['ticker'].apply(lambda x: compute_trend(historical_mentions.get(x, [])))

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
    st.title("TrendSage")

    if "data" not in st.session_state:
        st.session_state.data = gather_data()

    data = st.session_state.data

    if data:
        combined_data = data["combined_data"]
        columns = ["rank", "ticker", "name", "mentions", "rank_24h_ago", "mentions_24h_ago", "price", "volume", "trend"]
        df = pd.DataFrame(combined_data, columns=columns)

        df.set_index('rank', inplace=True)

        st.dataframe(
            df,
            column_config={
                "trend": st.column_config.AreaChartColumn(
                    label="Trend (30 days)",
                    width="medium",
                    help="The trend of mentions in the last 30 days",
                    y_min=0,
                    y_max=max(df["mentions"])
                )
            },
            hide_index=True
        )

        top_20_df = df.head(20)
        top_30_df = df.nlargest(30, 'mentions_24h_ago')

        fig_mentions = px.bar(top_20_df, x='ticker', y='mentions', title='Top 20 Mentions')
        fig_mentions.update_layout(
            autosize=False,
            width=800,  # Adjust the width as needed
            height=400,  # Adjust the height as needed
        )
        fig_changes = px.bar(top_30_df, x='ticker', y='mentions_24h_ago', title='Top 30 24h Change (%)')
        fig_changes.update_layout(
            autosize=False,
            width=800,  # Adjust the width as needed
            height=400,  # Adjust the height as needed
        )
        st.plotly_chart(fig_mentions)
        st.plotly_chart(fig_changes)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "stock_bot" not in st.session_state:
            st.session_state.stock_bot = StockChatBot(combined_data)

        st.subheader("Stock Data Analysis Chatbot")
        message_placeholder = st.empty()

        with st.container():
            st.write('<div class="centered-content">', unsafe_allow_html=True)
            user_input = st.chat_input("Ask a question about the data:", key="user_input")
            st.write('</div>', unsafe_allow_html=True)

            if user_input:
                response = st.session_state.stock_bot.query(user_input, st.session_state.chat_history)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response})

        for chat in st.session_state.chat_history:
            with st.chat_message(chat["role"]):
                st.markdown(chat["content"])

if __name__ == "__main__":
    display_chatbot()
