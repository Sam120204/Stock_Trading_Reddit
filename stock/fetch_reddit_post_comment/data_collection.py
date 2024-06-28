import praw
import dotenv
import os
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
from filter_post import is_relevant_post  # Import the filtering function


# Function to setup Reddit API
def setup_reddit_api():
    dotenv.load_dotenv()
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")

    reddit = praw.Reddit(
        client_id=client_id, 
        client_secret=client_secret, 
        user_agent=user_agent, 
        username=username, 
        password=password
    )
    return reddit

def fetch_comments(post):
    """
    Fetch comments for a given Reddit post and count the number of comments.

    Args:
        post (praw.models.Submission): The Reddit post.
        nums (int): The number of comments to fetch.

    Returns:
        tuple: A tuple containing the list of comments data and the total number of comments.
    """
    post.comments.replace_more(limit=0)
    comments_data = []
    comment_count = 0
    for comment in post.comments.list():
        if isinstance(comment, praw.models.MoreComments):
            continue
        comment_count += 1
        comment_data = {
            'body': comment.body,
            'created_utc': datetime.utcfromtimestamp(comment.created_utc),
            'score': comment.score,
            'replies': []
        }
        for reply in comment.replies:
            if isinstance(reply, praw.models.MoreComments):
                continue
            comment_count += 1
            comment_data['replies'].append({
                'body': reply.body,
                'created_utc': datetime.utcfromtimestamp(reply.created_utc),
                'score': reply.score
            })
        comments_data.append(comment_data)
    return comments_data, comment_count

def fetch_posts_and_comments(reddit, subreddits, limit=100):
    results = []
    time_filter = int((datetime.utcnow() - timedelta(hours=24)).timestamp())

    with ThreadPoolExecutor(max_workers=10) as executor:
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            posts = subreddit.new(limit=limit)

            for post in posts:
                if post.created_utc < time_filter:
                    continue
                
                comments_data, comment_count = executor.submit(fetch_comments, post).result()
                post_data = {
                    'title': post.title,
                    'body': post.selftext,
                    'created_utc': datetime.utcfromtimestamp(post.created_utc),
                    'score': post.score,
                    'comments': comments_data,
                    'url': f"https://www.reddit.com{post.permalink}"
                }
                
                # Filter the post using is_relevant_post function
                if is_relevant_post(post_data) and comment_count >= 8:
                    results.append(post_data)

    return results

def get_reddit_data(limit=100):
    reddit_api = setup_reddit_api()
    subreddits = [
        'wallstreetbets',
        'stocks',
        'pennystocks',
        'StockMarket',
        'EducatedInvesting',
        'Wallstreetbetsnew'
    ]

    data = fetch_posts_and_comments(reddit_api, subreddits, limit)
    return data

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    data = get_reddit_data()
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Fetched {len(data)} posts from Reddit. And it takes {elapsed_time:.2f} seconds")
    for i in range(10):
        first_post = data[i]
        print(f"URL: {first_post['url']}")