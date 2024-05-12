from reddit_client import get_reddit_instance

def test_reddit_connection():
    reddit = get_reddit_instance()
    subreddit = reddit.subreddit("test")  # Using 'test' subreddit for safety
    for submission in subreddit.hot(limit=10):
        print(submission.title)  # Print the title of each post

if __name__ == "__main__":
    test_reddit_connection()
