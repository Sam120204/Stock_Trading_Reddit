import openai
import os
import dotenv
from data_collection import get_reddit_data

# Load environment variables
dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_text_embeddings(texts):
    embeddings = []
    for text in texts:
        response = openai.Embedding.create(
            input=text,
            model="text-embedding-3-large"
        )
        embeddings.append(response['data'][0]['embedding'])
    return embeddings

def add_embeddings_to_data(reddit_data):
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
    
    # Attach embeddings back to the original data
    index = 0
    for post in reddit_data:
        post['title_embedding'] = embeddings[index]
        post['body_embedding'] = embeddings[index + 1]
        index += 2
        for comment in post['comments']:
            comment['embedding'] = embeddings[index]
            index += 1
            for reply in comment['replies']:
                reply['embedding'] = embeddings[index]
                index += 1
    
    return reddit_data

if __name__ == "__main__":
    reddit_data = get_reddit_data()
    enriched_data = add_embeddings_to_data(reddit_data)
    print(enriched_data)
