import psycopg2
import os
import dotenv

dotenv.load_dotenv()

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )
    return conn

def save_to_database(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    for item in data:
        cursor.execute(
            """
            INSERT INTO reddit_data (title, body, created_utc, score, url, embeddings, sentiment_scores)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (item['title'], item['body'], item['created_utc'], item['score'], item['url'], item['embeddings'], item['sentiment_scores'])
        )
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    sample_data = [
        {
            'title': 'Sample Post',
            'body': 'This is a sample post.',
            'created_utc': '2023-06-26 12:00:00',
            'score': 100,
            'url': 'http://example.com',
            'embeddings': np.random.rand(1, 384).tolist(),
            'sentiment_scores': {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
        }
    ]
    save_to_database(sample_data)
