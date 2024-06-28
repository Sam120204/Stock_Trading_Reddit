import os
import time
import dotenv
import nltk
from data_collection import get_reddit_data
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Load environment variables
dotenv.load_dotenv()

# Download the VADER lexicon
nltk.download('vader_lexicon')

# Initialize VADER SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    """
    Analyze sentiment using VADER sentiment analysis tool.

    Args:
        text (str): The text to analyze.

    Returns:
        float: Sentiment score between -1 and 1.
    """
    sentiment_scores = sia.polarity_scores(text)
    return sentiment_scores['compound']

def analyze_post_sentiment(post):
    """
    Analyze the sentiment of a Reddit post and its comments using VADER.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        float: Sentiment score between -1 and 1.
    """
    combined_text = (
        f"Title: {post['title']} (Score: {post['score']})\n"
        f"Body: {post['body']} (Score: {post['score']})\n"
        f"URL: {post['url']}\n"
        "Below is all comments:\n"
    )
    for comment in post['comments']:
        combined_text += f"Comment: {comment['body']} (Score: {comment['score']})\n"
        for reply in comment['replies']:
            combined_text += f"Reply: {reply['body']} (Score: {reply['score']})\n"
    
    return analyze_sentiment_vader(combined_text)

if __name__ == "__main__":
     # Start timing
    start_time = time.time()
    reddit_data = get_reddit_data()
    
    for i in range(10):
        sentiment = analyze_post_sentiment(reddit_data[i])
        print(f"URL: {reddit_data[i]['url']}, Sentiment: {sentiment}")
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"It takes {elapsed_time:.2f} seconds")