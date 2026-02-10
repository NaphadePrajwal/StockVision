import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots # New import for advanced charts
from data_loader import fetch_stock_data, get_company_info
from news_manager import fetch_finnhub_news, process_news_with_finbert
from feature_engine import add_technical_indicators # New Import
from model_engine import StockPredictor
import random 


# --- Page Config (Dark Mode is default in Streamlit, but we can tweak layout) ---
st.set_page_config(page_title="StockVision", layout="wide")

st.title("⚡ StockVision: AI-Powered Market Forecaster")

@st.cache_data
def load_ticker_data():
    """
    Loads a dataset of ~8,000 US stock symbols (NASDAQ, NYSE, AMEX).
    Source: GitHub raw dataset
    """
    # URL to a clean CSV of US Stock Symbols
    url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/all/all_tickers.txt"
    
    try:
        # Load the CSV
        df = pd.read_csv(url, header=None, names=["Ticker"])
        
        # Add some popular Indices manually (since they aren't usually in Stock lists)
        indices = pd.DataFrame({
            "Ticker": ["^GSPC", "^DJI", "^IXIC", "BTC-USD", "ETH-USD", "INR=X"]
        })
        
        # Combine them
        full_df = pd.concat([indices, df], ignore_index=True)
        return full_df
    except Exception as e:
        # Fallback if internet is down
        return pd.DataFrame({"Ticker": ["AAPL", "GOOGL", "MSFT", "TSLA"]})


def get_currency_symbol(ticker):
    """
    Returns '₹' if the ticker is Indian, otherwise '$'.
    """
    # Check for Indian suffixes (.NS, .BO) or specific Indian indices
    if ticker.endswith(".NS") or ticker.endswith(".BO") or ticker in ["^NSEI", "^BSESN", "INR=X"]:
        return "₹"
    else:
        return "$"
    
# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    # --- NEW: Dynamic Stock Loader ---
    st.subheader("Asset Selection")
    
    with st.spinner("Loading Tickers..."):
        ticker_df = load_ticker_data()
        
    # Create the dropdown
    # We allow the user to type to search in this huge list
    ticker = st.selectbox(
        "Select Asset:",
        ticker_df["Ticker"], # The list of 8000+ symbols
        index=0  # Default to the first one (S&P 500)
    )
    
    # Optional: Allow manual entry if they can't find it
    use_manual = st.checkbox("I can't find my ticker")
    if use_manual:
        ticker = st.text_input("Enter Ticker Symbol manually:", "AAPL")
    period = st.selectbox("History Period", ["1y", "2y", "5y", "max"], index=1)
    st.info(" Tip: Try 'GOOGL', 'TSLA', or 'MSFT'")

# --- Main Logic ---
if ticker:
    # 1. Fetch & Process Data
    with st.spinner(f"Analying market data for {ticker}..."):
        # A. Get Stock Data
        df = fetch_stock_data(ticker, period)
        
        # B. Get Company Info
        company_info = get_company_info(ticker)
        
       # C. Get News & Sentiment (Finnhub + FinBERT)
        if "FINNHUB_API_KEY" in st.secrets:
            api_key = st.secrets["FINNHUB_API_KEY"]
            with st.spinner("Fetching financial news & analyzing with FinBERT..."):
                raw_news = fetch_finnhub_news(ticker, api_key)
                sentiment_df = process_news_with_finbert(raw_news)
        else:
            st.error("Finnhub API Key missing!")
            sentiment_df = None

        # D. Add Technical Indicators
        if df is not None:
            df = add_technical_indicators(df)

        # E. Merge Sentiment into the Main DataFrame (Phase 5 NEW)
        # We create a new column 'Sentiment' in the main df
        df['Sentiment'] = 0.0 # Default to neutral (0.0)
        
        if sentiment_df is not None and not sentiment_df.empty:
            # Calculate average sentiment from the news we found
            avg_sentiment = sentiment_df['sentiment_score'].mean()
            
            # Apply this score to the last 5 days of data 
            # (So the AI knows the CURRENT news affects the LATEST prices)
            df.iloc[-5:, df.columns.get_loc('Sentiment')] = avg_sentiment

    # 2. Build the Dashboard Layout
    if df is not None and not df.empty:
        # -- Header Section --
        col_head1, col_head2 = st.columns([3, 1])
        with col_head1:
            if company_info:
                st.subheader(f"{company_info.get('longName', ticker)}")
                st.caption(f" {company_info.get('sector', 'N/A')} | {company_info.get('industry', 'N/A')}")
        
        with col_head2:
            # Display Current Price (Last Close)
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            delta = current_price - prev_price
            
            # --- NEW: Get Dynamic Currency Symbol ---
            currency = get_currency_symbol(ticker)
            
            # Display with the correct symbol (₹ or $)
            st.metric(
                label="Current Price", 
                value=f"{currency} {current_price:.2f}", 
                delta=f"{delta:.2f}"
            )

        # -- Main Content Area --
        # We use tabs to organize the view like a pro app
        tab1, tab2, tab3 = st.tabs(["📈 Technical Dashboard", "📰 News & Sentiment", "🤖 AI Forecast"])
        
        with tab1:
            # Create a subplot figure with 2 rows (Price on top, Indicators below)
            # This matches the "stacked" look of professional trading tools
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                vertical_spacing=0.05, row_heights=[0.7, 0.3])

            # Row 1: Candlestick Price Chart
            fig.add_trace(go.Candlestick(x=df['Date'],
                            open=df['Open'], high=df['High'],
                            low=df['Low'], close=df['Close'],
                            name='OHLC'), row=1, col=1)
            
            # Add Bollinger Bands (Using the NEW simple names)
            if 'UpperBand' in df.columns and 'LowerBand' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['UpperBand'], mode='lines', 
                                        line=dict(width=1, color='gray'), name='Upper Band'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['Date'], y=df['LowerBand'], mode='lines', 
                                        line=dict(width=1, color='gray'), name='Lower Band'), row=1, col=1)
            
            # -------------------------------------

            # Row 2: RSI Indicator
            fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', 
                                     line=dict(color='purple'), name='RSI'), row=2, col=1)
            
            # Add 70/30 lines for Overbought/Oversold
            fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=70, y1=70, 
                          line=dict(color="red", width=1, dash="dash"), row=2, col=1)
            fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=30, y1=30, 
                          line=dict(color="green", width=1, dash="dash"), row=2, col=1)

            fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.subheader("🛡️ Verified News Intelligence")
            st.caption("Pipeline: Fake News Detection AI ➔ FinBERT Sentiment AI")

            if sentiment_df is not None and not sentiment_df.empty:
                
                # --- STEP 1: THE FILTER (Data Separation) ---
                # We split the dataframe into two parts: Trusted vs. Untrusted
                clean_df = sentiment_df[sentiment_df['is_trusted'] == True]
                fake_df = sentiment_df[sentiment_df['is_trusted'] == False]
                
                # Count how many fake articles we found
                fake_count = len(fake_df)
                
                # Show a Security Status Message
                if fake_count > 0:
                    st.warning(f"⚠️ Security Alert: {fake_count} articles were flagged as 'Suspicious/Fake' and removed from the AI prediction.")
                else:
                    st.success("✅ Integrity Check Passed: All news sources appear legitimate.")
                
                # ---------------------------------------------

                # --- STEP 2: CALCULATE SCORE (Using ONLY Clean Data) ---
                if not clean_df.empty:
                    # The AI ONLY sees this score. It never sees the fake news score.
                    avg_score = clean_df['sentiment_score'].mean()
                else:
                    avg_score = 0.0 # Default to Neutral if all news is fake
                
                # Display the Gauge/Meter (Same as before)
                col_sent1, col_sent2 = st.columns([1, 2])
                with col_sent1:
                    if avg_score > 0.05:
                        st.success(f"🐂 Bullish (Score: {avg_score:.2f})")
                    elif avg_score < -0.05:
                        st.error(f"🐻 Bearish (Score: {avg_score:.2f})")
                    else:
                        st.warning(f"😐 Neutral (Score: {avg_score:.2f})")
                
                with col_sent2:
                    st.progress((avg_score + 1) / 2)

                # --- STEP 3: DISPLAY NEWS CARDS (Visualizing the Block) ---
                st.markdown("### 📰 Latest Financial News")
                
                IGNORE_API_IMAGES = True 
                FALLBACK_IMAGES = [
                    "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1535320903710-d9cf11350132?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1526304640152-d4619684e484?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=300&q=80"
                ]

                for index, row in sentiment_df.iterrows():
                     with st.container():
                        col_img, col_text = st.columns([1, 3])
                        
                        # --- LOGIC A: IF NEWS IS TRUSTED (Show Normal Card) ---
                        if row['is_trusted']:
                            with col_img:
                                # Show Image (Real or Wallpaper)
                                img_idx = index % len(FALLBACK_IMAGES)
                                if not IGNORE_API_IMAGES and row['image'] and row['image'].strip() != "":
                                    try:
                                        st.image(row['image'], use_container_width=True)
                                    except:
                                        st.image(FALLBACK_IMAGES[img_idx], use_container_width=True)
                                else:
                                    st.image(FALLBACK_IMAGES[img_idx], use_container_width=True)

                            with col_text:
                                if row['label'] == "Positive": emoji = "🟢"
                                elif row['label'] == "Negative": emoji = "🔴"
                                else: emoji = "⚪"
                                    
                                st.markdown(f"**[{emoji} {row['label']}]** \n[{row['title']}]({row['url']})")
                                
                                if pd.notna(row['summary']) and row['summary'] != "":
                                    st.caption(f"{row['summary'][:200]}...")
                                
                                st.caption(f"Source: {row['source']} • {row['published']}")
                                st.caption(f"FinBERT Confidence: {row['sentiment_score']:.4f}")

                        # --- LOGIC B: IF NEWS IS FAKE (Show "Blocked" Card) ---
                        else:
                            with col_img:
                                # Show a "Warning" Image
                                st.image("https://cdn-icons-png.flaticon.com/512/564/564619.png", width=80) 
                            
                            with col_text:
                                st.error("🚫 BLOCKED: SUSPICIOUS SOURCE DETECTED")
                                st.markdown(f"~~{row['title']}~~") # Strikethrough text
                                st.caption(f"Reason: AI detected potential fake news patterns ({row['fake_confidence']*100:.1f}% confidence).")
                                st.caption("Action: This article was removed from the price prediction model.")

                     st.divider()
            else:
                st.info("No recent financial news found for this ticker.")

        # --- TAB 3: AI Forecast ---
        with tab3:
            st.subheader("🤖 AI Price Prediction (LSTM)")
            st.caption("The model analyzes the past 60 days to predict future trends.")

            col_ai1, col_ai2 = st.columns([1, 3])
            
            with col_ai1:
                forecast_days = st.slider("Forecast Days", min_value=7, max_value=90, value=30)
                if st.button("Train Model & Predict 🚀"):
                    with st.spinner("Training Multivariate Model (Price + News + Tech)..."):
                        # Initialize with the FULL dataframe now (Price + RSI + Sentiment)
                        predictor = StockPredictor(df)  # <--- NEW LINE
                        # Note: build_model is called inside train() now, so we don't need to call it manually
                        predictor.train()
                        
                        # Forecast
                        forecast = predictor.predict_future(days=forecast_days)
                        
                        # Create Future Dates
                        last_date = df['Date'].iloc[-1]
                        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
                        
                        # Save to session state to keep chart after refresh
                        st.session_state['forecast'] = forecast
                        st.session_state['future_dates'] = future_dates
                        # ... (existing code inside the button) ...
                        st.success("Prediction Complete!")
                        
                        # --- IMPROVED: Explainable AI (Feature Importance) ---
                        st.markdown("---")
                        st.subheader("📊 Why did the AI make this prediction?")
                        st.caption("The chart below shows which factors (Technical & Sentiment) had the strongest relationship with the price.")
                        
                        # 1. Calculate Correlation
                        numeric_df = df.select_dtypes(include=['number'])
                        correlation = numeric_df.corr()['Close'].drop('Close')
                        
                        # 2. Filter & Sort for "Top Drivers"
                        # We only want to show the top 8 most important features to keep it clean
                        importance_df = pd.DataFrame({
                            'Feature': correlation.index,
                            'Importance': correlation.values
                        })
                        
                        # Create a "Color" column based on positive/negative correlation
                        importance_df['Color'] = importance_df['Importance'].apply(lambda x: '#00FA9A' if x > 0 else '#FF4B4B') # SpringGreen & Red
                        
                        # Sort by Absolute Value (Magnitude) and take top 8
                        importance_df['Abs_Importance'] = importance_df['Importance'].abs()
                        importance_df = importance_df.sort_values(by='Abs_Importance', ascending=True).tail(8)
                        
                        # 3. Create the Pro-Level Bar Chart
                        fig_xai = go.Figure(go.Bar(
                            x=importance_df['Importance'],
                            y=importance_df['Feature'],
                            orientation='h',
                            marker=dict(
                                color=importance_df['Color'], # Use our custom colors
                                line=dict(color='rgba(255, 255, 255, 0.2)', width=1) # Subtle border
                            ),
                            text=importance_df['Importance'].apply(lambda x: f"{x:.2f}"), # Show values on bars
                            textposition='auto'
                        ))
                        
                        fig_xai.update_layout(
                            title="<b>Top Factors Influencing Price</b>", # Bold Title
                            xaxis_title="Correlation Strength (-1 to +1)",
                            yaxis_title=None, # Remove y-axis label to save space
                            template="plotly_dark", # Ensure dark mode
                            height=400,
                            margin=dict(l=20, r=20, t=50, b=20),
                            showlegend=False
                        )
                        
                        # Add a vertical line at 0 for clarity
                        fig_xai.add_vline(x=0, line_width=1, line_dash="solid", line_color="gray")
                        
                        st.plotly_chart(fig_xai, use_container_width=True)
                        
                        # Add a "Pro Tip" explanation
                        with st.expander("ℹ️ How to read this chart"):
                            st.markdown("""
                            * **Green Bars (Right):** These features move *with* the price. (e.g., If Sentiment is Green, good news = higher price).
                            * **Red Bars (Left):** These features move *opposite* to the price.
                            * **Bar Length:** The longer the bar, the more the AI relies on this factor.
                            """)
            with col_ai2:
                if 'forecast' in st.session_state:
                    # Combine historical and forecast data for plotting
                    fig_ai = go.Figure()
                    
                    # Historical Data (Last 90 days for context)
                    fig_ai.add_trace(go.Scatter(
                        x=df['Date'].iloc[-90:], 
                        y=df['Close'].iloc[-90:], 
                        mode='lines', 
                        name='Historical Price',
                        line=dict(color='#00F0FF', width=2)
                    ))
                    
                    # Forecast Data
                    fig_ai.add_trace(go.Scatter(
                        x=st.session_state['future_dates'], 
                        y=st.session_state['forecast'],
                        mode='lines+markers', 
                        name='AI Prediction',
                        line=dict(color='#FF0055', width=2, dash='dot')
                    ))
                    
                    fig_ai.update_layout(
                        title="LSTM Model Forecast",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        template="plotly_dark",
                        height=500
                    )
                    st.plotly_chart(fig_ai, use_container_width=True)
                    
                    # Show numeric target
                    final_pred = st.session_state['forecast'][-1]
                    current = df['Close'].iloc[-1]
                    change = ((final_pred - current) / current) * 100
                    
                    color = "green" if change > 0 else "red"
                    st.markdown(f"### Predicted Price in {forecast_days} days: **${final_pred:.2f}**")
                    st.markdown(f"Expected Change: <span style='color:{color}'>{change:.2f}%</span>", unsafe_allow_html=True)

                else:
                    st.info("Click the button to train the AI and generate a forecast.")

    else:
        st.error(f"Could not find data for ticker '{ticker}'.")

else:
    st.info("Enter a stock ticker to begin analysis.")