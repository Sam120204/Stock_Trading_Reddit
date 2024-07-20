import praw
import re

# Initialize PRAW
reddit = praw.Reddit(client_id='L5x_OBLY_HG9UxgxfOg69Q',
                     client_secret='3f2igWO4Hdcu404B3KxVV81nE_hnsA',
                     user_agent='python:StockPredictionApp:v1.0 (by /u/Stock_prediction)')

def get_post_details(url):
    # Extract post ID from URL
    match = re.search(r'/comments/([a-z0-9]+)', url)
    if not match:
        return None
    
    post_id = match.group(1)
    
    # Fetch the post using PRAW
    try:
        submission = reddit.submission(id=post_id)
        return {'score': submission.score, 'num_comments': submission.num_comments}
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # Read URLs from file
    with open('post_urls.txt', 'r') as f:
        urls = f.readlines()
    
    for url in urls:
        url = url.strip()
        post_details = get_post_details(url)
        if post_details:
            print(f"URL: {url} -> Score: {post_details['score']}, Number of comments: {post_details['num_comments']}")
        else:
            print(f"Failed to fetch post details for URL: {url}")
