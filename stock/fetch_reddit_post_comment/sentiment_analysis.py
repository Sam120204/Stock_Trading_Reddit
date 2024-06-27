from openai import OpenAI
import os
import dotenv
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
                               f"Analyze the overall sentiment score of the following Reddit post. "
                                f"Consider the title, body, comments, and especially their scores (upvotes-downvotes by viewers) as indicators of the sentiment. "
                                f"You should just tell me a score number between -100 and 100 without any further explanation and "
                                f"A score of -100 means that the viewers significantly disagree with the post, considering it to be very negative or misleading (like a 'shit post' about this stock ticker). "
                                f"A score of 0 means that the viewers keeps nuturel with the post, considering it neither postive nor negative about this stock ticker. "
                                f"A score of 100 means that the viewers significantly agree with the post, finding it very positive or accurate (everyone feels the post is right in its opinion on this stock ticker).\n\n"
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
    reddit_data = get_reddit_data()
    
    for i in range(10):
        sentiment = analyze_post_sentiment(reddit_data[i])
        print(f"URL: {reddit_data[i]['url']}, Sentiment: {sentiment}")
