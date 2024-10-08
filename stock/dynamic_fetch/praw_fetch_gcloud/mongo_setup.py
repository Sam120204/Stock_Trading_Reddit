import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import time
from dotenv import load_dotenv
from urllib.parse import quote_plus
from fetch_posts_from_praw import fetch_prev_day_posts, fetch_all_comments_from_url

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

def round_to_nearest_hour(dt):
    if dt.minute >= 30:
        dt = dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    else:
        dt = dt.replace(minute=0, second=0, microsecond=0)
    return dt

def format_time(dt):
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def insert_or_update_post(post):
    post_id = post['id']
    title = post['title']
    # sentiment_score = post.get('sentiment_score', 0.75)  # Placeholder sentiment score
    number_of_scores = post['score']
    number_of_comments = post['num_comments']
    url = post['url']
    tickers = post.get('tickers', [])
    fetched_time = format_time(round_to_nearest_hour(datetime.now(local_tz)))

    existing_post = posts_collection.find_one({'_id': post_id})

    if existing_post:
        posts_collection.update_one(
            {'_id': post_id},
            {'$push': {
                # 'sentiment_scores': sentiment_score,
                'fetched_times': fetched_time,
                'number_of_scores': number_of_scores,
                'number_of_comments': number_of_comments
            },
            '$set': {'url': url, 'title': title, 'tickers': tickers}}
        )
    else:
        new_post = {
            '_id': post_id,
            'title': title,
            'number_of_scores': [number_of_scores],
            'number_of_comments': [number_of_comments],
            # 'sentiment_scores': [sentiment_score],
            'url': url,
            'tickers': tickers,
            'fetched_times': [fetched_time]
        }
        posts_collection.insert_one(new_post)

def insert_or_update_comment(comment):
    comment_id = comment['comment_url'].split('/')[-2]  # Use the comment URL to generate a unique ID
    post_url = comment['post_url']
    comment_scores = comment['comment_scores']
    comment_url = comment['comment_url']
    fetched_time = format_time(round_to_nearest_hour(datetime.now(local_tz)))
    
    existing_comment = comments_collection.find_one({'_id': comment_id})

    if existing_comment:
        comments_collection.update_one(
            {'_id': comment_id},
            {'$push': {
                'fetched_times': fetched_time,
                'comment_scores': comment_scores
             },
             '$set': {'post_url': post_url, 'comment_url': comment_url}}
        )
    else:
        new_comment = {
            '_id': comment_id,
            'post_url': post_url,
            'comment_scores': [comment_scores],
            'comment_url': comment_url,
            'fetched_times': [fetched_time]
        }
        comments_collection.insert_one(new_comment)
        
def main():
    # Start timing
    start_timing  = time.time()
    # Specify the subreddit and time period
    subreddit = 'wallstreetbets'

    end_time = round_to_nearest_hour(datetime.now(local_tz))  # End time is exclusive
    start_time = end_time - timedelta(days=4)  # Start time is inclusive
    start_epoch = int(start_time.timestamp())
    end_epoch = int(end_time.timestamp())
    # Fetch and store posts
    all_posts = fetch_prev_day_posts(subreddit, start_epoch, end_epoch)

    # Insert or update posts in MongoDB
    for post in all_posts:
        insert_or_update_post(post)
        # Fetch and store comments for each post
        comments = fetch_all_comments_from_url([post['url']], post['score'])
        for comment in comments:
            insert_or_update_comment(comment)
    
    # End timing
    end_timing = time.time()
    elapsed_time = end_timing - start_timing
    print(f"Total elapsed time: {elapsed_time:.2f} seconds")



if __name__ == "__main__":
    main()
