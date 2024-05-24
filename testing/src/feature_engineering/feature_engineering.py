# feature_engineering.py
import pandas as pd

def create_features(data):
    data['mentions'] = 1
    data['day'] = pd.to_datetime(data['created_utc']).dt.day
    data['month'] = pd.to_datetime(data['created_utc']).dt.month
    data['year'] = pd.to_datetime(data['created_utc']).dt.year
    
    # Ensure target column is created
    data['target_column'] = data['sentiment']
    
    return data
