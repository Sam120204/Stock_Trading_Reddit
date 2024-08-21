import os
from urllib.parse import quote_plus
import pytz
from datetime import datetime, timedelta
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB configuration
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
POSTS_COLLECTION_NAME = os.getenv('POSTS_COLLECTION_NAME')
COMMENTS_COLLECTION_NAME = os.getenv('COMMENTS_COLLECTION_NAME')

# Properly encode the username and password
encoded_username = quote_plus(MONGO_USERNAME)
encoded_password = quote_plus(MONGO_PASSWORD)

# Initialize MongoDB client
MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@trendsage.svfhdvw.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&authSource=admin"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts_collection = db[POSTS_COLLECTION_NAME]
comments_collection = db[COMMENTS_COLLECTION_NAME]

# Set the timezone for Waterloo, Canada
local_tz = pytz.timezone('America/Toronto')

def get_top_posts():
    # Get current UTC time and convert it to local timezone
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    local_now = utc_now.astimezone(local_tz)

    # Round down to the nearest hour
    local_now = local_now.replace(minute=0, second=0, microsecond=0)
    if local_now.hour % 3 != 0:
        local_now -= timedelta(hours=local_now.hour % 3)

    # Ensure we do not look at future entries if the hour is exactly a multiple of 3
    if local_now > utc_now.astimezone(local_tz):
        local_now -= timedelta(hours=3)

    rounded_down_hour_str = local_now.strftime('%Y-%m-%d %H:%M:%S')

    print("Fetching posts since:", rounded_down_hour_str)

    pipeline = [
        {
            "$addFields": {
                "last_fetched_time": {"$arrayElemAt": ["$fetched_times", -1]},
                "prev_fetched_time": {"$arrayElemAt": ["$fetched_times", -2]},
                "score_difference": {
                    "$subtract": [
                        {"$arrayElemAt": ["$number_of_scores", -1]},
                        {"$arrayElemAt": ["$number_of_scores", -2]}
                    ]
                }
            }
        },
        {
            "$match": {
                "last_fetched_time": {"$gte": rounded_down_hour_str}
            }
        },
        {
            "$sort": {"score_difference": -1}
        },
        {
            "$limit": 5
        },
        {
            "$project": {
                "_id": 0,  # Exclude the _id field
                "title": 1,
                "url": 1,
                "score_difference": 1,
                "prev_fetched_time": 1,
                "last_fetched_time": 1
            }
        }
    ]

    return list(posts_collection.aggregate(pipeline))


def display_dynamic_post(posts):
    st.title('Top Reddit Posts')

    for post in posts:
        # Creating a markdown string with a hyperlink to the post
        link = f"[{post['title']}]({post['url']})"
        st.markdown(link, unsafe_allow_html=True)
        st.text(f"Last Fetched: {post['last_fetched_time']} | Previous Fetched: {post['prev_fetched_time']}")
        st.text(f"Score Difference: {post['score_difference']}")
        st.write("---")  # Adding a line separator for visual clarity between posts


if __name__ == "__main__":
    # st.title("Top Posts in the Last 3 Hours")
    top_posts = get_top_posts()
    print(top_posts)
    display_dynamic_post(top_posts)
    #
    # for post in top_posts:
    #     st.write(f"Title: {post['title']}")
    #     st.write(f"URL: {post['url']}")
    #     st.write(f"Score Difference: {post['score_difference']}")
    #     st.write(f"Last Fetched Time: {post['last_fetched_time']}")
    #     st.write("---")