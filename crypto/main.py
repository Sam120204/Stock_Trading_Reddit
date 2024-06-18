from data_collection import get_reddit_data
from embedding import embed_text
from sentiment_analysis import analyze_sentiment
from vector_store import store_embeddings, retrieve_similar
import numpy as np

if __name__ == "__main__":
    # Fetch data from Reddit
    data = get_reddit_data()

    # Initialize lists to store embeddings and other information
    embeddings = []
    posts_info = []

    # Process each post
    for post in data:
        title = post['title']
        body = post['body']
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
            'embedding': embedding
        })

    # Convert embeddings to numpy array
    embeddings_np = np.array(embeddings)

    # Store embeddings in FAISS
    index = store_embeddings(embeddings_np)

    # Example query: retrieve similar embeddings
    query_embedding = embeddings_np[0]  # Use the first post's embedding as an example query
    distances, indices = retrieve_similar(index, np.expand_dims(query_embedding, axis=0))

    # Print similar posts
    print("Top 5 similar posts:")
    for i, idx in enumerate(indices[0]):
        print(f"Rank {i + 1}:")
        print(f"Title: {posts_info[idx]['title']}")
        print(f"Sentiment Score: {posts_info[idx]['sentiment_score']}")
        print(f"Distance: {distances[0][i]}")
