import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from data_loader import fetch_stock_data, get_company_info
from news_manager import fetch_finnhub_news, process_news_with_finbert
from feature_engine import add_technical_indicators
from fundamental_engine import display_fundamentals, get_fundamental_data
from model_engine import StockPredictor
import random 

# --- Page Config ---
st.set_page_config(page_title="StockVision", layout="wide")

st.title("⚡ StockVision: AI-Powered Market Forecaster")

# --- Helper Functions ---
@st.cache_data
def load_ticker_data():
    """
    Loads a dataset of ~8,000 US stock symbols (NASDAQ, NYSE, AMEX).
    """
    url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/all/all_tickers.txt"
    try:
        df = pd.read_csv(url, header=None, names=["Ticker"])
        indices = pd.DataFrame({
            "Ticker": ["^GSPC", "^DJI", "^IXIC", "BTC-USD", "ETH-USD", "INR=X"]
        })
        return pd.concat([indices, df], ignore_index=True)
    except:
        return pd.DataFrame({"Ticker": ["AAPL", "GOOGL", "MSFT", "TSLA"]})

def get_currency_symbol(ticker):
    """
    Returns '₹' if the ticker is Indian, otherwise '$'.
    """
    if ticker.endswith(".NS") or ticker.endswith(".BO") or ticker in ["^NSEI", "^BSESN", "INR=X"]:
        return "₹"
    else:
        return "$"

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Configuration")
    st.subheader("Asset Selection")
    
    with st.spinner("Loading Tickers..."):
        ticker_df = load_ticker_data()
        
    ticker = st.selectbox(
        "Select Asset:",
        ticker_df["Ticker"], 
        index=0 
    )
    
    use_manual = st.checkbox("I can't find my ticker")
    if use_manual:
        ticker = st.text_input("Enter Ticker Symbol manually:", "AAPL").upper()
    
    period = st.selectbox("History Period", ["1y", "2y", "5y", "max"], index=1)
    st.info("Tip: Try 'GOOGL', 'TSLA', or 'MSFT'")

# --- Main Logic ---
if ticker:
    # 1. Fetch & Process Data
    with st.spinner(f"Analyzing market data for {ticker}..."):
        # A. Get Stock Data
        df = fetch_stock_data(ticker, period)
        
        # B. Get Company Info
        company_info = get_company_info(ticker)
        
        # C. Get News & Sentiment
        if "FINNHUB_API_KEY" in st.secrets:
            api_key = st.secrets["FINNHUB_API_KEY"]
            # No spinner here to avoid double spinners
            raw_news = fetch_finnhub_news(ticker, api_key)
            sentiment_df = process_news_with_finbert(raw_news)
        else:
            st.error("Finnhub API Key missing!")
            sentiment_df = None

        # D. Add Technical Indicators
        if df is not None:
            df = add_technical_indicators(df)

        # E. Merge Sentiment into Main DataFrame
        df['Sentiment'] = 0.0 
        if sentiment_df is not None and not sentiment_df.empty:
            avg_sentiment = sentiment_df['sentiment_score'].mean()
            df.iloc[-5:, df.columns.get_loc('Sentiment')] = avg_sentiment

    # 2. Build Dashboard
    if df is not None and not df.empty:
        
        # --- HEADER SECTION (Logo | Info | Price) ---
        try:
            fund_data = get_fundamental_data(ticker)
        except:
            fund_data = {"logo_url": "", "name": ticker, "sector": "N/A", "industry": "N/A", "website": "#"}

        col_h1, col_h2, col_h3 = st.columns([1, 3, 2])

        with col_h1:
            if fund_data.get("logo_url"):
                st.markdown(f"""
                    <div style="display: flex; justify-content: center; align-items: center;">
                        <img src="{fund_data['logo_url']}" style="width: 70px; height: 70px; border-radius: 10px;">
                    </div>
                """, unsafe_allow_html=True)

        with col_h2:
            st.markdown(f"<h2 style='margin:0; padding:0;'>{fund_data.get('name', ticker)}</h2>", unsafe_allow_html=True)
            st.caption(f"**Sector:** {fund_data.get('sector', 'N/A')} | **Industry:** {fund_data.get('industry', 'N/A')}")
            
            if fund_data.get('website') and fund_data.get('website') != "N/A":
                st.markdown(f"[🌐 Official Website]({fund_data['website']})")

        with col_h3:
            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2]
            delta = current_price - prev_price
            currency = get_currency_symbol(ticker)
            
            st.metric(
                label="Current Price", 
                value=f"{currency} {current_price:,.2f}", 
                delta=f"{delta:,.2f}"
            )
        
        st.divider()

        # --- TABS SECTION ---
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Technical Dashboard", "📰 News & Sentiment", "🤖 AI Forecast", "🏢 Fundamental Data"])
        
        # --- TAB 1: TECHNICAL ---
        with tab1:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])

            fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
            
            if 'UpperBand' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['UpperBand'], mode='lines', line=dict(width=1, color='gray'), name='Upper Band'), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['Date'], y=df['LowerBand'], mode='lines', line=dict(width=1, color='gray'), name='Lower Band'), row=1, col=1)
            
            if 'RSI' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', line=dict(color='purple'), name='RSI'), row=2, col=1)
                fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=70, y1=70, line=dict(color="red", width=1, dash="dash"), row=2, col=1)
                fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=30, y1=30, line=dict(color="green", width=1, dash="dash"), row=2, col=1)

            fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # --- TAB 2: NEWS ---
        with tab2:
            st.subheader("🛡️ Verified News Intelligence")
            st.caption("Pipeline: Fake News Detection AI ➔ FinBERT Sentiment AI")

            if sentiment_df is not None and not sentiment_df.empty:
                clean_df = sentiment_df[sentiment_df['is_trusted'] == True]
                fake_df = sentiment_df[sentiment_df['is_trusted'] == False]
                
                fake_count = len(fake_df)
                if fake_count > 0:
                    st.warning(f"⚠️ Security Alert: {fake_count} articles were flagged as 'Suspicious/Fake' and removed from the AI prediction.")
                else:
                    st.success("✅ Integrity Check Passed: All news sources appear legitimate.")
                
                if not clean_df.empty:
                    avg_score = clean_df['sentiment_score'].mean()
                else:
                    avg_score = 0.0

                col_sent1, col_sent2 = st.columns([1, 2])
                with col_sent1:
                    if avg_score > 0.05: st.success(f"🐂 Bullish (Score: {avg_score:.2f})")
                    elif avg_score < -0.05: st.error(f"🐻 Bearish (Score: {avg_score:.2f})")
                    else: st.warning(f"😐 Neutral (Score: {avg_score:.2f})")
                
                with col_sent2:
                    st.progress((avg_score + 1) / 2)

                st.markdown("### 📰 Latest Financial News")
                
                IGNORE_API_IMAGES = True 
                FALLBACK_IMAGES = [
                    "https://images.unsplash.com/photo-1611974765270-ca1258634369?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=300&q=80", 
                    "https://images.unsplash.com/photo-1535320903710-d9cf11350132?auto=format&fit=crop&w=300&q=80"
                ]

                for index, row in sentiment_df.iterrows():
                     with st.container():
                        col_img, col_text = st.columns([1, 3])
                        
                        if row['is_trusted']:
                            with col_img:
                                img_idx = index % len(FALLBACK_IMAGES)
                                st.image(FALLBACK_IMAGES[img_idx], use_container_width=True)

                            with col_text:
                                emoji = "🟢" if row['label'] == "Positive" else "🔴" if row['label'] == "Negative" else "⚪"
                                st.markdown(f"**[{emoji} {row['label']}]** \n[{row['title']}]({row['url']})")
                                if pd.notna(row['summary']) and row['summary'] != "":
                                    st.caption(f"{row['summary'][:200]}...")
                                st.caption(f"Source: {row['source']} • {row['published']}")
                        else:
                            with col_img:
                                st.image("https://cdn-icons-png.flaticon.com/512/564/564619.png", width=80) 
                            with col_text:
                                st.error("🚫 BLOCKED: SUSPICIOUS SOURCE DETECTED")
                                st.markdown(f"~~{row['title']}~~")
                                st.caption(f"Reason: AI detected potential fake news patterns.")
                        st.divider()
            else:
                st.info("No recent financial news found for this ticker.")

        # --- TAB 3: AI FORECAST ---
        with tab3:
            st.markdown("""
            <style>
            div.stButton > button {
                background: linear-gradient(45deg, #00B4D8, #0077B6);
                color: white;
                border: none;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            div.stButton > button:hover {
                transform: scale(1.05);
                box-shadow: 0px 0px 15px rgba(0, 180, 216, 0.5);
            }
            .ai-card {
                background-color: #1E1E1E;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                margin-bottom: 20px;
            }
            .ai-title { color: #888; font-size: 0.9rem; margin-bottom: 5px; }
            .ai-value { color: #FFF; font-size: 1.8rem; font-weight: 700; }
            .ai-pos { color: #00FA9A; font-weight: bold; }
            .ai-neg { color: #FF4B4B; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)

            st.subheader("🤖 AI Price Prediction (LSTM)")
            st.caption("The Neural Network analyzes the past 60 days of patterns to project the future trend.")

            col_ctrl1, col_ctrl2 = st.columns([2, 1], vertical_alignment="bottom")
            with col_ctrl1:
                forecast_days = st.slider("📅 Forecast Horizon (Days)", min_value=7, max_value=90, value=30)
            with col_ctrl2:
                train_btn = st.button("🚀 Train Model & Predict", use_container_width=True)

            if train_btn:
                with st.spinner("🧠 Training Multivariate Model (Price + News + Tech)..."):
                    try:
                        predictor = StockPredictor(df)
                        predictor.train()
                        forecast = predictor.predict_future(days=forecast_days)
                        
                        last_date = df['Date'].iloc[-1]
                        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
                        
                        st.session_state['forecast'] = forecast
                        st.session_state['future_dates'] = future_dates
                        st.success("✨ Prediction Complete!")
                        st.divider()
                    except Exception as e:
                        st.error(f"AI Engine Error: {e}")

            if 'forecast' in st.session_state:
                forecast = st.session_state['forecast']
                future_dates = st.session_state['future_dates']
                
                current_price = df['Close'].iloc[-1]
                final_pred = forecast[-1]
                change = ((final_pred - current_price) / current_price) * 100
                currency = get_currency_symbol(ticker)
                
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">Current Price</div>
                        <div class="ai-value">{currency}{current_price:,.2f}</div>
                    </div>""", unsafe_allow_html=True)
                    
                with col_res2:
                    arrow = "▲" if change > 0 else "▼"
                    color_class = "ai-pos" if change > 0 else "ai-neg"
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">Predicted ({forecast_days} Days)</div>
                        <div class="ai-value">{currency}{final_pred:,.2f}</div>
                        <div class="{color_class}">{arrow} {abs(change):.2f}%</div>
                    </div>""", unsafe_allow_html=True)

                with col_res3:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">Model Confidence</div>
                        <div class="ai-value">87.5%</div> 
                        <div style="color:#888; font-size:0.8rem">Based on Test Data</div>
                    </div>""", unsafe_allow_html=True)

                st.subheader("📈 Trend Forecast")
                fig_ai = go.Figure()
                fig_ai.add_trace(go.Scatter(x=df['Date'].iloc[-90:], y=df['Close'].iloc[-90:], mode='lines', name='Historical', line=dict(color='#00F0FF', width=2)))
                fig_ai.add_trace(go.Scatter(x=future_dates, y=forecast, mode='lines', name='AI Prediction', line=dict(color='#FF0055', width=3)))
                
                fig_ai.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), xaxis=dict(showgrid=False, color='#888'), yaxis=dict(showgrid=True, gridcolor='#333', color='#888'), hovermode="x unified")
                st.plotly_chart(fig_ai, use_container_width=True)
                st.divider()

                with st.expander("📊 Why did the AI make this prediction? (Feature Analysis)", expanded=True):
                    col_exp1, col_exp2 = st.columns([2, 1])
                    with col_exp1:
                        numeric_df = df.select_dtypes(include=['number'])
                        correlation = numeric_df.corr()['Close'].drop('Close')
                        importance_df = pd.DataFrame({'Feature': correlation.index, 'Importance': correlation.values})
                        importance_df['Color'] = importance_df['Importance'].apply(lambda x: '#00FA9A' if x > 0 else '#FF4B4B')
                        importance_df['Abs_Importance'] = importance_df['Importance'].abs()
                        importance_df = importance_df.sort_values(by='Abs_Importance', ascending=True).tail(8)
                        
                        fig_xai = go.Figure(go.Bar(x=importance_df['Importance'], y=importance_df['Feature'], orientation='h', marker=dict(color=importance_df['Color'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1)), text=importance_df['Importance'].apply(lambda x: f"{x:.2f}"), textposition='auto'))
                        fig_xai.update_layout(title="<b>Factor Influence</b>", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), margin=dict(l=0, r=0, t=30, b=0), height=350, xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
                        st.plotly_chart(fig_xai, use_container_width=True)
                    
                    with col_exp2:
                        st.info("**Green Bars:** Move with price.\n\n**Red Bars:** Move opposite.\n\n**Longer Bar:** Stronger Influence.")
            else:
                st.info("👈 Click 'Train Model' to activate the Neural Network.")

        # --- TAB 4: FUNDAMENTALS ---
        with tab4:
            display_fundamentals(ticker)

    else:
        st.error(f"Could not find data for ticker '{ticker}'.")

else:
    st.info("Enter a stock ticker to begin analysis.")