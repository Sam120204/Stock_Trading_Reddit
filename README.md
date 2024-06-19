# TrendSage - Stock and Crypto Prediction Reddit Tool

## Overview

TrendSage aims to develop a correlation between stock and cryptocurrency predictions based on the posts or comments on Reddit and the actual market trends. The project consists of three phases, each focusing on different aspects of data collection, analysis, and prediction using social media sentiment. The data is fetched from the Apewisdom API, Reddit, and other sources, and is used to analyze sentiment and potential market movements. 

## Phases

### Phase 1: Testing API (testing directory)

**Objective**: Build an API similar to Apewisdom that predicts stock trends based on social media sentiment, particularly from Reddit posts and comments. Develop a stock prediction tool that predicts stock trends based on social media sentiment, particularly from Reddit posts and comments. This involves using the Random Forest Regressor machine learning algorithm to analyze sentiment and other features extracted from social media data.

**Tools and Technologies**:
- Python
- PRAW (Python Reddit API Wrapper) for fetching Reddit data
- Requests library for making HTTP requests
- NLTK and VADER for sentiment analysis
- Scikit-learn for machine learning (Random Forest Regressor)
- Pandas for data manipulation
- Matplotlib and Seaborn for data visualization

### Phase 2: Apewisdom API Integration (apewisdom directory)

**Objective**: Use the Apewisdom API to gather trending stock tickers' mentions and store this data in MongoDB. Fetch real-time stock prices based on MongoDB stock ticker names and compare the real trending stock tickers on Reddit posts/comments through Apewisdom with the real-time prices to show their correlation. Integrate GPT-4 for a chatbot that provides information on these stock tickers.

**Tools and Technologies**:
- Python
- PRAW (Python Reddit API Wrapper)
- Requests library
- MongoDB (for data storage)
- Matplotlib and Seaborn (for data visualization)
- GPT-4 (for chatbot)
- Streamlit (for frontend)
- Docker and Google Cloud (for deployment and scheduling)

### Phase 3: Crypto Analysis (crypto directory)

**Objective**: Analyze the correlation between social media sentiment and cryptocurrency prices. Use embeddings (tokenized with BERT and GPT models) to analyze the sentiments of Reddit posts and comments about cryptocurrencies. Store these embeddings in a vector database (FAISS) for future implementation.

**Tools and Technologies**:
- Python
- Anaconda (Virtual Environment)
- PRAW (Python Reddit API Wrapper)
- Requests library
- Matplotlib and Seaborn (for data visualization)
- BERT and GPT models (for embedding and sentiment analysis)
- FAISS (for vector database storage)

**Subreddits Analyzed**:
- `bitcoin`
- `btc`
- `CryptoCurrency`
- `BitcoinBeginners`
- `binance`
- `coinbase`
- `CryptoMoonShots`
- `CryptoMarkets`
- `CryptoTechnology`

**Next Steps**:
- Continue training the model to better fit and provide more accurate sentiment scores focused on cryptocurrency discussions.
- Use embeddings and store this information in the FAISS vector database for future implementation.
- Use LLM (Large Language Models) to analyze the correlation between social media sentiment and real cryptocurrency prices in detail.

## Installation and Setup Instructions

### Prerequisites

- Python 3.6 or higher
- Conda (recommended for virtual environment management)
- MongoDB (for data storage)

### Clone the Repository

```sh
git clone https://github.com/yourusername/Stock_Trading_Reddit.git
cd Stock_Trading_Reddit


## Example Output

```plaintext
Trending Stocks on Reddit in the past 24 hours
Rank  Ticker   Name                           Mentions  24h Change (%) 
======================================================================
1     BB       BlackBerry                     1420      -8.00           
2     AMC      AMC Entertainment              1278      -46.00          
3     SPY      SPDR S&P 500 ETF Trust         617       51.00           
4     NVDA     NVIDIA                         298       121.00          
5     GME      GameStop                       228       -52.00          
6     TSLA     Tesla                          132       47.00           
7     SOFI     SoFi                           119       -40.00          
8     QQQ      Invesco QQQ ETF                88        72.00           
9     FFIE     Faraday Future                 82        204.00          
10    SNDL     Sundial Growers                79        -65.00          

Trending Cryptocurrencies on Reddit in the past 24 hours
Rank  Ticker   Name                           Mentions  24h Change (%) 
======================================================================
1     BTC      Bitcoin                        2200      10.00           
2     ETH      Ethereum                       1800      -5.00           
3     DOGE     Dogecoin                       1200      20.00          
4     ADA      Cardano                        1000      15.00           
5     XRP      Ripple                         800       12.00          

Most mentioned Stocks & Cryptos on 4Chan /biz in the last 24h (BETA)
Rank  Ticker   Name                           Mentions  24h Change (%) 
======================================================================
1     GME      GameStop                       500       12.00           
2     AMC      AMC Entertainment              450       -8.00           
3     TSLA     Tesla                          400       7.00            
4     BTC      Bitcoin                        350       15.00           
5     ETH      Ethereum                       300       -5.00           
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.

## Contact

If you have any questions or feedback, feel free to reach out at zhongjiayou1202@gmail.com.
