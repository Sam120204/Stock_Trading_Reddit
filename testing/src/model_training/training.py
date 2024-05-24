from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

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
    
    X_train, X_test, y_train, y_test = train_test_split(data[features], data[target], test_size=0.2, random_state=42)
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    return model
