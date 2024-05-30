Sure, here's a detailed `README.md` section covering the setup and operations we've done so far for your "TrendSage - Stock Prediction Reddit Tool":

---

# TrendSage - Stock Prediction Reddit Tool

## Overview
TrendSage aims to develop a correlation between stock predictions based on posts or comments on Reddit and the actual stock trends. The project fetches trending stocks, cryptocurrencies, and 4Chan /biz mentions data from the Apewisdom API and retrieves relevant Reddit posts and comments discussing these assets. This data is used to analyze sentiment and potential market movements.

## Features
- Fetch trending stocks from Apewisdom API
- Fetch trending cryptocurrencies from Apewisdom API
- Fetch most mentioned stocks & cryptos on 4Chan /biz from Apewisdom API
- Retrieve and display Reddit posts and comments related to trending stocks and cryptocurrencies within the last 15 days
- Calculate and display the 24-hour change in mentions of each stock and cryptocurrency
- Visualize the data using bar charts for mentions and 24-hour change percentage
- Implement a machine learning model to predict stock trends based on Reddit data
- Save data to MongoDB for persistent storage
- Automatically gather data every hour

## Prerequisites
- Python 3.6 or higher
- PRAW (Python Reddit API Wrapper)
- Requests library
- Matplotlib
- Seaborn
- Pandas
- Schedule
- MongoDB (for data storage)

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/Stock_Trading_Reddit.git
cd Stock_Trading_Reddit
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment:

```sh
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows PowerShell
```

### 3. Install the Required Libraries

Install the necessary Python packages:

```sh
pip install praw requests matplotlib seaborn pandas schedule pymongo
```

### 4. Set Up MongoDB

You can use either a local MongoDB instance or MongoDB Atlas (recommended for cloud setup).

#### Local MongoDB Setup

1. Ensure MongoDB is installed and running on your local machine.
2. Start MongoDB:

    ```sh
    mongod --dbpath <your_db_path>
    ```

#### MongoDB Atlas Setup

1. Sign up for MongoDB Atlas at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a new cluster.
3. Obtain the connection string for your cluster.

### 5. Configure Reddit API Credentials

Create a `config.py` file in the root directory with your Reddit API credentials:

```python
REDDIT_CLIENT_ID = 'your_client_id'
REDDIT_SECRET = 'your_client_secret'
REDDIT_USER_AGENT = 'your_user_agent'
REDDIT_USERNAME = 'your_reddit_username'
REDDIT_PASSWORD = 'your_reddit_password'
```

### 6. Update MongoDB Connection String

Update the `database.py` file with your MongoDB connection string (for MongoDB Atlas):

```python
from pymongo import MongoClient

class MongoDBClient:
    def __init__(self, db_name, collection_name, uri="your_mongodb_atlas_connection_string"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert_data(self, data):
        if isinstance(data, list):
            self.collection.insert_many(data)
        else:
            self.collection.insert_one(data)

    def find_data(self, query={}):
        return list(self.collection.find(query))
```

### 7. Running the Script

Run the main script to fetch and store trending stocks:

```sh
python main.py
```

### 8. Automate Data Gathering

To continuously gather data every hour, the script includes scheduling functionality using the `schedule` library. Ensure the script runs continuously:

```python
import schedule
import time

def gather_data():
    # Fetch and store trending stocks from Apewisdom
    pass  # (Your existing code for gathering data)

def main():
    schedule.every(1).hours.do(gather_data)
    gather_data()  # Run once immediately

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
```

Run the script to start the continuous data gathering process:

```sh
python main.py
```

### 9. Verifying Data in MongoDB

You can verify that the data is being stored correctly using MongoDB Compass or the MongoDB shell.

#### Using MongoDB Compass

1. Open MongoDB Compass.
2. Connect to your MongoDB server.
3. Navigate to the `stock_trends` database and check the `trending_stocks` collection.

#### Using MongoDB Shell

1. Open a new terminal or command prompt.
2. Start the MongoDB shell:

    ```sh
    mongo
    ```

3. Switch to the `stock_trends` database:

    ```sh
    use stock_trends
    ```

4. Query the `trending_stocks` collection:

    ```sh
    db.trending_stocks.find().pretty()
    ```

## Example Output

### Trending Stocks on Reddit in the past 24 hours

```
Rank  Ticker   Name                           Mentions  24h Change (%) 
======================================================================
1     NVDA     NVIDIA                         1258      -32.00           
2     SPY      SPDR S&P 500 ETF Trust         442       11.34           
3     CRM      Salesforce                     298       -8.33           
...
```

### Visualizations

The script generates bar charts for mentions and 24-hour change percentages for the trending stocks and cryptocurrencies.

