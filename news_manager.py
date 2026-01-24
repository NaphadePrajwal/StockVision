import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import streamlit as st
from datetime import datetime, timedelta

def fetch_stock_news(ticker, api_key, limit=5):
    """
    Fetches news metadata from NewsAPI.
    """
    # Get date for the last 7 days to ensure relevance
    from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    # URL for NewsAPI
    url = f"https://newsapi.org/v2/everything?q={ticker}&from={from_date}&sortBy=publishedAt&language=en&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("status") != "ok":
            st.error(f"Error fetching news: {data.get('message')}")
            return []
        
        # Return only the list of articles
        return data.get("articles", [])[:limit]
        
    except Exception as e:
        print(f"API Request Error: {e}")
        return []

def filter_fake_news(articles):
    """
    REQ-3.4.3-1: Fake News Detection Module (Layer 1).
    Currently uses Source Credibility Verification (Whitelist approach).
    """
    # A list of generally credible financial news domains
    TRUSTED_SOURCES = [
        "bloomberg.com", "reuters.com", "cnbc.com", "finance.yahoo.com", 
        "wsj.com", "marketwatch.com", "forbes.com", "businessinsider.com",
        "ft.com", "investopedia.com", "benzinga.com", "techcrunch.com"
    ]
    
    verified_articles = []
    
    for article in articles:
        # Check if the article has a valid source name and URL
        if not article.get('source') or not article.get('url'):
            continue

        source_name = article['source'].get('name', '').lower()
        url = article['url'].lower()
        
        # Simple heuristic: Check if source is in our trusted list
        # OR if we are desperate, we accept it (for now, we are strict)
        is_trusted = any(trusted in url for trusted in TRUSTED_SOURCES)
        
        # For this prototype, if we find NO trusted news, we might show everything 
        # but mark it. For now, let's append valid ones.
        if is_trusted:
            verified_articles.append(article)
            
    # If the filter is too strict and returns nothing, return raw articles 
    # but normally we would warn the user.
    return verified_articles if verified_articles else articles

def analyze_sentiment(articles):
    """
    REQ-3.4.3-2: Applies VADER Sentiment Analysis.
    """
    analyzer = SentimentIntensityAnalyzer()
    sentiment_data = []

    for article in articles:
        title = article.get('title', '')
        description = article.get('description', '') or ""
        
        # Combine title and description for better accuracy
        text_to_analyze = f"{title}. {description}"
        
        # Get sentiment scores
        scores = analyzer.polarity_scores(text_to_analyze)
        compound = scores['compound']
        
        # Categorize
        if compound >= 0.05:
            sentiment_label = "Positive"
            color = "green"
        elif compound <= -0.05:
            sentiment_label = "Negative"
            color = "red"
        else:
            sentiment_label = "Neutral"
            color = "gray"
            
        sentiment_data.append({
            "title": title,
            "source": article['source']['name'],
            "published": article['publishedAt'][:10],
            "sentiment_score": compound,
            "label": sentiment_label,
            "color": color,
            "url": article['url']
        })
        
    return pd.DataFrame(sentiment_data)