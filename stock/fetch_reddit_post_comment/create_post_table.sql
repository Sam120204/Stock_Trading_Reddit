CREATE TABLE reddit_posts (
    post_id VARCHAR(50) PRIMARY KEY,
    subreddit VARCHAR(50) NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    author VARCHAR(50),
    post_time TIMESTAMP NOT NULL,
    score INT,
    num_comments INT
);

CREATE TABLE reddit_sentiment_score (
    score_id SERIAL PRIMARY KEY,
    post_id VARCHAR(50) REFERENCES Posts(post_id),
    sentiment_score NUMERIC(5, 2),
    analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
