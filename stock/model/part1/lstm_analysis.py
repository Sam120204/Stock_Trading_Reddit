import os
from dotenv import load_dotenv
import psycopg2
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt


def make_future_predictions(lstm_model, scaled_data, past_steps, future_days, fitted_scaler):
    """
    Function to recursively predict future stock prices using the LSTM model.

    Args:
        lstm_model: Trained LSTM model for stock price prediction.
        scaled_data: Scaled input data (numpy array) from which we start predicting future values.
        past_steps: Number of past days (steps) to use as input for each prediction.
        future_days: Number of future days to predict.
        fitted_scaler: Fitted MinMaxScaler for scaling and inverse scaling of data.

    Returns:
        future_predictions: Predicted stock prices for the next 'future_days'.
    """
    # Initialize with the last 'past_steps' data points
    recent_data = scaled_data[-past_steps:]

    # List to store the future predicted values
    future_predictions = []

    # Predict recursively for each future day
    for _ in range(future_days):
        # Reshape recent_data to match the LSTM input shape: (1 sample, past_steps, number of features)
        recent_data_reshaped = np.reshape(recent_data, (1, past_steps, scaled_data.shape[1]))

        # Use the model to predict the next day's closing price
        next_day_prediction = lstm_model.predict(recent_data_reshaped)

        # Create a new row to store the predicted value, padding other features with zeros
        next_day_full_features = np.zeros(
            (1, scaled_data.shape[1]))  # Initialize an empty row with the correct number of features
        next_day_full_features[0, -1] = next_day_prediction[
            0]  # Set the predicted 'Close' value (assumed to be the last feature)

        # Append the predicted closing price to the future_predictions list
        future_predictions.append(next_day_prediction[0])

        # Update the recent data by removing the oldest step and adding the predicted row
        recent_data = np.vstack([recent_data[1:], next_day_full_features])

    # Convert predictions back to the original scale using the scaler
    future_predictions = np.array(future_predictions)
    future_stock_prices = fitted_scaler.inverse_transform(
        np.column_stack([np.zeros((len(future_predictions), scaled_data.shape[1] - 1)), future_predictions])
    )[:, -1]  # Assumes 'Close' is the last feature

    return future_stock_prices


load_dotenv()

# Connect to your PostgreSQL database
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
    host=os.getenv("HOST"),
    port=os.getenv("DBPORT")
)

# SQL query to join the tables and filter by ticker 'NVDA'
query = """
SELECT date_trunc('day', rp.post_time) as date, rs.score as upvotes, rs.num_comments as comments,
       rs.sentiment_score as sentiment, rp.status
FROM reddit_raw_posts rp
LEFT JOIN reddit_post_scores rs ON rs.id = rp.id
WHERE rp.ticker = 'GME'
"""

df = pd.read_sql_query(query, conn)

# data = {
#     'date': ['2024-08-21', '2024-08-21', '2024-08-22', '2024-08-22'],
#     'upvotes': [150, 23, 25, 1537],
#     'comments': [149, 7, 55, 404],
#     'sentiment': [0.49, None, 0.10, 0.70],
#     'status': ['fetched', 'dropped', 'fetched', 'fetched']
# }
#
# df = pd.DataFrame(data)

df['weight'] = df.apply(lambda x: (x['upvotes'] + 2 * x['comments']) if x['status'] != 'dropped' else None, axis=1)

result = df[df['status'] != 'dropped'].groupby('date').apply(
    lambda x: (x['sentiment'] * x['weight']).sum() / x['weight'].sum() if x['weight'].sum() > 0 else None
).reset_index(name='weighted_average_sentiment')

result['total_upvotes'] = df.groupby('date')['upvotes'].sum().reset_index(drop=True)
result['total_comments'] = df.groupby('date')['comments'].sum().reset_index(drop=True)

# Create a complete date range
all_dates = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')
result.set_index('date', inplace=True)
result = result.reindex(all_dates)

# Fill NaNs for days without any posts
result['total_upvotes'].fillna(0, inplace=True)
result['total_comments'].fillna(0, inplace=True)
result['weighted_average_sentiment'].fillna(0, inplace=True)  # Adjust if another fill value is more appropriate

# Reset the index if you prefer having 'date' as a column
result.reset_index(inplace=True)
result.rename(columns={'index': 'date'}, inplace=True)

# Load the stock price data
stock_df = pd.read_csv('data/GME_long_term.csv', parse_dates=True, index_col='Date', usecols=['Date', 'Close'])

# Assume 'result' is already prepared as per previous steps and has a 'Date' column
reddit_df = result.rename(columns={'date': 'Date'})
reddit_df['Date'] = pd.to_datetime(reddit_df['Date'])

# Merge Reddit data with stock prices
merged_df = pd.merge(reddit_df, stock_df, on='Date', how='left')

# Forward fill missing stock prices
merged_df['Close'] = merged_df['Close'].fillna(method='ffill')

print(merged_df)

features = ['weighted_average_sentiment', 'total_upvotes', 'total_comments', 'Close']
data = merged_df[features]

for feature in features:
    for lag in [1, 3, 7]:
        data[f'{feature}_lag_{lag}'] = data[feature].shift(lag)

# Drop rows with NaN values that result from lagging
data.dropna(inplace=True)
print(data)
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)
print(data_scaled)


# Function to create sequences with multiple features
def create_sequences(data, n_steps_in, n_steps_out):
    X, y, X_predict = [], [], []
    for i in range(n_steps_in, len(data) - n_steps_out + 1):
        X.append(data[i - n_steps_in:i])
        y.append(data[i:i + n_steps_out, -1][::-1])  # Now includes the next 3 days

    for i in range(len(data) - n_steps_out + 1, len(data)):
        X_predict.append(data[i - n_steps_in:i])
    return np.array(X), np.array(y), np.array(X_predict)


n_steps_in, n_steps_out = 30, 7  # Predicting next day's closing price based on past 30 days
X, y, X_predict = create_sequences(data_scaled, n_steps_in, n_steps_out)
print(y)

# Train/test split
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Define LSTM model architecture
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(n_steps_in, X.shape[2])),
    Dropout(0.2),
    LSTM(50),
    Dropout(0.2),
    Dense(n_steps_out)  # Output 3 values for 3 days
])

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Fit model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

predicted_prices_scaled = model.predict(X_test)
# Inverse transform the predicted prices
predicted_prices = scaler.inverse_transform(np.column_stack([np.zeros((len(predicted_prices_scaled), data.shape[1] - 1)), predicted_prices_scaled[:, 0]]))[:, -1]

predicted_full_last = np.zeros((n_steps_out, data.shape[1]))  # Create an array for 3 days of predictions
predicted_full_last[:, -1] = predicted_prices_scaled[-1]  # Take all 3 predictions from the last test sample

# Inverse transform the 3 days of predictions for the last sequence
predicted_prices_last_3 = scaler.inverse_transform(predicted_full_last)[:, -1]
print(predicted_prices_last_3)

# Inverse transform the actual closing prices for comparison

actual_prices = scaler.inverse_transform(np.column_stack([np.zeros((len(y_test), data.shape[1] - 1)), y_test[:, 0]]))[:, -1]
print(actual_prices)

future_prediction_prices_scaled = model.predict(X_predict)
future_predict_full_last = np.zeros((n_steps_out, data.shape[1]))
future_predict_full_last[:, -1] = future_prediction_prices_scaled[-1]
future_step_out_predicted_prices = scaler.inverse_transform(future_predict_full_last)[:, -1]

future_prediction_prices = scaler.inverse_transform(np.column_stack([np.zeros((len(future_prediction_prices_scaled), data.shape[1] - 1)), future_prediction_prices_scaled[:, 0]]))[:, -1]
print(future_prediction_prices)
print(future_step_out_predicted_prices)

# Calculate RMSE
rmse = np.sqrt(mean_squared_error(actual_prices, predicted_prices))
print(f'Root Mean Squared Error: {rmse}')

last_date = pd.to_datetime(merged_df['Date'].iloc[-1]) - pd.Timedelta(days=n_steps_out) # Last date in the dataset
future_dates = pd.date_range(start=last_date, periods=n_steps_out, freq='D')[1:]  # Start from next day
future_prediction_dates = pd.date_range(start=future_dates[-1], periods=n_steps_out, freq='D')[1:]

# Plot training and validation loss
plt.figure(figsize=(10, 5))
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epoch')
plt.legend()
plt.show()

# Plot actual vs predicted prices
plt.figure(figsize=(14, 5))
actual_dates = merged_df['Date'].iloc[-len(actual_prices)-n_steps_out:]
dates = merged_df['Date'].iloc[-len(actual_prices)-n_steps_out:-n_steps_out]
plt.plot(actual_dates, merged_df['Close'].iloc[-len(actual_prices)-n_steps_out:], label='Actual Closing Prices', color='blue')
plt.plot(dates, predicted_prices, label='Predicted Closing Prices', color='orange')
print(future_dates)
print(predicted_prices[-1])
plt.plot(future_dates, future_prediction_prices, label='Predicted Closing Prices', color='orange')
plt.plot(future_prediction_dates, future_step_out_predicted_prices[1::], label='Future Predicted Closing Prices', color='orange', linestyle='--')

plt.title('Comparison of Actual and Predicted Closing Stock Prices')
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.legend()
plt.grid(True)
plt.show()




# fig, ax1 = plt.subplots(figsize=(14, 7))
#
# color = 'tab:red'
# ax1.set_xlabel('Date')
# ax1.set_ylabel('Close', color=color)
# data['Close_pct_growth'] = data['Close'].shift(0).pct_change() * 100
# ax1.plot(data.index, data['Close_pct_growth'], color=color)
# ax1.tick_params(axis='y', labelcolor=color)
#
# ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
# color = 'tab:blue'
# ax2.set_ylabel('Sentiment', color=color)  # we already handled the x-label with ax1
# ax2.plot(data.index, data['weighted_average_sentiment'], color=color)
# ax2.tick_params(axis='y', labelcolor=color)
#
# # ax3 = ax1.twinx()  # another axis for upvotes
# # ax3.spines['right'].set_position(('outward', 60))
# # color = 'tab:green'
# # ax3.set_ylabel('Upvotes', color=color)
# # ax3.plot(data.index, data['total_upvotes'], color=color)
# # ax3.tick_params(axis='y', labelcolor=color)
# #
# # ax4 = ax1.twinx()  # another axis for comments
# # ax4.spines['right'].set_position(('outward', 120))
# # color = 'tab:purple'
# # ax4.set_ylabel('Comments', color=color)
# # ax4.plot(data.index, data['total_comments'], color=color)
# # ax4.tick_params(axis='y', labelcolor=color)
#
# fig.tight_layout()  # to handle the overlap of axes
# plt.title('Feature Trends Over Time')
# plt.show()
#
#
# # Select the columns you need
# data = data[['weighted_average_sentiment', 'Close']]
#
# # Calculate the percentage growth of Close prices from two days ago
# data['Close_pct_growth_2d_ago'] = data['Close'].shift(-5).pct_change() * 100
#
# # Align this growth with today's sentiment
# data['Current_day_sentiment'] = data['weighted_average_sentiment']
#
# # Drop rows with NaN values that result from shifting and percentage change calculations
# data.dropna(inplace=True)
#
# # Scatter plot to show the relationship between 2-day-ago close price growth and current day's sentiment
# plt.figure(figsize=(10, 6))
# plt.scatter(data['Current_day_sentiment'], data['Close_pct_growth_2d_ago'], color='blue', alpha=0.5)
# plt.title('Relationship Between Close Price Growth 2 Days Ago and Current Day\'s Sentiment')
# plt.ylabel('Close Price Growth 2 Days Ago (%)')
# plt.xlabel('Current Day\'s Sentiment')
# plt.grid(True)
# plt.show()



