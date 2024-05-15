# Stock_Trading_Reddit

## Overview

This project aims to develop a correlation between stock predictions based on the posts or comments on Reddit and the actual stock trends. The project fetches trending stocks data from the Apewisdom API and retrieves relevant Reddit posts and comments discussing these stocks. This data is used to analyze sentiment and potential market movements.

## Features

- Fetch trending stocks from Apewisdom API
- Retrieve and display Reddit posts and comments related to trending stocks
- Calculate and display the 24-hour change in mentions of each stock
- Analyze sentiment from Reddit discussions

## Prerequisites

- Python 3.6 or higher
- PRAW (Python Reddit API Wrapper)
- Requests library

## Setup

1. **Clone the repository**
    ```sh
    git clone https://github.com/Sam120204/Stock_Trading_Reddit.git
    cd Stock_Trading_Reddit
    ```

2. **Install the required libraries**
    ```sh
    pip install praw requests
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

## Usage

1. **Fetch trending stocks and display data**
    ```sh
    python main.py
    ```

2. **Fetch posts and comments related to trending stocks**
    The `main.py` script fetches and displays trending stocks. It also retrieves and prints relevant Reddit posts and comments discussing these stocks.

## Project Structure

- `config.py`: Contains Apewisdom API credentials.
- `main.py`: Main script to fetch and display trending stocks and Reddit discussions.
- `reddit_client.py`: Handles Reddit API connection and data retrieval.
- `apewisdom_client.py`: Fetches trending stocks data from Apewisdom API.
- `README.md`: Project documentation.

## Example Output

```plaintext
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
