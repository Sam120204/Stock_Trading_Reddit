import re
import pandas as pd
import spacy
import os
# Load the spaCy model for Named Entity Recognition (NER)
model_path = os.path.join(os.path.dirname(__file__), "en_core_web_sm/en_core_web_sm-3.7.1")
nlp = spacy.load(model_path)

def load_company_ticker_map(file_path='./ticker_company_names.csv'):
    company_ticker_map = {}
    nasdaq_data = pd.read_csv(file_path)
    suffixes = ["Inc.", "Corporation", "Corp.", "Ltd.", "Limited", "LLC", "LP", "PLC", "Group", "Holdings", "Holding", "Class A", "Class B", "Class C"]
    for index, row in nasdaq_data.iterrows():
        company_name = row['Name']
        for suffix in suffixes:
            company_name = company_name.replace(suffix, "").strip()  # Remove suffixes
        company_ticker_map[company_name] = row['Symbol']
    return company_ticker_map

# Load the map once at the beginning
COMPANY_TICKER_MAP = load_company_ticker_map()

# Example lists of keywords for expanded keyword matching
financial_keywords = ["stock", "shares", "market", "investment", "price", "trading", "bullish", "bearish", "IPO", "earnings", "dividends"]

# List of terms to ignore as potential tickers
IGNORE_TERMS = [
    "YOLO", "LOL", "FOMO", "TBA", "CEO", "CFO", "PR", "ER", "TA", "ETF", "BTFD", 
    "DD", "ATH", "BULL", "BEAR", "HODL", "PUMP", "DUMP", "STOCKS", "OPTIONS", "TRADING", 
    "MOON", "DIAMOND", "HANDS", "GAINZ", "LOSS", "LOSS", "PROFIT", "CALL", "PUT", "SPAC",
    "WSB", "RED", "GREEN", "BUY", "SELL", "MARGIN", "SHORT", "LONG", "OPTIONS", 
    "ROCKET", "STONK", "STOCK", "TRADE", "FINANCE", "INVEST", "CRYPTO"
]

def extract_tickers(text):
    """
    Extract potential stock tickers and company names from text.

    Args:
        text (str): The text to extract tickers from.

    Returns:
        list: A list of potential stock tickers found in the text.
    """
    # Regex pattern to capture stock tickers (e.g., AAPL, MSFT), avoiding single letters and common words
    ticker_pattern = re.compile(r'\b[A-Z]{2,5}\b')
    tickers = set(ticker_pattern.findall(text))

    # Check for formal company names and add their tickers
    for company, ticker in COMPANY_TICKER_MAP.items():
        if re.search(r'\b' + re.escape(company.lower()) + r'\b', text.lower()):  # Case-insensitive matching
            tickers.add(ticker)

    # Remove ignored terms
    tickers = [ticker for ticker in tickers if ticker not in IGNORE_TERMS]

    return list(tickers)

def ner_filter(text):
    """
    Filter posts based on Named Entity Recognition (NER) to identify relevant entities.

    Args:
        text (str): The text to analyze.

    Returns:
        list: A list of relevant entities found in the text.
    """
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        if ent.label_ in {"ORG", "GPE", "PRODUCT"}:  # ORG for organizations, GPE for geopolitical entities, PRODUCT for potential ticker names
            entities.append(ent.text)
    return entities

def context_check(text):
    """
    Analyze the context of mentions to ensure they are relevant to financial discussions.

    Args:
        text (str): The text to analyze.

    Returns:
        bool: True if the context indicates a financial discussion, False otherwise.
    """
    for keyword in financial_keywords:
        if keyword in text.lower():
            return True
    return False

def extract_and_filter_tickers(post):
    """
    Extract and filter tickers from a Reddit post.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        list: A list of valid stock tickers found in the post.
    """
    combined_text = post['title'] + " " + post['body']
    tickers = extract_tickers(combined_text)
    ner_entities = ner_filter(combined_text)
    if context_check(combined_text):
        tickers.extend(extract_tickers(" ".join(ner_entities)))
    return list(set(tickers))  # Combine and deduplicate tickers

# # Print the company ticker map to verify
# print(COMPANY_TICKER_MAP)
