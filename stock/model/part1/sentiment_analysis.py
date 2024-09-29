import pandas as pd
from openai import OpenAI
import os
import dotenv
import praw
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
                    # "content": improved but bad prompt
                    #            f"Analyze the overall sentiment of the following Reddit post and its comments regarding the specific ticker {ticker}. "
                    #            f"Consider the title, body, comments, and especially their scores (upvotes-downvotes by viewers) as indicators of the sentiment. "
                    #            f"Give special weight to comments with significantly higher scores than the post itself, as these may indicate a stronger community sentiment that could override the post's original message. However, ensure that the overall sentiment score reflects the collective view expressed in both the post and its comments."
                    #            f"Pay special attention to the relative relationship between the post's score and the scores of its comments. "
                    #            f"If a post has many comments with similar scores, this should be weighted similarly to a post with a single, very high score, ensuring that the general sentiment reflects the overall community engagement. "
                    #            f"Focus on the general sentiment about the stock ticker or company discussed in the post considering whole posts and comments with scores, rather than individual agreement or disagreement with specific comments. "
                    #            f"You should just tell me a sentiment score between -1 and 1 without any further explanation. "
                    #            f"A score of -1 means that the sentiment towards the stock ticker or company is very negative, indicating that the general view is pessimistic or bearish. "
                    #            f"A score of 0 means that the sentiment is neutral, indicating that the general view is neither positive nor negative. "
                    #            f"A score of 1 means that the sentiment is very positive, indicating that the general view is optimistic or bullish.\n\n"
                    #            f"{text}"
                    # "content":
                    #     f"Analyze the overall sentiment of the following Reddit post and its comments regarding the specific ticker {ticker}. "
                    #     f"Consider the title, body, comments, and especially their scores (upvotes-downvotes by viewers) as indicators of the sentiment. "
                    #     f"Focus on the general sentiment about the specific ticker or company {ticker} in the post considering whole posts and comments with scores, rather than individual agreement or disagreement with specific comments. "
                    #     f"You should just tell me a sentiment score between -1 and 1 without any further explanation. "
                    #     f"A score of -1 means that the sentiment towards the stock ticker or company {ticker} is very negative, indicating that the general view towards ticker {ticker} is pessimistic or bearish. "
                    #     f"A score of 0 means that the sentiment is neutral, indicating that the general view towards ticker {ticker} is neither positive nor negative."
                    #     f"A score of 1 means that the sentiment is very positive, indicating that the general view towards ticker {ticker} is optimistic or bullish.\n\n"
                    #     f"{text}"
                    "content":
    f"Analyze the overall sentiment of the following Reddit post and its comments regarding the likelihood of price growth for the specific ticker {ticker}. "
    f"Consider the title, body, comments, and especially their scores (upvotes-downvotes by viewers) as indicators of the sentiment. "
    f"Focus on the general sentiment about the potential price growth of ticker {ticker} in the post, considering all posts and comments with scores, rather than individual agreement or disagreement with specific comments. "
    f"You should just tell me a sentiment score between -1 and 1 without any further explanation. "
    f"A score of -1 means that the sentiment is very negative, indicating a general expectation that the price of ticker {ticker} will fall. "
    f"A score of 0 means that the sentiment is neutral, indicating that either the ticker {ticker} is not generally discussed or the expectations about the price movement of ticker {ticker} are neither strongly positive nor negative. "
    f"A score of 1 means that the sentiment is very positive, indicating a general expectation that the price of ticker {ticker} will grow.\n\n"
    f"{text}"


                }
            ],
            stream=True,
            max_tokens=15
        )
        sentiment = ""
        for chunk in response:
            # Safely concatenate content if it's not None
            content = chunk.choices[0].delta.content
            if content:
                sentiment += content
                print(content, end="")  # Print the chunk as it arrives
        print(sentiment.strip())
        return sentiment.strip()
    except Exception as e:
        print(f"Error analyzing sentiment: {str(e)}")
        return None


def chunk_text(title, body, comments, score, num_comments, max_tokens=8192):
    combined_text = f"Title: {title}\nBody: {body}\n"
    chunked_texts = []
    current_chunk = combined_text

    # Filter and sort comments based on the absolute value of their scores
    filtered_comments = [
        comment for comment in comments
        # if (abs(comment['score']) + 2 * len(comment.get('replies', []))) > (abs(score) + 2 * num_comments) * 0.05
    ]
    sorted_comments = sorted(filtered_comments, key=lambda c: (abs(c['score']) + 2 * len(c.get('replies', []))), reverse=True)

    # Process only the top 10 comments with the highest scores
    for comment in sorted_comments[:5]:
        comment_text = f"Comment: {comment['body']} (Score: {comment['score']})\n"
        if len(current_chunk) + len(comment_text) > max_tokens:
            chunked_texts.append(current_chunk)
            current_chunk = combined_text + comment_text
        else:
            current_chunk += comment_text
        # Check replies in the comment if they exist and meet the criteria
        for reply in comment.get('replies', []):
            if (abs(reply['score']) + len(reply.get('replies', []))) > (abs(comment['score']) + 2 * len(comment.get('replies', []))) * 0.20:
                reply_text = f"Reply: {reply['body']} (Score: {reply['score']})\n"
                if len(current_chunk) + len(reply_text) > max_tokens:
                    chunked_texts.append(current_chunk)
                    current_chunk = combined_text + reply_text
                else:
                    current_chunk += reply_text

    # Append the last chunk if it's not empty
    if current_chunk != combined_text:
        chunked_texts.append(current_chunk)
    return chunked_texts


def analyze_post_sentiment(post, ticker):
    title = post['title']
    body = post['body']
    comments = post['comments']
    score = post['score']
    num_comments = len(comments)

    chunked_texts = chunk_text(title, body, comments, score, num_comments)
    # print(chunked_texts)

    sentiment_scores = []
    for chunk in chunked_texts:
        sentiment = analyze_sentiment(chunk, ticker)
        if sentiment is not None:
            try:
                sentiment_scores.append(float(sentiment))
            except ValueError:
                continue

    if sentiment_scores:
        return round(sum(sentiment_scores) / len(sentiment_scores), 4)
    else:
        return "Error: Unable to analyze sentiment"


# ADDing URL as input function
def get_reddit_post_from_url(url):
    # Initialize Reddit API client
    reddit = praw.Reddit(
        client_id=os.environ.get("REDDIT_CLIENT_ID"),
        client_secret=os.environ.get("REDDIT_CLIENT_SECRET"),
        user_agent=os.environ.get("REDDIT_USER_AGENT"),
        username=os.environ.get("REDDIT_USERNAME"),
        password=os.environ.get("REDDIT_PASSWORD")
    )

    submission = reddit.submission(url=url)

    # Gather post details
    post = {
        'title': submission.title,
        'body': submission.selftext,
        'score': submission.score,
        'url': url,
        'comments': []
    }

    # Gather top-level comments and their replies
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        comment_data = {
            'body': comment.body,
            'score': comment.score,
            'replies': [
                {'body': reply.body, 'score': reply.score}
                for reply in comment.replies
            ]
        }
        post['comments'].append(comment_data)

    return post

def analyze_reddit_url_sentiment(url, ticker):
    post = get_reddit_post_from_url(url)
    sentiment = analyze_post_sentiment(post, ticker)
    return sentiment


if __name__ == "__main__":
    reddit_url = input("Enter a Reddit URL: ")
    ticker = input("Enter the stock ticker: ")

    sentiment_score = analyze_reddit_url_sentiment(reddit_url, ticker)
    print(f"Sentiment score for {ticker} from the post at {reddit_url}: {sentiment_score}")
#
# if __name__ == "__main__":
#     start_time = time.time()
#
#     # Load the Reddit data
#     reddit_data = get_reddit_data()
#
#     rows = []
#     for post in reddit_data:
#         combined_text = f"Title: {post['title']}\nBody: {post['body']}\n"
#         for comment in post['comments']:
#             combined_text += f"Comment: {comment['body']} (Score: {comment['score']})\n"
#             for reply in comment.get('replies', []):
#                 combined_text += f"Reply: {reply['body']} (Score: {reply['score']})\n"
#
#         sentiment = analyze_post_sentiment(post, "AAPL")
#         print(f"URL: {post['url']}, Sentiment: {sentiment}")
#
#         rows.append({
#             'combined_text': combined_text,
#             'sentiment': sentiment,
#             'post_score': post['score']
#         })
#
#     # Convert to DataFrame and save to CSV
#     df = pd.DataFrame(rows)
#     df.to_csv('reddit_data_with_sentiment.csv', index=False)
#
#     elapsed_time = time.time() - start_time
#     print(f"Processing completed in {elapsed_time:.2f} seconds")
