import praw
import dotenv
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

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
    post.comments.replace_more(limit=0)
    comments_data = []
    for comment in post.comments.list():
        if isinstance(comment, praw.models.MoreComments):
            continue
        comment_data = {
            'body': comment.body,
            'created_utc': datetime.utcfromtimestamp(comment.created_utc),
            'score': comment.score,
            'replies': []
        }
        for reply in comment.replies:
            if isinstance(reply, praw.models.MoreComments):
                continue
            reply_data = {
                'body': reply.body,
                'created_utc': datetime.utcfromtimestamp(reply.created_utc),
                'score': reply.score
            }
            comment_data['replies'].append(reply_data)
        comments_data.append(comment_data)
    return comments_data

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

                post_data = {
                    'title': post.title,
                    'body': post.selftext,
                    'created_utc': datetime.utcfromtimestamp(post.created_utc),
                    'score': post.score,
                    'comments': executor.submit(fetch_comments, post).result(),
                    'url': f"https://www.reddit.com{post.permalink}"
                }
                results.append(post_data)

    return results

def get_reddit_data(limit=100):
    reddit_api = setup_reddit_api()
    subreddits = [
        'wallstreetbets',
        # 'stocks',
        # 'pennystocks',
        # 'StockMarket',
        # 'EducatedInvesting',
        # 'Wallstreetbetsnew'
    ]

    data = fetch_posts_and_comments(reddit_api, subreddits, limit)
    return data

if __name__ == "__main__":
    data = get_reddit_data()
    print(f"Fetched {len(data)} posts from Reddit.")
    if len(data) > 0:
        first_post = data[0]
        print("\nFirst post information:")
        print(f"Title: {first_post['title']}")
        print(f"Body: {first_post['body']}")
        print(f"Created UTC: {first_post['created_utc']}")
        print(f"Score: {first_post['score']}")
        print(f"URL: {first_post['url']}")
        print("Comments:")
        for comment in first_post['comments']:
            print(f"  - {comment['body']} (Score: {comment['score']})")
            for reply in comment['replies']:
                print(f"    * {reply['body']} (Score: {reply['score']})")
    else:
        print("No posts found.")