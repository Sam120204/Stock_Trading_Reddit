import pandas as pd
from openai import OpenAI
import os
import dotenv
import time
from data_collection import get_reddit_data

# Load environment variables
dotenv.load_dotenv()
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

def analyze_sentiment(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": 
                               f"Analyze the overall sentiment of the following Reddit post and its comments regarding the mentioned stock ticker or company. "
                               f"Consider the title, body, comments, and especially their scores (upvotes-downvotes by viewers) as indicators of the sentiment. "
                               f"Focus on the general sentiment about the stock ticker or company discussed in the post considering whole posts and comments with scores, rather than individual agreement or disagreement with specific comments. "
                               f"You should just tell me a sentiment score between -1 and 1 without any further explanation. "
                               f"A score of -1 means that the sentiment towards the stock ticker or company is very negative, indicating that the general view is pessimistic or bearish. "
                               f"A score of 0 means that the sentiment is neutral, indicating that the general view is neither positive nor negative. "
                               f"A score of 1 means that the sentiment is very positive, indicating that the general view is optimistic or bullish.\n\n"
                               f"{text}"
                }
            ],
            stream=True,
            max_tokens=15
        )
        sentiment = ""
        for chunk in response:
            sentiment += chunk.choices[0].delta.content or ""
        return sentiment.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_post_sentiment(post):
    combined_text = (
        f"Title: {post['title']} (Score: {post['score']})\n"
        f"Body: {post['body']} (Score: {post['score']})\n"
        f"URL: {post['url']}\n"
    )
    combined_text += "Below is all comments\n"
    for comment in post['comments']:
        combined_text += f"Comment: {comment['body']} (Score: {comment['score']})\n"
        for reply in comment['replies']:
            combined_text += f"Reply: {reply['body']} (Score: {reply['score']})\n"
    
    return analyze_sentiment(combined_text)

if __name__ == "__main__":
    # Load the Reddit data
    reddit_data = get_reddit_data()
    # Start timing
    start_time = time.time()
    # Analyze sentiment and save to new CSV
    sentiments = []
    for i in range(len(reddit_data)):
        sentiment = analyze_post_sentiment(reddit_data[i])
        print(f"URL: {reddit_data[i]['url']}, Sentiment: {sentiment}")
        reddit_data[i]['sentiment'] = sentiment
        sentiments.append(reddit_data[i])

    # Convert to DataFrame and save to CSV
    rows = []
    for post in sentiments:
        post_info = {
            'post_title': post['title'],
            'post_body': post['body'],
            'post_created_utc': post['created_utc'],
            'post_score': post['score'],
            'post_url': post['url'],
            'sentiment': post['sentiment']  # Add sentiment to the post info
        }
        for comment in post['comments']:
            comment_info = {
                'comment_body': comment['body'],
                'comment_created_utc': comment['created_utc'],
                'comment_score': comment['score']
            }
            # Add comment info with post info
            rows.append({**post_info, **comment_info, 'reply_body': '', 'reply_score': ''})
            for reply in comment['replies']:
                reply_info = {
                    'reply_body': reply['body'],
                    'reply_created_utc': reply['created_utc'],
                    'reply_score': reply['score']
                }
                # Add reply info with post and comment info
                rows.append({**post_info, **comment_info, **reply_info})

    df = pd.DataFrame(rows)
    df.to_csv('reddit_data_with_sentiment.csv', index=False)

    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"It takes {elapsed_time:.2f} seconds")
