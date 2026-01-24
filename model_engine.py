import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class StockPredictor:
    def __init__(self, df, lookback=60):
        """
        df: Pandas DataFrame containing ['Close', 'RSI', 'MACD', etc.]
        """
        # --- FIX: Explicitly remove 'Date' column so AI doesn't crash ---
        clean_df = df.copy()
        if 'Date' in clean_df.columns:
            clean_df = clean_df.drop(columns=['Date'])
            
        # Select only numeric columns (Price, RSI, Sentiment, etc.)
        self.raw_df = clean_df.select_dtypes(include=['number'])
        
        self.lookback = lookback
        
        # Scaler for ALL features
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = None
        
        # Separate scaler just for 'Close' price (to reverse-engineer the prediction later)
        self.target_scaler = MinMaxScaler(feature_range=(0, 1))

    def prepare_data(self):
        # 1. Fit scaler on all data (Price, RSI, Sentiment...)
        scaled_data = self.scaler.fit_transform(self.raw_df)
        
        # Fit target scaler just on Close price
        # We assume 'Close' is one of the columns. We find its index.
        if 'Close' in self.raw_df.columns:
            close_idx = self.raw_df.columns.get_loc('Close')
            self.target_scaler.fit(self.raw_df[['Close']])
        else:
            # Fallback if 'Close' isn't found (should not happen)
            close_idx = 0
            self.target_scaler.fit(self.raw_df.iloc[:, [0]])
        
        X, y = [], []
        
        # 2. Create sequences
        for i in range(self.lookback, len(scaled_data)):
            X.append(scaled_data[i-self.lookback:i]) # Past 60 days of ALL features
            y.append(scaled_data[i, close_idx])       # Next day's Close price
            
        X, y = np.array(X), np.array(y)
        return X, y, scaled_data

    def build_model(self, input_shape):
        model = Sequential()
        model.add(LSTM(units=50, return_sequences=True, input_shape=input_shape))
        model.add(Dropout(0.2))
        model.add(LSTM(units=50, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(units=1))
        
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model
        return model

    def train(self, epochs=25, batch_size=32):
        X, y, _ = self.prepare_data()
        self.build_model(input_shape=(X.shape[1], X.shape[2]))
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        return self.model

    def predict_future(self, days=30):
        X, _, scaled_data = self.prepare_data()
        
        # Start with the last known sequence
        current_batch = scaled_data[-self.lookback:].reshape(1, self.lookback, scaled_data.shape[1])
        
        future_predictions = []
        close_idx = self.raw_df.columns.get_loc('Close')
        
        for i in range(days):
            # Predict next price
            next_pred_scaled = self.model.predict(current_batch, verbose=0)[0, 0]
            
            # Store prediction (inverse scaled to get real $$)
            pred_inverse = self.target_scaler.inverse_transform([[next_pred_scaled]])[0, 0]
            future_predictions.append(pred_inverse)
            
            # Update batch for next step
            new_row = current_batch[0, -1, :].copy()
            new_row[close_idx] = next_pred_scaled
            
            new_row = new_row.reshape(1, 1, -1)
            current_batch = np.append(current_batch[:, 1:, :], new_row, axis=1)
            
        return future_predictions