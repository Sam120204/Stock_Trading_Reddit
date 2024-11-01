from insider_transactions_agent import InsiderTransactionsAgent
from market_news_agent import MarketNewsAgent
from technical_indicators_agent import TechnicalIndicatorsAgent
from time_series_agent import TimeSeriesAgent

# Initialize agents
insider_agent = InsiderTransactionsAgent()
news_agent = MarketNewsAgent()
tech_indicator_agent = TechnicalIndicatorsAgent()
time_series_agent = TimeSeriesAgent()

# Test each agent with a sample symbol
symbol = "AAPL"

# Fetch insider transactions
insider_data = insider_agent.get_insider_transactions(symbol)
print("Insider Transactions:", insider_data)

# Fetch market news
news_data = news_agent.get_market_news(symbol)
print("Market News:", news_data)

# Fetch technical indicator (Simple Moving Average)
tech_indicator_data = tech_indicator_agent.get_technical_indicator(symbol)
print("Technical Indicator (SMA):", tech_indicator_data)

# Fetch time series data
time_series_data = time_series_agent.get_time_series(symbol)
print("Time Series Data:", time_series_data)
