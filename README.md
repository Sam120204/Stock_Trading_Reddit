# TrendSage - Stock Prediction Reddit Tool

## Overview

TrendSage aims to develop a correlation between stock predictions based on the posts or comments on Reddit and the actual stock trends. The project fetches trending stocks, cryptocurrencies, and 4Chan /biz mentions data from the Apewisdom API and retrieves relevant Reddit posts and comments discussing these assets. This data is used to analyze sentiment and potential market movements.

## Features

- Fetch trending stocks from Apewisdom API
- Fetch trending cryptocurrencies from Apewisdom API
- Fetch most mentioned stocks & cryptos on 4Chan /biz from Apewisdom API
- Retrieve and display Reddit posts and comments related to trending stocks and cryptocurrencies within the last 15 days
- Calculate and display the 24-hour change in mentions of each stock and cryptocurrency
- Visualize the data using bar charts for mentions and 24-hour change percentage
- Implement a machine learning model to predict stock trends based on Reddit data
- Save data to MongoDB for persistent storage

## Prerequisites

- Python 3.6 or higher
- PRAW (Python Reddit API Wrapper)
- Requests library
- Matplotlib
- Seaborn
- Pandas
- Scikit-learn
- TextBlob (for sentiment analysis)
- MongoDB (for data storage)

## Setup

1. **Clone the repository**
    ```sh
    git clone https://github.com/yourusername/Stock_Trading_Reddit.git
    cd Stock_Trading_Reddit
    ```

2. **Install the required libraries**
    ```sh
    pip install praw requests matplotlib seaborn
    ```

3. **Set up Reddit API credentials**
    Create a `config.py` file in the root directory with the following content:
    ```python
    REDDIT_CLIENT_ID = 'your_client_id'
    REDDIT_SECRET = 'your_client_secret'
    REDDIT_USER_AGENT = 'your_user_agent'
    REDDIT_USERNAME = 'your_reddit_username'
    REDDIT_PASSWORD = 'your_reddit_password'
    ```
4. **Set up MongoDB**
   Make sure MongoDB is installed and running. You can start MongoDB with:
    ```sh
    mongod --dbpath <your_db_path>
    ```

## Usage

1. **Fetch trending stocks, cryptocurrencies, and 4Chan data and display results**
    ```sh
    python main.py
    ```

2. **Fetch posts and comments related to trending stocks and cryptocurrencies**
    The `main.py` script fetches and displays trending stocks, cryptocurrencies, and 4Chan mentions. It also retrieves and prints relevant Reddit posts and comments discussing these assets within the last 15 days.

3. **Visualize the data**
    The script will generate bar charts for mentions and 24-hour change percentage for trending stocks, cryptocurrencies, and 4Chan mentions.

## Project Structure

### `apewisdom` Directory

Contains the existing project that predicts the stock profit using Apewisdom API and Reddit Post API.

- `config.py`: Contains Reddit API credentials.
- `main.py`: Main script to fetch and display trending stocks, cryptocurrencies, 4Chan mentions, and Reddit discussions.
- `reddit_client.py`: Handles Reddit API connection and data retrieval.
- `apewisdom_client.py`: Fetches trending stocks, cryptocurrencies, and 4Chan data from Apewisdom API.
- `README.md`: Project documentation.

### `testing` Directory

Contains the currently developing API that works similar to Apewisdom API.

- `config.py`: Contains Reddit API credentials.
- `main.py`: Main script to fetch and display trending stocks, cryptocurrencies, 4Chan mentions, Reddit discussions, and to train the machine learning model.
- `src/data_collection/reddit_client.py`: Handles Reddit API connection and data retrieval.
- `src/data_collection/apewisdom_client.py`: Fetches trending stocks, cryptocurrencies, and 4Chan data from Apewisdom API.
- `src/data_preprocessing/preprocessing.py`: Contains functions for data preprocessing and sentiment analysis.
- `src/feature_engineering/feature_engineering.py`: Contains functions for feature engineering.
- `src/model_training/training.py`: Contains functions for training and evaluating the machine learning model.
- `src/database/database.py`: Contains functions for saving data to MongoDB.
- `requirements.txt`: Lists all the required libraries.
- `README.md`: Project documentation.

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

## Future Plans
I am also currently working on developing a web or mobile application to make this tool more accessible and user-friendly. Stay tuned for updates!

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## Contact
If you have any questions or feedback, feel free to reach out at zhongjiayou1202@gmail.com.