import praw
import dotenv
import os
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from filter_post import is_relevant_post

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

def fetch_post_info_on_url(reddit, url):
    """
    Fetch details of a Reddit post using its URL.

    Args:
        reddit (praw.Reddit): The Reddit instance.
        url (str): The URL of the Reddit post.

    Returns:
        dict: A dictionary containing post details.
    """
    # Extract the submission ID from the URL
    submission_id = url.split('/')[-3]
    
    # Fetch the submission
    submission = reddit.submission(id=submission_id)
    
    # Fetch comments data and count
    comments_data, comment_count = fetch_comments(submission)
    
    # Return post details
    post_info = {
        'title': submission.title,
        'body': submission.selftext,
        'score': submission.score,
        'comments': comments_data,
        'url': submission.url
    }
    
    return post_info

def fetch_posts_and_comments(reddit, subreddits, limit=100):
    results = []
    time_filter = int((datetime.utcnow() - timedelta(hours=24)).timestamp())

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for subreddit_name in subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            posts = subreddit.new(limit=limit)

            for post in posts:
                if post.created_utc < time_filter:
                    continue
                futures.append(executor.submit(fetch_post_info_on_url, reddit, f"https://www.reddit.com{post.permalink}"))
        
        for future in as_completed(futures):
            post_data = future.result()
            if is_relevant_post(post_data) and len(post_data['comments']) >= 30:
                results.append(post_data)

    return results

def fetch_posts_and_comments_parallel(reddit, urls):
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_post_info_on_url, reddit, url) for url in urls]

        for future in as_completed(futures):
            post_data = future.result()
            if len(post_data['comments']) + post_data['score'] >= 40: # adjust this if necessary
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

def get_reddit_data_from_urls(urls):
    reddit_api = setup_reddit_api()
    data = fetch_posts_and_comments_parallel(reddit_api, urls)
    return data

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    
    # # Fetch data using subreddits
    # data = get_reddit_data()
    # print(data)
    # print(f"Fetched {len(data)} posts from Reddit using subreddits.")

    # Example URLs
    urls = [
        'https://www.reddit.com/r/wallstreetbets/comments/1dtyos2/nvda_si_on_the_rise/',
        'https://www.reddit.com/r/wallstreetbets/comments/1dtv40t/how_do_you_guys_consistently_stay_profitable/'
    ]

    # Fetch data using URLs
    url_data = get_reddit_data_from_urls(urls)
    print(f"Fetched {len(url_data)} posts from Reddit using URLs.")

    # Print a sample of the fetched data
    for i in range(min(10, len(url_data))):
        print(url_data[i])

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
