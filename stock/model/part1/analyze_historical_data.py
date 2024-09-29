from data_collection import get_reddit_data_from_urls, get_raw_reddit_data_from_urls
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
        SELECT post_id, url, ticker, id FROM reddit_raw_posts 
        WHERE status = 'fetched' AND post_time >= %s AND post_time < %s
    """, (start_time, end_time))
    rows = cur.fetchall()

    # Process each URL
    for row in rows:
        post_id, url, ticker, entry_id = row
        print(url)
        # try:
        posts = get_reddit_data_from_urls([url])
        print(posts)

        if not posts:
            cur.execute("""
                UPDATE reddit_raw_posts
                SET status = 'dropped'
                WHERE id = %s
            """, (entry_id,))

        for post in posts:

            cur.execute("SELECT EXISTS(SELECT 1 FROM reddit_post_scores WHERE id = %s)", (entry_id,))
            exists = cur.fetchone()[0]

            if not exists:
                # Analyze sentiment
                sentiment_score = analyze_post_sentiment(post, ticker)

                if sentiment_score == "Error: Unable to analyze sentiment":
                    cur.execute("""
                        UPDATE reddit_raw_posts
                        SET status = 'dropped'
                        WHERE id = %s
                    """, (entry_id,))
                    print(f"Post {post_id} dropped due to failed sentiment analysis")
                    continue

                # Store results in reddit_post_scores
                cur.execute("""
                    INSERT INTO reddit_post_scores (post_id, score, num_comments, sentiment_score, id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (post_id, post['score'], len(post['comments']), sentiment_score, entry_id))

                # Update the reddit_raw_posts table status to 'analyzed'
                cur.execute("""
                    UPDATE reddit_raw_posts
                    SET status = 'analyzed'
                    WHERE id = %s
                """, (entry_id,))

        # Commit the transaction for each URL
        conn.commit()
        #
        # except Exception as e:
        #     print(f"Error processing post_id {post_id}: {e}")
        #     conn.rollback()  # Rollback in case of error to maintain data integrity


def update_dropped_posts(start_time: datetime, end_time: datetime):
    # Update the data of posts that were dropped during processing
    cur.execute("""
            SELECT post_id, url, ticker, id FROM reddit_raw_posts 
            WHERE status = 'dropped' AND post_time >= %s AND post_time < %s
        """, (start_time, end_time))
    rows = cur.fetchall()

    for row in rows:
        post_id, url, ticker, entry_id = row

        posts = get_raw_reddit_data_from_urls([url])
        print(posts)

        if not posts:
            print(f"Post {post_id} is totally deleted and has no data")
            cur.execute("SELECT EXISTS(SELECT 1 FROM reddit_post_scores WHERE id = %s)", (entry_id,))
            exists = cur.fetchone()[0]
            if not exists:
                cur.execute("""
                                INSERT INTO reddit_post_scores (post_id, score, num_comments, sentiment_score, id)
                                VALUES (%s, %s, %s, %s)
                            """, (post_id, 0, 0, 0, entry_id))
        else:
            for post in posts:
                cur.execute("SELECT EXISTS(SELECT 1 FROM reddit_post_scores WHERE id = %s)", (entry_id,))
                exists = cur.fetchone()[0]

                if not exists:
                    print("DROPPED UPDATED:", post['score'], len(post['comments']))
                    cur.execute("""
                                    INSERT INTO reddit_post_scores (post_id, score, num_comments, sentiment_score, id)
                                    VALUES (%s, %s, %s, %s)
                                """, (post_id, post['score'], len(post['comments']), 0, entry_id))

        conn.commit()




# Example usage
start_time = datetime(2023, 8, 13)  # Start time is inclusive
end_time = datetime(2024, 9, 29)  # End time is exclusive
fetch_and_process_posts(start_time, end_time)
# update_dropped_posts(start_time, end_time)

# Close the cursor and connection
cur.close()
conn.close()
