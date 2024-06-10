# random_forest_model.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from combined_data_preparation import combine_data

def train_random_forest():
    data = combine_data()
    # Convert sentiment to numerical values
    data['sentiment_score'] = data['sentiment'].apply(lambda x: 1 if x.lower() == 'positive' else -1 if x.lower() == 'negative' else 0)
    
    # Prepare features and target
    features = ['price', 'volume', 'open', 'high', 'low', 'close', 'sentiment_score']
    # Assuming you want to predict the next day's closing price
    # Ensure you have a target column in your data
    y = data['target']  # Adjust based on your actual target column

    # Ensure you handle any missing values
    data = data.dropna(subset=features + ['target'])
    X = data[features]
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')

    return model

# Example usage
if __name__ == "__main__":
    model = train_random_forest()
