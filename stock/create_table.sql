CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE INDEX idx_ticker_timestamp ON stock_prices(ticker, timestamp);
