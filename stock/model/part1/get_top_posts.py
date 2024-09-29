import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

# MongoDB configuration
MONGO_USERNAME = os.getenv('MONGO_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
DB_NAME = os.getenv('POST_DB_NAME')
POSTS_COLLECTION_NAME = os.getenv('POSTS_COLLECTION_NAME')
COMMENTS_COLLECTION_NAME = os.getenv('COMMENTS_COLLECTION_NAME')

# Properly encode the username and password
encoded_username = quote_plus(MONGO_USERNAME)
encoded_password = quote_plus(MONGO_PASSWORD)

MONGO_URI = f"mongodb+srv://{encoded_username}:{encoded_password}@trendsage.svfhdvw.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&authSource=admin"
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
posts_collection = db[POSTS_COLLECTION_NAME]
# comments_collection = db[COMMENTS_COLLECTION_NAME]

time_intervals = {
    '1_hour': 1,
    '2_hours': 2,
    '3_hours': 3,
    '6_hours': 6,
    '12_hours': 12,
    '1_day': 24
}

current_time = datetime.strptime('2024-08-14 00:00:00', "%Y-%m-%d %H:%M:%S")

posts = posts_collection.find({
    "fetched_times": "2024-08-14 00:00:00"
})

top_posts_by_interval = {interval: [] for interval in time_intervals}

# Process each post
for post in posts:
    title = post['title']
    number_of_comments = [int(nc['$numberInt']) for nc in post['number_of_comments']]
    number_of_scores = [int(ns['$numberInt']) for ns in post['number_of_scores']]
    fetched_times = [datetime.strptime(ft, "%Y-%m-%d %H:%M:%S") for ft in post['fetched_times']]

    # Sort fetched_times just to be sure
    fetched_times.sort()

    # Calculate the changes for each time interval
    for interval_name, hours in time_intervals.items():
        time_threshold = current_time - timedelta(hours=hours)

        # Find the latest index and the closest index to the time threshold
        latest_index = len(fetched_times) - 1
        threshold_index = next((i for i, t in enumerate(fetched_times) if t <= time_threshold), 0)

        # Calculate changes
        comment_change = number_of_comments[latest_index] - number_of_comments[threshold_index]
        score_change = number_of_scores[latest_index] - number_of_scores[threshold_index]
        total_change = comment_change + score_change

        # Store the post information along with the total change
        top_posts_by_interval[interval_name].append({
            'title': title,
            'comment_change': comment_change,
            'score_change': score_change,
            'total_change': total_change
        })

# Sort the posts by the largest change and get the top 5 for each interval
for interval_name in time_intervals:
    top_posts_by_interval[interval_name] = sorted(
        top_posts_by_interval[interval_name],
        key=lambda p: p['total_change'],
        reverse=True
    )[:5]

# Display the top posts for each interval
for interval_name, top_posts in top_posts_by_interval.items():
    print(f"Top 5 posts for {interval_name}:")
    for post in top_posts:
        print(f"  Title: {post['title']}, Comment Change: {post['comment_change']}, Score Change: {post['score_change']}, Total Change: {post['total_change']}")



