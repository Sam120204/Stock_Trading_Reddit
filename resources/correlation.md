To model the relationship between real-time crypto prices and sentiment results from social media posts/comments, you can use a machine learning model that can handle time series data and multiple input features. One of the best approaches for this kind of task is to use a Recurrent Neural Network (RNN), specifically Long Short-Term Memory (LSTM) networks, or Transformer-based models designed for time series prediction.

### Recommended Approach

1. **Data Preparation**:
   - **Sentiment Scores**: Aggregate sentiment scores from social media posts/comments at regular intervals (e.g., hourly, daily).
   - **Crypto Prices**: Collect corresponding crypto prices at the same intervals.

2. **Feature Engineering**:
   - **Time Alignment**: Ensure that sentiment scores and crypto prices are aligned based on time.
   - **Normalization**: Normalize the features to ensure they are on a similar scale.

3. **Model Selection**:
   - Use an LSTM model or a Transformer model for time series prediction. These models are well-suited for capturing temporal dependencies and patterns in sequential data.

4. **Training the Model**:
   - Train the model using historical data of sentiment scores and crypto prices.

5. **Prediction and Correlation Analysis**:
   - Use the trained model to predict crypto prices based on new sentiment scores and compare the predicted prices with actual prices to analyze the correlation.

### Detailed Steps

#### Step 1: Data Preparation

```python
import pandas as pd

# Example sentiment data (aggregated hourly sentiment scores)
# Assume sentiment_scores is a DataFrame with columns ['timestamp', 'sentiment_score']
sentiment_scores = pd.DataFrame({
    'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
    'sentiment_score': np.random.rand(100)
})

# Example crypto price data (hourly prices)
# Assume crypto_prices is a DataFrame with columns ['timestamp', 'price']
crypto_prices = pd.DataFrame({
    'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
    'price': np.random.rand(100) * 10000
})

# Merge the data on timestamp
data = pd.merge(sentiment_scores, crypto_prices, on='timestamp')
```

#### Step 2: Feature Engineering

```python
from sklearn.preprocessing import MinMaxScaler

# Normalize the features
scaler = MinMaxScaler()
data[['sentiment_score', 'price']] = scaler.fit_transform(data[['sentiment_score', 'price']])

# Prepare input sequences for the model
def create_sequences(data, seq_length):
    xs, ys = [], []
    for i in range(len(data) - seq_length):
        x = data.iloc[i:(i + seq_length)][['sentiment_score', 'price']].values
        y = data.iloc[i + seq_length]['price']
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)

seq_length = 10  # Number of time steps to include in each input sequence
X, y = create_sequences(data, seq_length)
```

#### Step 3: Model Selection (LSTM)

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# Define the LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

# Hyperparameters
input_size = 2  # Number of input features (sentiment_score and price)
hidden_size = 64
num_layers = 2
output_size = 1

# Create the model
model = LSTMModel(input_size, hidden_size, num_layers, output_size)
```

#### Step 4: Training the Model

```python
# Prepare the dataset and dataloader
batch_size = 32
train_dataset = TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32))
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

# Loss and optimizer
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training loop
num_epochs = 20
for epoch in range(num_epochs):
    for inputs, targets in train_loader:
        # Forward pass
        outputs = model(inputs)
        loss = criterion(outputs, targets.unsqueeze(1))
        
        # Backward pass and optimization
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')
```

#### Step 5: Prediction and Correlation Analysis

```python
# Example prediction
model.eval()
with torch.no_grad():
    inputs = torch.tensor(X, dtype=torch.float32)
    predicted_prices = model(inputs).numpy()

# Inverse transform the predicted prices to get them back to the original scale
predicted_prices = scaler.inverse_transform(predicted_prices)

# Compare with actual prices
actual_prices = scaler.inverse_transform(y.reshape(-1, 1))

# Correlation analysis
from scipy.stats import pearsonr

correlation, _ = pearsonr(predicted_prices.flatten(), actual_prices.flatten())
print(f"Correlation between predicted and actual prices: {correlation}")

# Visualization
import matplotlib.pyplot as plt

plt.plot(actual_prices, label='Actual Prices')
plt.plot(predicted_prices, label='Predicted Prices')
plt.legend()
plt.show()
```

### Conclusion

- **Data Preparation**: Collect and align sentiment scores and crypto prices.
- **Feature Engineering**: Normalize the data and create input sequences for the model.
- **Model Selection**: Use an LSTM model for capturing temporal dependencies.
- **Training**: Train the model using historical data.
- **Prediction and Correlation Analysis**: Use the trained model to predict prices and analyze the correlation between predicted and actual prices.

This approach leverages the strengths of LSTM models in handling sequential data and provides a robust framework for analyzing the impact of social media sentiment on crypto prices.