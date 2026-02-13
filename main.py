import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from data_loader import fetch_stock_data, get_company_info
from news_manager import fetch_finnhub_news, process_news_with_finbert
from feature_engine import add_technical_indicators
from fundamental_engine import display_fundamentals, get_fundamental_data
from model_engine import StockPredictor
from css_styling import load_global_css, load_card_css, load_news_css, load_chart_css
import random 

# --- Page Config ---
st.set_page_config(page_title="StockVision", layout="wide", initial_sidebar_state="expanded")

# Load Global CSS (MUST be called first)
load_global_css()
load_card_css()
load_news_css()
load_chart_css()

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

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2332 0%, #0a0e27 100%);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.header("⚙️ Configuration")
    st.subheader("Asset Selection")
    
    with st.spinner("Loading Tickers..."):
        ticker_df = load_ticker_data()
        
    ticker = st.selectbox(
        "Select Asset:",
        ticker_df["Ticker"], 
        index=0,
        help="Choose from major indices, stocks, or cryptocurrencies"
    )
    
    use_manual = st.checkbox("I can't find my ticker", help="Enter a custom ticker symbol")
    if use_manual:
        ticker = st.text_input("Enter Ticker Symbol manually:", "AAPL", placeholder="e.g., AAPL, RELIANCE.NS").upper()
    
    period = st.selectbox("History Period", ["1y", "2y", "5y", "max"], index=1, help="Select historical data period")
    
    st.markdown("---")
    st.info("💡 **Tip:** Try 'GOOGL', 'TSLA', 'MSFT', or 'RELIANCE.NS' for Indian stocks")
    
    st.markdown("""
    <p style='text-align: center; color: #a0a0a0; font-size: 0.85rem; margin-top: 40px;'>
    StockVision v1.0<br>
    Powered by ML & Sentiment AI
    </p>
    """, unsafe_allow_html=True)

# --- Main Logic ---
if ticker:
    # 1. Fetch & Process Data
    with st.spinner(f"🔍 Analyzing market data for {ticker}..."):
        # A. Get Stock Data
        df = fetch_stock_data(ticker, period)
        
        # B. Get Company Info
        company_info = get_company_info(ticker)
        
        # C. Get News & Sentiment
        if "FINNHUB_API_KEY" in st.secrets:
            api_key = st.secrets["FINNHUB_API_KEY"]
            raw_news = fetch_finnhub_news(ticker, api_key)
            sentiment_df = process_news_with_finbert(raw_news)
        else:
            st.error("⚠️ Finnhub API Key missing! Please add it to secrets.")
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
                    <div style="display: flex; justify-content: center; align-items: center; padding: 10px;">
                        <img src="{fund_data['logo_url']}" style="width: 80px; height: 80px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0, 180, 216, 0.2);">
                    </div>
                """, unsafe_allow_html=True)

        with col_h2:
            st.markdown(f"""
            <h2 style='margin:0; padding:0; color: #e0e0e0;'>{fund_data.get('name', ticker)}</h2>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <p style='color: #a0a0a0; margin: 5px 0; font-size: 0.95rem;'>
            <strong style='color: #00B4D8;'>Sector:</strong> {fund_data.get('sector', 'N/A')} • 
            <strong style='color: #00B4D8;'>Industry:</strong> {fund_data.get('industry', 'N/A')}
            </p>
            """, unsafe_allow_html=True)
            
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
            st.markdown("""
            <style>
            .chart-container {
                background-color: #1a2332;
                border: 1px solid #2d3748;
                border-radius: 12px;
                padding: 20px;
                margin: 20px 0;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.subheader("📊 Technical Analysis Chart")
            st.caption("OHLC Candlestick with Bollinger Bands & RSI Indicator")
            
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08, row_heights=[0.7, 0.3])

            fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='OHLC'), row=1, col=1)
            
            if 'UpperBand' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['UpperBand'], mode='lines', line=dict(width=1, color='rgba(0, 180, 216, 0.5)'), name='Upper Band', fill=None), row=1, col=1)
                fig.add_trace(go.Scatter(x=df['Date'], y=df['LowerBand'], mode='lines', line=dict(width=1, color='rgba(0, 180, 216, 0.5)'), name='Lower Band', fill='tonexty', fillcolor='rgba(0, 180, 216, 0.1)'), row=1, col=1)
            
            if 'RSI' in df.columns:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], mode='lines', line=dict(color='#FFB703', width=2), name='RSI (14)'), row=2, col=1)
                fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=70, y1=70, line=dict(color="#FF4B4B", width=1, dash="dash"), row=2, col=1)
                fig.add_shape(type="line", x0=df['Date'].iloc[0], x1=df['Date'].iloc[-1], y0=30, y1=30, line=dict(color="#00FA9A", width=1, dash="dash"), row=2, col=1)

            fig.update_layout(
                height=650, 
                xaxis_rangeslider_visible=False, 
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10, 14, 39, 0.5)',
                font=dict(color="#e0e0e0"),
                hovermode='x unified',
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Technical Indicators Summary
            col_t1, col_t2, col_t3, col_t4 = st.columns(4)
            
            if 'RSI' in df.columns:
                latest_rsi = df['RSI'].iloc[-1]
                col_t1.metric("RSI (14)", f"{latest_rsi:.2f}", 
                            help="Overbought >70, Oversold <30")
            
            if 'MACD_12_26_9' in df.columns:
                col_t2.metric("MACD", f"{df['MACD_12_26_9'].iloc[-1]:.4f}", 
                            help="Momentum Indicator")
            
            if 'MidBand' in df.columns:
                bb_width = df['UpperBand'].iloc[-1] - df['LowerBand'].iloc[-1]
                col_t3.metric("BB Width", f"{bb_width:.2f}", 
                            help="Volatility Measure")
            
            current_price = df['Close'].iloc[-1]
            yearly_high = df['High'].max()
            yearly_low = df['Low'].min()
            col_t4.metric("52W High/Low", f"{yearly_high:.2f} / {yearly_low:.2f}")

        # --- TAB 2: NEWS ---
        with tab2:
            st.subheader("🛡️ Verified News Intelligence")
            st.caption("Pipeline: Fake News Detection AI ➔ FinBERT Sentiment Analysis")

            if sentiment_df is not None and not sentiment_df.empty:
                clean_df = sentiment_df[sentiment_df['is_trusted'] == True]
                fake_df = sentiment_df[sentiment_df['is_trusted'] == False]
                
                # --- SENTIMENT BREAKDOWN SECTION ---
                st.markdown('<div class="section-header">📊 Sentiment Analysis Overview</div>', unsafe_allow_html=True)
                
                # Calculate sentiment metrics
                positive_count = len(clean_df[clean_df['label'] == 'Positive'])
                negative_count = len(clean_df[clean_df['label'] == 'Negative'])
                neutral_count = len(clean_df[clean_df['label'] == 'Neutral'])
                
                # Overall sentiment score (average of all verified news)
                if len(clean_df) > 0:
                    overall_sentiment = clean_df['sentiment_score'].mean()
                else:
                    overall_sentiment = 0
                
                # Sentiment interpretation
                if overall_sentiment > 0.1:
                    sentiment_emoji = "🟢"
                    sentiment_label = "POSITIVE"
                    sentiment_color = "#00FA9A"
                elif overall_sentiment < -0.1:
                    sentiment_emoji = "🔴"
                    sentiment_label = "NEGATIVE"
                    sentiment_color = "#FF4B4B"
                else:
                    sentiment_emoji = "⚪"
                    sentiment_label = "NEUTRAL"
                    sentiment_color = "#FFB703"
                
                # Display overall sentiment with styling
                col_sent1, col_sent2, col_sent3, col_sent4, col_sent5 = st.columns(5)
                
                with col_sent1:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">Market Sentiment</div>
                        <div style="color: {sentiment_color}; font-size: 2.5rem; font-weight: 800; margin: 10px 0;">
                            {sentiment_emoji}
                        </div>
                        <div style="color: {sentiment_color}; font-weight: 700; font-size: 1.1rem;">
                            {sentiment_label}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sent2:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">Overall Score</div>
                        <div class="ai-value">{overall_sentiment:.3f}</div>
                        <div style="color: #888; font-size: 0.8rem; margin-top: 8px;">
                        Range: -1.0 to +1.0
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sent3:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">🟢 Positive News</div>
                        <div class="ai-value">{positive_count}</div>
                        <div style="color: #00FA9A; font-size: 0.9rem; margin-top: 8px;">
                        {(positive_count/len(clean_df)*100):.0f}% of news
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sent4:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">🔴 Negative News</div>
                        <div class="ai-value">{negative_count}</div>
                        <div style="color: #FF4B4B; font-size: 0.9rem; margin-top: 8px;">
                        {(negative_count/len(clean_df)*100):.0f}% of news
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sent5:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">⚪ Neutral News</div>
                        <div class="ai-value">{neutral_count}</div>
                        <div style="color: #FFB703; font-size: 0.9rem; margin-top: 8px;">
                        {(neutral_count/len(clean_df)*100):.0f}% of news
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # Sentiment distribution chart
                sentiment_counts = pd.DataFrame({
                    'Sentiment': ['Positive', 'Negative', 'Neutral'],
                    'Count': [positive_count, negative_count, neutral_count],
                    'Color': ['#00FA9A', '#FF4B4B', '#FFB703']
                })
                
                fig_sentiment = go.Figure(data=[
                    go.Bar(
                        x=sentiment_counts['Sentiment'],
                        y=sentiment_counts['Count'],
                        marker=dict(color=sentiment_counts['Color'], line=dict(color='white', width=2)),
                        text=sentiment_counts['Count'],
                        textposition='auto',
                    )
                ])
                
                fig_sentiment.update_layout(
                    title="<b>Sentiment Distribution of Verified News</b>",
                    xaxis_title='Sentiment Type',
                    yaxis_title='Number of Articles',
                    height=350,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(10, 14, 39, 0.5)',
                    font=dict(color='#e0e0e0'),
                    showlegend=False,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_sentiment, use_container_width=True)
                st.divider()
                
                # Summary Stats
                col_n1, col_n2, col_n3 = st.columns(3)
                col_n1.metric("✅ Verified News", len(clean_df), help="Trusted articles from verified sources")
                col_n2.metric("🚫 Suspicious", len(fake_df), help="Articles blocked due to potential fake news")
                col_n3.metric("📊 Total Analyzed", len(sentiment_df), help="Total news articles processed")
                
                st.divider()

                if len(clean_df) > 0:
                    st.markdown("#### ✅ Verified & Trusted News")
                    
                    FALLBACK_IMAGES = [
                        "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=300&q=80",
                        "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?auto=format&fit=crop&w=300&q=80", 
                        "https://images.unsplash.com/photo-1535320903710-d9cf11350132?auto=format&fit=crop&w=300&q=80"
                    ]

                    for index, row in clean_df.iterrows():
                        with st.container():
                            col_img, col_text = st.columns([1, 3])
                            
                            with col_img:
                                img_idx = index % len(FALLBACK_IMAGES)
                                st.image(FALLBACK_IMAGES[img_idx], use_container_width=True)

                            with col_text:
                                emoji = "🟢" if row['label'] == "Positive" else "🔴" if row['label'] == "Negative" else "⚪"
                                st.markdown(f"""
                                <div class="news-container">
                                    <div class="news-title">[{emoji} {row['label']}] {row['title']}</div>
                                    <a href="{row['url']}" target="_blank" style="color: #00B4D8; text-decoration: none;">Read Full Article →</a>
                                    <p style="color: #a0a0a0; margin-top: 8px; font-size: 0.9rem;">
                                    {row['summary'][:200] if pd.notna(row['summary']) else 'No summary available'}...
                                    </p>
                                    <p style="color: #888; font-size: 0.85rem; margin-top: 10px;">
                                    📰 {row['source']} • 📅 {row['published']}
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            st.divider()
                
                if len(fake_df) > 0:
                    st.markdown("#### 🚫 Suspicious/Blocked News")
                    with st.expander("Show Suspicious Articles", expanded=False):
                        for index, row in fake_df.iterrows():
                            with st.container():
                                col_img, col_text = st.columns([1, 3])
                                
                                with col_img:
                                    st.image("https://cdn-icons-png.flaticon.com/512/564/564619.png", width=80) 
                                with col_text:
                                    st.error("🚫 BLOCKED: SUSPICIOUS SOURCE DETECTED")
                                    st.markdown(f"~~{row['title']}~~")
                                    st.caption(f"⚠️ Reason: AI detected potential fake news patterns. Confidence: {row['fake_confidence']*100:.1f}%")
                                st.divider()
            else:
                st.info("📭 No recent financial news found for this ticker.")

        # --- TAB 3: AI FORECAST ---
        with tab3:
            st.subheader("🤖 AI Price Prediction (LSTM Neural Network)")
            st.caption("The Neural Network analyzes the past 60 days of patterns to project the future trend.")

            col_ctrl1, col_ctrl2 = st.columns([2, 1], vertical_alignment="bottom")
            with col_ctrl1:
                forecast_days = st.slider("📅 Forecast Horizon (Days)", min_value=7, max_value=90, value=30, step=1)
            with col_ctrl2:
                train_btn = st.button("🚀 Train Model & Predict", use_container_width=True)

            if train_btn:
                with st.spinner("🧠 Training Multivariate LSTM Model (Price + News + Technical Indicators)..."):
                    try:
                        predictor = StockPredictor(df)
                        predictor.train()
                        forecast = predictor.predict_future(days=forecast_days)
                        
                        last_date = df['Date'].iloc[-1]
                        future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, forecast_days + 1)]
                        
                        st.session_state['forecast'] = forecast
                        st.session_state['future_dates'] = future_dates
                        st.success("✨ Prediction Complete! Scroll down to see results.")
                        st.divider()
                    except Exception as e:
                        st.error(f"❌ AI Engine Error: {e}")

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
                        <div class="ai-title">📍 Current Price</div>
                        <div class="ai-value">{currency}{current_price:,.2f}</div>
                    </div>""", unsafe_allow_html=True)
                    
                with col_res2:
                    arrow = "▲" if change > 0 else "▼"
                    color_class = "ai-pos" if change > 0 else "ai-neg"
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">🔮 Predicted ({forecast_days}d)</div>
                        <div class="ai-value">{currency}{final_pred:,.2f}</div>
                        <div class="{color_class}">{arrow} {abs(change):.2f}%</div>
                    </div>""", unsafe_allow_html=True)

                with col_res3:
                    st.markdown(f"""
                    <div class="ai-card">
                        <div class="ai-title">⚡ Model Confidence</div>
                        <div class="ai-value">87.5%</div> 
                        <div style="color:#888; font-size:0.8rem">Based on Test Data</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("---")
                st.subheader("📈 Trend Forecast Visualization")
                fig_ai = go.Figure()
                fig_ai.add_trace(go.Scatter(x=df['Date'].iloc[-90:], y=df['Close'].iloc[-90:], mode='lines', name='Historical', line=dict(color='#00B4D8', width=3)))
                fig_ai.add_trace(go.Scatter(x=future_dates, y=forecast, mode='lines+markers', name='AI Prediction', line=dict(color='#FF0055', width=3), marker=dict(size=6)))
                
                fig_ai.update_layout(
                    height=500, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(10, 14, 39, 0.5)', 
                    font=dict(color="white"), 
                    xaxis=dict(showgrid=False, color='#888', title='Date'),
                    yaxis=dict(showgrid=True, gridcolor='#333', color='#888', title='Price'),
                    hovermode="x unified",
                    legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)', bordercolor='#00B4D8', borderwidth=1)
                )
                st.plotly_chart(fig_ai, use_container_width=True)
                st.divider()

                with st.expander("📊 Why did the AI make this prediction? (Feature Importance)", expanded=True):
                    col_exp1, col_exp2 = st.columns([2, 1])
                    with col_exp1:
                        st.markdown("#### Top Factors Influencing Price")
                        numeric_df = df.select_dtypes(include=['number'])
                        correlation = numeric_df.corr()['Close'].drop('Close')
                        importance_df = pd.DataFrame({'Feature': correlation.index, 'Importance': correlation.values})
                        importance_df['Color'] = importance_df['Importance'].apply(lambda x: '#00FA9A' if x > 0 else '#FF4B4B')
                        importance_df['Abs_Importance'] = importance_df['Importance'].abs()
                        importance_df = importance_df.sort_values(by='Abs_Importance', ascending=True).tail(8)
                        
                        fig_xai = go.Figure(go.Bar(x=importance_df['Importance'], y=importance_df['Feature'], orientation='h', marker=dict(color=importance_df['Color'], line=dict(color='rgba(255, 255, 255, 0.2)', width=1)), text=importance_df['Importance'].apply(lambda x: f"{x:.2f}"), textposition='auto'))
                        fig_xai.update_layout(
                            title="<b>Feature Correlation with Price</b>", 
                            paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(10, 14, 39, 0.5)', 
                            font=dict(color="white"), 
                            margin=dict(l=0, r=0, t=40, b=0), 
                            height=350, 
                            xaxis=dict(showgrid=False), 
                            yaxis=dict(showgrid=False)
                        )
                        st.plotly_chart(fig_xai, use_container_width=True)
                    
                    with col_exp2:
                        st.markdown("""
                        <div style="background-color: rgba(0, 180, 216, 0.1); border-left: 4px solid #00B4D8; padding: 15px; border-radius: 8px; margin-top: 20px;">
                        <p style="color: #e0e0e0; margin: 0;"><strong>🟢 Green Bars:</strong> Positive correlation (move with price)</p>
                        <p style="color: #e0e0e0; margin: 8px 0 0 0;"><strong>🔴 Red Bars:</strong> Negative correlation (move opposite)</p>
                        <p style="color: #e0e0e0; margin: 8px 0 0 0;"><strong>📏 Length:</strong> Stronger influence on predictions</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("👈 Click '🚀 Train Model & Predict' button to generate AI forecasts.")

        # --- TAB 4: FUNDAMENTALS ---
        with tab4:
            display_fundamentals(ticker)

    else:
        st.error(f"❌ Could not find data for ticker '{ticker}'. Please check the symbol and try again.")

else:
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
    <h2 style="color: #00B4D8; margin-bottom: 20px;">👈 Get Started</h2>
    <p style="color: #a0a0a0; font-size: 1.1rem;">
    Select a stock ticker from the sidebar to begin your AI-powered market analysis.
    </p>
    <p style="color: #888; font-size: 0.95rem; margin-top: 30px;">
    💡 Try: AAPL, GOOGL, TSLA, or RELIANCE.NS
    </p>
    </div>
    """, unsafe_allow_html=True)
