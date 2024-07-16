CREATE TYPE post_status AS ENUM ('fetched', 'analyzed', 'dropped');

CREATE TABLE reddit_raw_posts (
    post_id VARCHAR(50) PRIMARY KEY,
    subreddit VARCHAR(50) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    post_time TIMESTAMP NOT NULL,
    status post_status NOT NULL DEFAULT 'fetched',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
);

CREATE TABLE reddit_post_scores (
    post_id VARCHAR(50) REFERENCES reddit_raw_posts(post_id),
    score INT,
    num_comments INT,
    sentiment_score NUMERIC(5, 2),
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SET client_encoding = 'UTF8';
