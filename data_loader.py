# data_loader.py
import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker, period="5y"):
    """
    Fetches historical stock data for a given ticker.
    
    Args:
        ticker (str): The stock symbol (e.g., 'AAPL').
        period (str): The duration of data to fetch (default '5y' per REQ-3.4.1-1).
        
    Returns:
        pd.DataFrame: A dataframe containing Open, High, Low, Close, Volume.
    """
    try:
        # Using yfinance to download data
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if df.empty:
            return None
        
        # Reset index to make Date a column for easier plotting later
        df.reset_index(inplace=True)
        
        # Standardize timezone to remove potential issues with plotting
        df['Date'] = df['Date'].dt.date
        
        return df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def get_company_info(ticker):
    """
    Fetches basic company metadata (Sector, Description).
    """
    try:
        stock = yf.Ticker(ticker)
        return stock.info
    except:
        return None