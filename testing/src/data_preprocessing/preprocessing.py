# preprocessing.py
import pandas as pd
from textblob import TextBlob

def preprocess_data(data):
    data['text'] = data['title'] + ' ' + data.get('selftext', '')
    return data

def add_sentiment(data):
    data['sentiment'] = data['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
    return data
