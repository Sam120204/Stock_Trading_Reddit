from flask import Flask, request, jsonify
from src.data_preprocessing.preprocessing import preprocess_data, add_sentiment
from src.feature_engineering.feature_engineering import create_features
from src.model_training.training import load_model
import pandas as pd

app = Flask(__name__)

# Load the trained model
model = load_model('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    df = pd.DataFrame([data])
    
    # Preprocess and feature engineering steps
    df = preprocess_data(df)
    df = add_sentiment(df)
    features = create_features(df)
    
    # Ensure the order of features matches the training
    feature_columns = ['mentions', 'day', 'month', 'year', 'sentiment']
    features = features[feature_columns]
    
    # Make prediction
    prediction = model.predict(features)
    return jsonify({'prediction': prediction[0]})

if __name__ == '__main__':
    app.run(debug=True)
