import re
import spacy
# from data_collection import get_reddit_data

# Load the spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")

# Example lists of keywords for expanded keyword matching
financial_keywords = ["stock", "shares", "market", "investment", "price", "trading", "bullish", "bearish", "IPO", "earnings", "dividends"]

def extract_tickers(text):
    """
    Extract potential stock tickers from text using regex patterns.

    Args:
        text (str): The text to extract tickers from.

    Returns:
        list: A list of potential stock tickers found in the text.
    """
    # Regex pattern to capture stock tickers (e.g., $AAPL, AAPL)
    ticker_pattern = re.compile(r'\b[A-Z]{1,5}\b')
    tickers = ticker_pattern.findall(text)
    return tickers

def dynamic_ticker_filter(post):
    """
    Filter posts dynamically based on the presence of stock tickers.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        bool: True if the post contains potential stock tickers, False otherwise.
    """
    tickers_in_title = extract_tickers(post['title'])
    tickers_in_body = extract_tickers(post['body'])
    # Combine tickers found in title and body
    all_tickers = set(tickers_in_title + tickers_in_body)
    # Check against a more comprehensive, up-to-date list of tickers or validate them
    return bool(all_tickers)

def ner_filter(post):
    """
    Filter posts based on Named Entity Recognition (NER) to identify relevant entities.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        bool: True if the post contains relevant entities, False otherwise.
    """
    # Combine title and body for NER analysis
    text = post['title'] + " " + post['body']
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in {"ORG", "GPE", "PRODUCT"}:  # ORG for organizations, GPE for geopolitical entities, PRODUCT for potential ticker names
            return True
    return False

def context_check(post):
    """
    Analyze the context of mentions to ensure they are relevant to financial discussions.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        bool: True if the context indicates a financial discussion, False otherwise.
    """
    combined_text = post['title'] + " " + post['body']
    for keyword in financial_keywords:
        if keyword in combined_text:
            return True
    return False

def keyword_filter(post):
    """
    Filter posts based on an expanded list of financial keywords.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        bool: True if the post contains relevant financial keywords, False otherwise.
    """
    combined_text = post['title'] + " " + post['body']
    for keyword in financial_keywords:
        if keyword in combined_text:
            return True
    return False

def is_relevant_post(post):
    """
    Determine if a Reddit post is relevant based on multiple filtering methods.

    Args:
        post (dict): A dictionary representing a Reddit post.

    Returns:
        bool: True if the post is relevant, False otherwise.
    """
    # Apply dynamic ticker extraction
    if dynamic_ticker_filter(post):
        return True
    # Apply enhanced NER filtering
    if ner_filter(post):
        return True
    # Apply contextual analysis
    if context_check(post):
        return True
    # Apply expanded keyword matching
    if keyword_filter(post):
        return True
    return False

# Debug below
# if __name__ == "__main__":
    # # Fetch Reddit data using the get_reddit_data function
    # reddit_data = get_reddit_data()
    
    # # Filter relevant posts using the is_relevant_post function
    # relevant_posts = [post for post in reddit_data if is_relevant_post(post)]
    
    # # Print the URL and title of each relevant post
    # for post in relevant_posts:
    #     print(f"URL: {post['url']}, Title: {post['title']}")