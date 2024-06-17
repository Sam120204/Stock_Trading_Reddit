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
import plotly.graph_objects as stgo

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
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days-1)

    for ticker in tickers:
        daily_mentions = [None] * 30

        for i in range(30):
            day = start_date + timedelta(days=i)
            mentions = list(db['trending_stocks'].find(
                {"ticker": ticker, "fetch_date": {"$gte": day, "$lte": day + timedelta(days=1)}},
                {"mentions": 1, "fetch_date": 1}
            ).sort("fetch_date", 1).limit(1))

            if mentions:
                daily_mentions[i] = mentions[0]

        historical_mentions[ticker] = daily_mentions

    return historical_mentions


@st.cache_data(ttl=3600)
def fetch_historical_prices(tickers, days=30):
    historical_prices = {}
    end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=days-1)

    for ticker in tickers:
        daily_close_prices = [None] * 30

        for i in range(30):
            day = start_date + timedelta(days=i)

            # Use Friday's price for Saturday and Sunday
            if day.weekday() == 6:
                day = day - timedelta(days=2)
            elif day.weekday() == 5:
                day = day - timedelta(days=1)

            prices = list(db['real_time_prices'].find(
                {"ticker": ticker, "date": {"$gte": day, "$lte": day + timedelta(days=1)}},
                {"close": 1, "date": 1}
            ).sort("date", 1).limit(1))

            if prices:
                daily_close_prices[i] = prices[0]

        historical_prices[ticker] = daily_close_prices

    return historical_prices


def compute_trend(trend_data):
    return [0 if not item else (item['mentions'] if ('mentions' in item) else item['close']) for item in trend_data]


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

        combined_data = pd.merge(pd.DataFrame(trending_stocks), real_time_prices, on='ticker',
                                 suffixes=('_trending', '_real_time'))

        start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=29)
        historical_mentions = fetch_historical_mentions(tickers_stocks)
        historical_prices = fetch_historical_prices(tickers_stocks)
        combined_data['mention_trend'] = combined_data['ticker'].apply(lambda x: compute_trend(historical_mentions.get(x, [])))
        combined_data['price_trend'] = combined_data['ticker'].apply(lambda x: compute_trend(historical_prices.get(x, [])))

        data = {
            "trending_stocks": trending_stocks,
            "real_time_prices": real_time_prices,
            "combined_data": combined_data,
            "trend_period": [start_date + timedelta(days=i) for i in range(30)]
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
        columns = ["rank", "ticker", "name", "mentions", "rank_24h_ago", "mentions_24h_ago", "price", "volume", "mention_trend", "price_trend"]
        df = pd.DataFrame(combined_data, columns=columns)

        df.set_index('rank', inplace=True)

        selected_ticker = st.multiselect("Select stocks to display their trend:", df['ticker'].tolist(), default=None)

        if selected_ticker:
            fig = stgo.Figure()

            for ticker in selected_ticker:
                fig.add_trace(
                    stgo.Scatter(x=data['trend_period'],
                                 y=df[df['ticker'] == ticker]["mention_trend"].tolist()[0],
                                 name=f"{ticker} Mentions", marker=dict()),
                )

                fig.add_trace(
                    stgo.Scatter(x=data['trend_period'],
                                 y=df[df['ticker'] == ticker]['price_trend'].tolist()[0],
                                 name=f"{ticker} Price", marker=dict(), yaxis="y2"),
                )

            fig.update_layout(
                xaxis=dict(title="Date"),
                yaxis=dict(title="Mentions", side="left", rangemode="normal"),
                yaxis2=dict(title="Price", side="right", overlaying="y", rangemode="normal"),
                title="Stock Price and Mentions Over 30 Days"
            )

            st.plotly_chart(fig)

        st.dataframe(
            df,
            column_config={
                "mention_trend": st.column_config.AreaChartColumn(
                    label="Mention Trend (30 days)",
                    width="medium",
                    help="The trend of mentions in the last 30 days",
                    y_min=0,
                    y_max=max(df["mentions"])
                ),
                "price_trend": st.column_config.AreaChartColumn(
                    label="Price Trend (30 days)",
                    width="medium",
                    help="The trend of prices in the last 30 days",
                    y_min=0,
                    y_max=max(df["price"])
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
