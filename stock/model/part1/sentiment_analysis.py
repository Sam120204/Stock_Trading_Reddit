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

def analyze_sentiment(text, ticker):
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": 
                               f"Analyze the overall sentiment of the following Reddit post and its comments regarding the specific ticker {ticker}. "
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

def chunk_text(title, body, comments, max_tokens=8192):
    combined_text = f"Title: {title}\nBody: {body}\n"
    chunked_texts = [combined_text]
    current_chunk = combined_text

    for comment in comments:
        comment_text = f"Comment: {comment['body']} (Score: {comment['score']})\n"
        if len(current_chunk) + len(comment_text) > max_tokens:
            chunked_texts.append(current_chunk)
            current_chunk = combined_text + comment_text
        else:
            current_chunk += comment_text
        for reply in comment.get('replies', []):
            reply_text = f"Reply: {reply['body']} (Score: {reply['score']})\n"
            if len(current_chunk) + len(reply_text) > max_tokens:
                chunked_texts.append(current_chunk)
                current_chunk = combined_text + reply_text
            else:
                current_chunk += reply_text

    if current_chunk:
        chunked_texts.append(current_chunk)
    
    return chunked_texts

def analyze_post_sentiment(post, ticker):
    title = post['title']
    body = post['body']
    comments = post['comments']
    chunked_texts = chunk_text(title, body, comments)

    sentiment_scores = []
    for chunk in chunked_texts:
        sentiment = analyze_sentiment(chunk, ticker)
        try:
            sentiment_scores.append(float(sentiment))
        except ValueError:
            continue
    
    if sentiment_scores:
        return round(sum(sentiment_scores) / len(sentiment_scores), 4)
    else:
        return "Error: Unable to analyze sentiment"

if __name__ == "__main__":
    # Start timing
    start_time = time.time()
    
    # Load the Reddit data
    reddit_data = get_reddit_data()
    
    # Analyze sentiment and save to new data structure
    rows = []
    for post in reddit_data:
        combined_text = f"Title: {post['title']}\nBody: {post['body']}\n"
        for comment in post['comments']:
            combined_text += f"Comment: {comment['body']} (Score: {comment['score']})\n"
            for reply in comment['replies']:
                combined_text += f"Reply: {reply['body']} (Score: {reply['score']})\n"
        
        sentiment = analyze_post_sentiment(post)
        print(f"URL: {post['url']}, Sentiment: {sentiment}")
        
        rows.append({
            'combined_text': combined_text,
            'sentiment': sentiment,
            'post_score': post['score']
        })
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(rows)
    df.to_csv('reddit_data_with_sentiment.csv', index=False)
    
    # End timing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"It takes {elapsed_time:.2f} seconds")
