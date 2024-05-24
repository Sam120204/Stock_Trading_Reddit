import pandas as pd
from textblob import TextBlob

def preprocess_data(data):
    data = data.dropna()
    data['text'] = data['title'] + ' ' + data['selftext']
    data['text'] = data['text'].str.replace(r'\W', ' ')
    data['text'] = data['text'].str.lower()
    return data

def add_sentiment(data):
    data['sentiment'] = data['text'].apply(lambda x: TextBlob(x).sentiment.polarity)
    return data
