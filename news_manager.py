import requests
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from sentiment_engine import predict_finbert_sentiment # Import our new brain

def fetch_finnhub_news(ticker, api_key):
    """
    Fetches company-specific news from Finnhub (Stocks/ETFs).
    """
    # Get dates: Today and 7 days ago
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Finnhub Company News Endpoint
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start_date}&to={today}&token={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Finnhub returns a list directly. If empty, return empty list.
        if not data:
            return []
            
        # Limit to top 10 most recent articles to save processing time
        return data[:10]
        
    except Exception as e:
        print(f"Finnhub API Error: {e}")
        return []

def process_news_with_finbert(articles):
    """
    Takes raw Finnhub articles, runs FinBERT, and returns a DataFrame.
    """
    if not articles:
        return pd.DataFrame()
    
    news_data = []
    headlines = []
    
    # 1. Prepare data
    for article in articles:
        headline = article.get('headline', '')
        summary = article.get('summary', '')
        full_text = f"{headline}. {summary}"
        headlines.append(full_text)
        
        pub_date = datetime.fromtimestamp(article['datetime']).strftime('%Y-%m-%d')
        
        news_data.append({
            'title': headline,
            # --- NEW: Get the Image URL ---
            'image': article.get('image', ''), 
            # ------------------------------
            'source': article.get('source', 'Finnhub'),
            'url': article.get('url', '#'),
            'published': pub_date,
            'full_text': full_text
        })
        
    # 2. Run FinBERT (Batch Processing)
    if headlines:
        # Get probabilities tensor
        probs = predict_finbert_sentiment(headlines)
        # FinBERT classes are: [positive, negative, neutral] usually at indices 0, 1, 2
        # But ProsusAI/finbert output order is: [0: Positive, 1: Negative, 2: Neutral]
        
        # Let's map them to a single score (-1 to 1) for our chart
        # Score = Prob(Pos) - Prob(Neg). Neutral doesn't pull the score.
        sentiments = []
        labels = []
        
        for i in range(len(probs)):
            p_pos = probs[i][0].item()
            p_neg = probs[i][1].item()
            p_neu = probs[i][2].item()
            
            # Create a composite score
            score = p_pos - p_neg
            
            # Assign Label
            if score > 0.05:
                label = "Positive"
            elif score < -0.05:
                label = "Negative"
            else:
                label = "Neutral"
                
            sentiments.append(score)
            labels.append(label)
            
        # Add to dataframe
        df = pd.DataFrame(news_data)
        df['sentiment_score'] = sentiments
        df['label'] = labels
        
        return df
    
    return pd.DataFrame()