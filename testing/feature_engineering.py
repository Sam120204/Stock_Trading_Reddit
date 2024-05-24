def create_features(data):
    data['date'] = pd.to_datetime(data['created_utc'])
    data['day'] = data['date'].dt.day
    data['month'] = data['date'].dt.month
    data['year'] = data['date'].dt.year
    mention_counts = data.groupby(['ticker', 'date']).size().reset_index(name='mentions')
    data = pd.merge(data, mention_counts, on=['ticker', 'date'])
    return data
