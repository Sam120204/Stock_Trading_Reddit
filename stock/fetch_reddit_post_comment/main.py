from data_collection import get_reddit_data
from text_embedding import get_text_embeddings
from sentiment_analysis import get_sentiment_scores
from database_operations import save_to_database

def process_reddit_data():
    reddit_data = get_reddit_data()

    # Flatten the text data for embedding and sentiment analysis
    all_texts = []
    for post in reddit_data:
        all_texts.append(post['title'])
        all_texts.append(post['body'])
        for comment in post['comments']:
            all_texts.append(comment['body'])
            for reply in comment['replies']:
                all_texts.append(reply['body'])

    # Generate embeddings
    embeddings = get_text_embeddings(all_texts)

    # Calculate sentiment scores
    sentiment_scores = get_sentiment_scores(all_texts)

    # Attach embeddings and sentiment scores back to the original data
    index = 0
    for post in reddit_data:
        post['embeddings'] = embeddings[index:index+2]  # title and body embeddings
        post['sentiment_scores'] = sentiment_scores[index:index+2]
        index += 2
        for comment in post['comments']:
            comment['embeddings'] = embeddings[index:index+1]
            comment['sentiment_scores'] = sentiment_scores[index:index+1]
            index += 1
            for reply in comment['replies']:
                reply['embeddings'] = embeddings[index:index+1]
                reply['sentiment_scores'] = sentiment_scores[index:index+1]
                index += 1

    # Save to database
    save_to_database(reddit_data)

if __name__ == "__main__":
    process_reddit_data()
    print("Processing complete and data saved to database.")
