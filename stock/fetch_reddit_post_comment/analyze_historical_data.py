from data_collection import get_reddit_data_from_urls
from sentiment_analysis import analyze_post_sentiment
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
load_dotenv()

# PostgreSQL's connection details
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("DBPORT")
)
cur = conn.cursor()


def fetch_and_process_posts(start_time: datetime, end_time: datetime):
    # Fetch URLs from the reddit_raw_posts table between the given dates
    cur.execute("""
        SELECT post_id, url FROM reddit_raw_posts 
        WHERE status = 'fetched' AND post_time >= %s AND post_time < %s
    """, (start_time, end_time))
    rows = cur.fetchall()

    # Process each URL
    for row in rows:
        post_id, url = row
        print(url)
        try:
            posts = get_reddit_data_from_urls([url])
            print(posts)

            for post in posts:
                # Analyze sentiment
                sentiment_score = analyze_post_sentiment(post['content'])

                # Store results in reddit_post_scores
                cur.execute("""
                    INSERT INTO reddit_post_scores (post_id, score, num_comments, sentiment_score)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (post_id) DO UPDATE
                    SET score = EXCLUDED.score,
                        num_comments = EXCLUDED.num_comments,
                        sentiment_score = EXCLUDED.sentiment_score,
                        analysis_time = CURRENT_TIMESTAMP
                """, (post_id, post['score'], post['num_comments'], sentiment_score))

                # Update the reddit_raw_posts table status to 'analyzed'
                cur.execute("""
                    UPDATE reddit_raw_posts
                    SET status = 'analyzed'
                    WHERE post_id = %s
                """, (post_id,))

            # Commit the transaction for each URL
            conn.commit()

        except Exception as e:
            print(f"Error processing post_id {post_id}: {e}")
            conn.rollback()  # Rollback in case of error to maintain data integrity


# Example usage
start_time = datetime(2024, 6, 29)  # Start time is inclusive
end_time = datetime(2024, 7, 1)  # End time is exclusive
fetch_and_process_posts(start_time, end_time)

# Close the cursor and connection
cur.close()
conn.close()