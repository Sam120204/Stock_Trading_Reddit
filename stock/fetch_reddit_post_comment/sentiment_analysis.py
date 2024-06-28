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
    combined_text+="Below is all comments"
    for comment in post['comments']:
        combined_text += f"Comment: {comment['body']} (Score: {comment['score']})\n"
        for reply in comment['replies']:
            combined_text += f"Reply: {reply['body']} (Score: {reply['score']})\n"
    
    return analyze_sentiment(combined_text)


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
