from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

def train_model(data):
    features = ['mentions', 'day', 'month', 'year', 'day_of_week', 'hour_of_day', 'is_weekend']
    target = 'target_column'  # Replace with your actual target column
    
    # Check if features exist in the DataFrame
    for feature in features:
        if feature not in data.columns:
            raise KeyError(f"Feature '{feature}' not found in data columns.")
    
    X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)
    
    model = RandomForestClassifier()
    model.fit(X_train, y_train)
    
    return model
