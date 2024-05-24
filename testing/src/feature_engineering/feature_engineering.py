import pandas as pd

def create_features(data):
    # Ensure the date field is converted to datetime
    data['date'] = pd.to_datetime(data['created_utc'])
    
    # Extract day, month, year from the date
    data['day'] = data['date'].dt.day
    data['month'] = data['date'].dt.month
    data['year'] = data['date'].dt.year
    
    # Other features
    data['day_of_week'] = data['date'].dt.dayofweek
    data['hour_of_day'] = data['date'].dt.hour
    data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
    
    return data
