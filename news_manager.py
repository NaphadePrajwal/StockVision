import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from sentiment_engine import predict_finbert_sentiment
from fake_news_engine import detect_fake_news

def fetch_google_news(ticker):
    """
    FALLBACK: Fetches news from Google News RSS (India) if Finnhub fails.
    """
    # 1. Clean the ticker (e.g., "RELIANCE.NS" -> "RELIANCE")
    clean_ticker = ticker.split('.')[0]
    
    # 2. Build the RSS URL for India (hl=en-IN, gl=IN)
    # We search for "TICKER stock news"
    url = f"https://news.google.com/rss/search?q={clean_ticker}+stock+news+india&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        response = requests.get(url)
        root = ET.fromstring(response.content)
        
        articles = []
        # Parse the XML
        for item in root.findall('./channel/item')[:10]: # Limit to 10
            title = item.find('title').text
            link = item.find('link').text
            pub_date_str = item.find('pubDate').text
            
            # Google dates look like: "Fri, 10 Feb 2026 08:30:00 GMT"
            # We convert this to YYYY-MM-DD
            try:
                dt_obj = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                pub_date = dt_obj.strftime('%Y-%m-%d')
                timestamp = dt_obj.timestamp()
            except:
                pub_date = datetime.now().strftime('%Y-%m-%d')
                timestamp = datetime.now().timestamp()

            # Create a structure that matches Finnhub's format
            articles.append({
                'headline': title,
                'summary': title, # Google RSS doesn't give summaries, so we use title
                'url': link,
                'datetime': timestamp,
                'source': 'Google News (India)',
                'image': '' # RSS doesn't provide images
            })
            
        return articles

    except Exception as e:
        print(f"Google News Error: {e}")
        return []

def fetch_finnhub_news(ticker, api_key):
    """
    Primary: Finnhub. Secondary: Google News.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    url = f"https://finnhub.io/api/v1/company-news?symbol={ticker}&from={start_date}&to={today}&token={api_key}"
    
    finnhub_articles = []
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # --- CRITICAL FIX: Check if we actually got a LIST of news ---
        if isinstance(data, list):
            finnhub_articles = data
        else:
            # If Finnhub returns a Dictionary (Error Message), ignore it
            print(f"Finnhub API Response (Not a list): {data}")
            finnhub_articles = []
            
    except Exception as e:
        print(f"Finnhub Connection Error: {e}")
        finnhub_articles = []

    # --- THE FALLBACK LOGIC ---
    # If list is empty (or was invalid), switch to Google News
    if not finnhub_articles:
        print(f"⚠️ Finnhub found no news for {ticker} (or returned error). Switching to Google News...")
        return fetch_google_news(ticker)
    
    return finnhub_articles[:10]


def process_news_with_finbert(articles):
    """
    Process news (works for both Finnhub and Google News data).
    """
    if not articles:
        return pd.DataFrame()
    
    news_data = []
    
    for article in articles:
        headline = article.get('headline', '')
        summary = article.get('summary', '')
        full_text = f"{headline}. {summary}"
        
        # 1. Fake News Detection
        validity, confidence = detect_fake_news(headline)
        
        is_trusted = True
        if validity == "FAKE" and confidence > 0.60:
            is_trusted = False

        # Handle Date Format
        try:
            # If it comes from Finnhub, it's a timestamp (int)
            # If it comes from our Google function, we already made it a timestamp
            pub_date = datetime.fromtimestamp(article['datetime']).strftime('%Y-%m-%d')
        except:
            pub_date = datetime.now().strftime('%Y-%m-%d')
        
        news_data.append({
            'title': headline,
            'summary': summary,
            'image': article.get('image', ''),
            'source': article.get('source', 'Finnhub'),
            'url': article.get('url', '#'),
            'published': pub_date,
            'full_text': full_text,
            'is_trusted': is_trusted,
            'fake_confidence': confidence
        })
        
    # Run FinBERT (Same logic as before)
    if news_data:
        headlines = [item['full_text'] for item in news_data]
        probs = predict_finbert_sentiment(headlines)
        
        sentiments = []
        labels = []
        
        for i in range(len(probs)):
            p_pos = probs[i][0].item()
            p_neg = probs[i][1].item()
            score = p_pos - p_neg
            
            if score > 0.05: label = "Positive"
            elif score < -0.05: label = "Negative"
            else: label = "Neutral"
                
            sentiments.append(score)
            labels.append(label)
            
        df = pd.DataFrame(news_data)
        df['sentiment_score'] = sentiments
        df['label'] = labels
        
        return df
    
    return pd.DataFrame()