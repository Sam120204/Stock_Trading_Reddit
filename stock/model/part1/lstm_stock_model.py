import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Load the stock data (5 years)
stock_data = pd.read_csv('data/AAPL_long_term.csv', parse_dates=True, index_col='Date')

# Feature selection: Stock features
stock_features = ['Close', 'Volume']
# reddit_features = ['Sentiment_Score', 'Mentions', 'Pct_Change_Mentions']  # Commented out

# Prepare stock data for initial training
scaler_stock = MinMaxScaler(feature_range=(0, 1))
scaled_stock_data = scaler_stock.fit_transform(stock_data[stock_features])

# Creating sequences for LSTM (for stock data)
def create_sequences(data, time_steps=30, future_steps=1):
    X, y = [], []
    for i in range(time_steps, len(data) - future_steps + 1):
        X.append(data[i-time_steps:i])
        y.append(data[i + future_steps - 1, 0])  # Predicting the closing price in 'future_steps' days
    return np.array(X), np.array(y)

# Hyperparameters
time_steps = 30
future_steps = 1  # Predicting the next day's closing price. Increase this value to predict further into the future.

X_stock, y_stock = create_sequences(scaled_stock_data, time_steps, future_steps)

# Splitting the stock data into training and testing sets
split_ratio = 0.8
train_size = int(len(X_stock) * split_ratio)
X_train_stock, X_test_stock = X_stock[:train_size], X_stock[train_size:]
y_train_stock, y_test_stock = y_stock[:train_size], y_stock[train_size:]

# Building the LSTM model for initial training
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train_stock.shape[1], X_train_stock.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(units=50))
model.add(Dropout(0.2))
model.add(Dense(units=future_steps))  # Output layer for predicting future prices

# Compiling the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Initial training on long-term stock data
history = model.fit(X_train_stock, y_train_stock, epochs=100, batch_size=32, validation_split=0.2)

# # Prepare the data for fine-tuning with recent Reddit data (Commented out)
# merged_data = stock_data[-len(reddit_data):].join(reddit_data, how='inner')

# # Combine stock and Reddit features for fine-tuning (Commented out)
# scaler_combined = MinMaxScaler(feature_range=(0, 1))
# scaled_combined_data = scaler_combined.fit_transform(merged_data[stock_features + reddit_features])

# # Creating sequences for LSTM (combined stock and Reddit data) (Commented out)
# X_combined, y_combined = create_sequences(scaled_combined_data, time_steps)

# # Fine-tune the model on the combined data (Commented out)
# model.fit(X_combined, y_combined, epochs=20, batch_size=16)

# Predicting on the test set from the stock data
predicted_prices = model.predict(X_test_stock)
predicted_prices = scaler_stock.inverse_transform(np.concatenate([predicted_prices, np.zeros((len(predicted_prices), 1))], axis=1))[:, 0]

# Inverse transform the test set for comparison
actual_prices = scaler_stock.inverse_transform(np.concatenate([y_test_stock.reshape(-1, 1), np.zeros((len(y_test_stock), 1))], axis=1))[:, 0]

# Evaluating the model
rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
print(f"Root Mean Squared Error: {rmse}")

# Plotting the training loss
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Plotting the actual vs. predicted prices
plt.figure(figsize=(14, 5))
plt.plot(actual_prices, color='blue', label='Actual Prices')
plt.plot(predicted_prices, color='red', label='Predicted Prices')
plt.title('Stock Price Prediction (Without Reddit Data)')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()
