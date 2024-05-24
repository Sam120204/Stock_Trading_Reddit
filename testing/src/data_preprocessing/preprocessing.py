# preprocessing.py

import pandas as pd

def preprocess_data(data):
    data['selftext'] = data.get('selftext', '')  # Ensure selftext column exists
    data['text'] = data['title'] + ' ' + data['selftext']
    return data
