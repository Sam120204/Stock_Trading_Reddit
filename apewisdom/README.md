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
- Deploy Streamlit app on Google Cloud Run

## Prerequisites
- Python 3.9 or higher
- PRAW (Python Reddit API Wrapper)
- Requests library
- Plotly
- Pandas
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
pip install -r requirements.txt
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

### 7. Build and Deploy the Streamlit App to Google Cloud Run

#### 7.1 Build the Docker Image

```sh
docker build -t streamlit-app .
```

#### 7.2 Tag the Docker Image

```sh
docker tag streamlit-app us-central1-docker.pkg.dev/trendsage/gcf-artifacts/streamlit-app
```

#### 7.3 Push the Docker Image

```sh
docker push us-central1-docker.pkg.dev/trendsage/gcf-artifacts/streamlit-app
```

#### 7.4 Deploy to Google Cloud Run

```sh
gcloud run deploy streamlit-app --image us-central1-docker.pkg.dev/trendsage/gcf-artifacts/streamlit-app --platform managed --region us-central1 --allow-unauthenticated
```

### 8. Access the App

Once deployed, you can access the Streamlit app via the URL provided by Google Cloud Run.

### Example Output

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

## Files

- `app.py`: Main Streamlit app file
- `config.py`: Configuration file for Reddit API credentials
- `database.py`: MongoDB client for data storage
- `requirements.txt`: List of Python dependencies
- `Dockerfile`: Docker configuration for the app
- `reddit_client.py`: Reddit client setup
- `apewisdom_client.py`: Client to fetch data from Apewisdom API

## Running the App Locally

You can also run the Streamlit app locally by executing:

```sh
streamlit run app.py
```

This will start the app on `localhost:8501`.

## Verifying Data in MongoDB

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
```
