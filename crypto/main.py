from data_collection import get_reddit_data
from embedding import embed_text
from sentiment_analysis import analyze_sentiment
from vector_store import store_embeddings, retrieve_similar
import numpy as np

if __name__ == "__main__":
    # Fetch data from Reddit
    try:
        data = get_reddit_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        exit(1)

    # Initialize lists to store embeddings and other information
    embeddings = []
    posts_info = []

    # Process each post
    for post in data:
        try:
            title = post['title']
            body = post['body']
            url = post['url']  # Get the post URL
            text = f"{title} {body}"

            # Generate embedding
            embedding = embed_text(text)
            embeddings.append(embedding)

            # Analyze sentiment
            sentiment_score = analyze_sentiment(text)

            # Store post information
            posts_info.append({
                'title': title,
                'body': body,
                'score': post['score'],
                'created_utc': post['created_utc'],
                'sentiment_score': sentiment_score,
                'embedding': embedding,
                'url': url  # Store the URL
            })
        except Exception as e:
            print(f"Error processing post: {post['title']}. Error: {e}")
            continue

    # Convert embeddings to numpy array
    try:
        embeddings_np = np.array(embeddings)
    except Exception as e:
        print(f"Error converting embeddings to numpy array: {e}")
        exit(1)

    # Store embeddings in FAISS
    try:
        index = store_embeddings(embeddings_np)
    except Exception as e:
        print(f"Error storing embeddings in FAISS: {e}")
        exit(1)

    # Example query: retrieve similar embeddings
    try:
        query_embedding = embeddings_np[0]  # Use the first post's embedding as an example query
        distances, indices = retrieve_similar(index, np.expand_dims(query_embedding, axis=0), k=15)  # Change k to 15 to retrieve top 15 posts

        # Print similar posts
        print("Top 15 similar posts:")
        for i, idx in enumerate(indices[0]):
            print(f"Rank {i + 1}:")
            print(f"Title: {posts_info[idx]['title']}")
            print(f"URL: {posts_info[idx]['url']}")  # Print the URL
            print(f"Sentiment Score: {posts_info[idx]['sentiment_score']}")
            print(f"Distance: {distances[0][i]}")
    except Exception as e:
        print(f"Error retrieving similar embeddings: {e}")
        exit(1)
