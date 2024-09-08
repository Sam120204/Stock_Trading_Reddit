from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv
import pytz  # Import pytz for timezone handling
import os

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

# Set up the Toronto timezone
TORONTO_TZ = pytz.timezone('America/Toronto')


def calculate_percentage_change(old_value, new_value):
    """Calculate percentage change between two values."""
    if old_value == 0:
        return 0 if new_value == 0 else 100
    return round(((new_value - old_value) / old_value) * 100, 2)


def get_24hr_indices(fetched_times):
    """Find the indices for the latest and 24-hour-ago fetched times within the last 24 hours."""
    # Get the current Toronto time and calculate the time 24 hours ago
    now_toronto = datetime.now(TORONTO_TZ)
    past_24hr_time = now_toronto - timedelta(hours=24)

    # Convert fetched times to datetime objects in Toronto timezone
    fetched_datetimes = [TORONTO_TZ.localize(datetime.strptime(ft, "%Y-%m-%d %H:%M:%S")) for ft in fetched_times]

    # Filter out times older than 24 hours
    fetched_within_24hrs = [(i, dt) for i, dt in enumerate(fetched_datetimes) if dt >= past_24hr_time]

    if not fetched_within_24hrs:
        # No fetched times within the last 24 hours
        return None, None

    # Find the earliest (closest to 24 hours ago) and latest within the 24-hour range
    closest_24hr_index = fetched_within_24hrs[0][0]  # Index of the first entry within the 24 hours range
    latest_index = fetched_within_24hrs[-1][0]  # Index of the last entry within the 24 hours range

    return closest_24hr_index, latest_index


def analyze_and_update_posts():
    """Analyze Reddit posts, calculate score and comment changes, and update the database."""
    posts = collection.find({})  # Fetch all posts or apply a filter if necessary

    for post in posts:
        fetched_times = post.get('fetched_times', [])
        number_of_scores = post.get('number_of_scores', [])
        number_of_comments = post.get('number_of_comments', [])

        if len(fetched_times) < 2:
            continue  # Skip posts with insufficient data

        # Get the 24-hour-ago and latest indices
        index_24hr_ago, latest_index = get_24hr_indices(fetched_times)

        if index_24hr_ago is not None:
            # Get scores and comments for the relevant times (24-hour comparison)
            score_24hr_ago = number_of_scores[index_24hr_ago]
            score_latest = number_of_scores[latest_index]

            comments_24hr_ago = number_of_comments[index_24hr_ago]
            comments_latest = number_of_comments[latest_index]

            # Calculate percentage changes for 24 hours
            score_change_24h = calculate_percentage_change(score_24hr_ago, score_latest)
            comment_change_24h = calculate_percentage_change(comments_24hr_ago, comments_latest)

            # Add the changes to MongoDB under 'score_change_24h' and 'comment_change_24h'
            collection.update_one(
                {"_id": post["_id"]},
                {"$push": {
                    "score_change_24h": score_change_24h,
                    "comment_change_24h": comment_change_24h
                }}
            )

            # Print or update MongoDB for 24-hour changes
            print(f"Updated post {post['_id']} with 24h score change: {score_change_24h}% and 24h comment change: {comment_change_24h}%")

            # Calculate recent (1-hour-like) changes only if the post is within the last 24 hours
            if len(fetched_times) >= 2:
                recent_index = len(fetched_times) - 1  # Last index
                previous_index = recent_index - 1  # Second-to-last index

                # Get scores and comments for the last two entries
                score_recent = number_of_scores[recent_index]
                score_previous = number_of_scores[previous_index]

                comments_recent = number_of_comments[recent_index]
                comments_previous = number_of_comments[previous_index]

                # Calculate percentage changes between the last two entries (1-hour-like)
                score_change_recent = calculate_percentage_change(score_previous, score_recent)
                comment_change_recent = calculate_percentage_change(comments_previous, comments_recent)

                # Add the recent changes to MongoDB under 'score_change_recent' and 'comment_change_recent'
                collection.update_one(
                    {"_id": post["_id"]},
                    {"$push": {
                        "score_change_recent": score_change_recent,
                        "comment_change_recent": comment_change_recent
                    }}
                )

                # Print or update MongoDB for recent (1-hour-like) changes
                print(f"Updated post {post['_id']} with recent score change: {score_change_recent}% and recent comment change: {comment_change_recent}%")


if __name__ == "__main__":
    analyze_and_update_posts()
