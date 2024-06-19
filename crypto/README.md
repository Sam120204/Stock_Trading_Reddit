# Crypto Sentiment Analysis

This project analyzes the sentiment of Reddit posts related to cryptocurrencies. It collects data from specific subreddits, processes the text to generate embeddings, analyzes the sentiment, and stores the results in a FAISS vector database for further analysis.

## Project Structure

- `data_collection.py`: Collects Reddit posts and comments from specified subreddits.
- `embedding.py`: Generates embeddings for the collected text data using BERT.
- `sentiment_analysis.py`: Analyzes the sentiment of the collected text using VADER.
- `vector_store.py`: Stores the generated embeddings in a FAISS vector store and retrieves similar embeddings.
- `main.py`: Integrates all components and runs the entire pipeline from data collection to sentiment analysis and storage.

## Setup Instructions

### Prerequisites

- Python 3.7+
- Reddit API credentials

### Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/crypto-sentiment-analysis.git
    cd crypto-sentiment-analysis
    ```

2. **Set up a Conda environment**:

    ```sh
    conda create --name crypto_analysis_env python=3.8
    conda activate crypto_analysis_env
    ```

3. **Install the required Python packages**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up your Reddit API credentials**:

    Create a `secrets.toml` file in the root directory of the project with the following content:

    ```toml
    [reddit]
    client_id = "YOUR_CLIENT_ID"
    client_secret = "YOUR_CLIENT_SECRET"
    user_agent = "YOUR_USER_AGENT"
    username = "YOUR_REDDIT_USERNAME"
    password = "YOUR_REDDIT_PASSWORD"
    ```

## Usage

### Running the Full Pipeline

To run the entire pipeline, execute the `main.py` script:

```sh
python main.py
