from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import joblib

def train_model(data):
    features = ['mentions', 'day', 'month', 'year', 'sentiment']
    target = 'target_column'  # Replace with the actual target column name

    # Check if the target column exists in the data
    if target not in data.columns:
        raise KeyError(f"Target column '{target}' not found in data columns.")
    
    # Check if all features exist in the data
    for feature in features:
        if feature not in data.columns:
            raise KeyError(f"Feature '{feature}' not found in data columns.")
    
    X = data[features]
    y = data[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Use RandomForestRegressor instead of LinearRegression
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    return model, X_test, y_test

def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    return mse

def save_model(model, model_path):
    joblib.dump(model, model_path)

def load_model(model_path):
    return joblib.load(model_path)
