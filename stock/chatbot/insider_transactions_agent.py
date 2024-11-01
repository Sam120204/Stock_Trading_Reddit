import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import finnhub
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# Load environment variables from .env file
load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

# Cache for storing results to minimize API calls
cache = {}


class InsiderTransactionsAgent:
    def __init__(self):
        self.base_url = 'https://finnhub.io/api/v1/stock/insider-transactions'

    def get_insider_transactions(self, symbol, max_entries=5, months=3):
        cache_key = f"{symbol}_insider_transactions"
        if cache_key in cache:
            cache_time, cached_data = cache[cache_key]
            if time.time() - cache_time < 86400:  # 24 hours
                return cached_data

        # Fetch insider transaction data from Finnhub
        params = {'symbol': symbol, 'token': FINNHUB_API_KEY}
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            transactions = []

            # Define the cutoff date for recent transactions
            cutoff_date = datetime.now() - timedelta(days=months * 30)

            for transaction in data.get('data', []):
                transaction_date = datetime.strptime(transaction['transactionDate'], "%Y-%m-%d")

                # Include only recent transactions
                if transaction_date >= cutoff_date:
                    transactions.append({
                        'name': transaction['name'],
                        'transaction_date': transaction['transactionDate'],
                        'transaction_code': transaction['transactionCode'],
                        'shares_changed': transaction['change'],
                        'transaction_price': transaction['transactionPrice'],
                        'remaining_shares': transaction['share'],
                        'filing_date': transaction['filingDate']
                    })

            # Limit the number of entries to max_entries
            transactions = transactions[:max_entries]
            cache[cache_key] = (time.time(), transactions)
            return transactions
        else:
            return {'error': f"Failed to fetch data: {response.status_code} {response.text}"}

    def get_insider_sentiment(self, symbol, start_date='2024-10-01', max_entries=5):
        cache_key = f"{symbol}_insider_sentiment"
        if cache_key in cache:
            cache_time, cached_data = cache[cache_key]
            if time.time() - cache_time < 86400:  # 24 hours
                return cached_data

        # Fetch insider sentiment data from Finnhub
        end_date = datetime.today().strftime('%Y-%m-%d')
        data = finnhub_client.stock_insider_sentiment(symbol, start_date, end_date)

        if 'data' in data and data['data']:
            sentiment_data = []
            for entry in data['data'][:max_entries]:  # Limit entries
                sentiment_data.append({
                    'year': entry['year'],
                    'month': entry['month'],
                    'change': entry['change'],
                    'mspr': entry['mspr'],
                    'date': f"{entry['year']}-{entry['month']:02d}"
                })
            cache[cache_key] = (time.time(), sentiment_data)
            return sentiment_data
        else:
            return {'error': 'No insider sentiment data available for this period.'}


def create_summary(symbol):
    agent = InsiderTransactionsAgent()

    # Fetch and limit data size for both insider transactions and sentiment
    insider_data = agent.get_insider_transactions(symbol, max_entries=5)
    sentiment_data = agent.get_insider_sentiment(symbol, max_entries=5)

    # Set up OpenAI Chat model for LangChain
    llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPENAI_API_KEY"))

    # Define prompt template for summarizing insider activity
    prompt_template = PromptTemplate.from_template(
        "Analyze the insider activity for {symbol} based on recent transactions and sentiment data:\n\n"
        "Insider Transactions:\n{insider_data}\n\n"
        "Insider Sentiment:\n{sentiment_data}\n\n"
        "Provide a summary."
    )

    # Define the LangChain chain with chat-based LLM
    chain = LLMChain(
        llm=llm,
        prompt=prompt_template
    )

    # Run the LangChain chain with the gathered data
    result = chain.run({
        "symbol": symbol,
        "insider_data": insider_data,
        "sentiment_data": sentiment_data
    })

    return result


if __name__ == "__main__":
    symbol = input("Enter the stock symbol (e.g., AAPL): ").strip().upper()
    summary = create_summary(symbol)
    print(summary)
