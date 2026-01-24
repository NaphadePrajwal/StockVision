import pandas as pd
import pandas_ta as ta

def add_technical_indicators(df):
    """
    REQ-3.4.2-1: Adds RSI, MACD, and Bollinger Bands.
    """
    # Create a copy to avoid SettingWithCopy warnings
    df = df.copy()
    
    # Ensure date is sorted
    df = df.sort_values(by="Date")
    
    # 1. RSI (Relative Strength Index)
    df['RSI'] = ta.rsi(df['Close'], length=14)
    
    # 2. MACD
    macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
    # MACD returns 3 columns. We merge them back.
    df = pd.concat([df, macd], axis=1)
    
    # 3. Bollinger Bands
    bbands = ta.bbands(df['Close'], length=20, std=2)
    
    # --- CRITICAL FIX: Rename columns to simple names ---
    # pandas_ta returns columns like BBL_20_2.0. We rename them to be safe.
    if bbands is not None:
        # The columns are usually in order: Lower, Mid, Upper, Bandwidth, Percent
        # We assume the default column order from pandas_ta
        bbands.columns = ['LowerBand', 'MidBand', 'UpperBand', 'Bandwidth', 'Percent']
        df = pd.concat([df, bbands], axis=1)
    
    # Cleanup: Drop NaN values (first 20 days will be empty due to moving averages)
    df.dropna(inplace=True)
    
    return df