import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

def load_fundamental_css():
    st.markdown("""
        <style>
        /* 1. Metric Cards */
        div[data-testid="stMetric"] {
            background-color: #181818;
            border: 1px solid #333;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.2s ease-in-out;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: #4CAF50;
        }
        div[data-testid="stMetricLabel"] {
            color: #B0B0B0 !important;
            font-size: 0.9rem !important;
        }
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            font-size: 1.4rem !important;
        }
        /* 2. Section Headers */
        .section-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #4CAF50;
            margin-top: 20px;
            margin-bottom: 10px;
            border-bottom: 1px solid #333;
            padding-bottom: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

def get_fundamental_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    def safe_get(key, default="N/A"):
        return info.get(key, default)

    # --- High-Res Logo Logic (Still needed for the Main Header) ---
    website = safe_get("website")
    logo_url = ""
    
    if website and website != "N/A":
        logo_url = f"https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url={website}&size=256"
    else:
        logo_url = f"https://ui-avatars.com/api/?name={ticker}&background=random&size=256&bold=true"

    return {
        "info": info,
        "income_stmt": stock.financials,
        "balance_sheet": stock.balance_sheet,
        "cash_flow": stock.cashflow,
        "calendar": stock.calendar,
        "dividends": stock.dividends,
        "name": safe_get("longName", ticker),
        "summary": safe_get("longBusinessSummary"),
        "sector": safe_get("sector"),
        "industry": safe_get("industry"),
        "website": website,
        "logo_url": logo_url,
        "market_cap": safe_get("marketCap"),
        "forward_pe": safe_get("forwardPE"),
        "trailing_pe": safe_get("trailingPE"),
        "peg_ratio": safe_get("pegRatio"),
        "price_to_book": safe_get("priceToBook"),
        "dividend_yield": safe_get("dividendYield"),
        "roe": safe_get("returnOnEquity"),
        "roa": safe_get("returnOnAssets"),
        "debt_to_equity": safe_get("debtToEquity"),
        "eps": safe_get("trailingEps"),
    }

def display_fundamentals(ticker):
    try:
        load_fundamental_css()
        data = get_fundamental_data(ticker)
        currency_symbol = "₹" if ticker.endswith(".NS") or ticker.endswith(".BO") else "$"

        # --- UPDATED: Removed Duplicate Header Section ---
        # The tab now starts directly with the Business Description
        
        with st.expander("📖 Business Description", expanded=False):
            st.write(data['summary'])
        
        st.markdown('<div class="section-header">📊 Key Financial Ratios</div>', unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        # Helper to format large numbers
        def format_large(num):
            if num == "N/A" or num is None: return "N/A"
            if isinstance(num, (int, float)):
                if num > 1e12: return f"{num/1e12:.2f}T"
                if num > 1e9: return f"{num/1e9:.2f}B"
                if num > 1e6: return f"{num/1e6:.2f}M"
                return f"{num:.2f}"
            return str(num)

        kpi1.metric("Market Cap", f"{currency_symbol}{format_large(data['market_cap'])}")
        kpi1.metric("Forward P/E", data['forward_pe'] if data['forward_pe'] != "N/A" else "N/A")
        kpi2.metric("EPS (TTM)", f"{currency_symbol}{data['eps']}" if data['eps'] != "N/A" else "N/A")
        kpi2.metric("PEG Ratio", data['peg_ratio'])
        kpi3.metric("ROE", f"{data['roe']*100:.2f}%" if data['roe'] != "N/A" and data['roe'] is not None else "N/A")
        kpi3.metric("ROA", f"{data['roa']*100:.2f}%" if data['roa'] != "N/A" and data['roa'] is not None else "N/A")
        kpi4.metric("Debt-to-Equity", data['debt_to_equity'])
        kpi4.metric("Book Value", data['price_to_book'])

        st.divider()

        # --- SECTION 3: FINANCIAL STATEMENTS ---
        st.markdown('<div class="section-header">📑 Financial Statements</div>', unsafe_allow_html=True)
        tab_inc, tab_bal, tab_cf = st.tabs(["💵 Income Statement", "⚖️ Balance Sheet", "🌊 Cash Flow"])
        
        with tab_inc:
            if not data['income_stmt'].empty:
                df_inc = data['income_stmt'].T.iloc[:3]
                fig = go.Figure(data=[
                    go.Bar(name='Total Revenue', x=df_inc.index, y=df_inc.get('Total Revenue', [0]*3), marker_color='#2E86C1'),
                    go.Bar(name='Net Income', x=df_inc.index, y=df_inc.get('Net Income', [0]*3), marker_color='#28B463')
                ])
                fig.update_layout(barmode='group', height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(data['income_stmt'], height=300)
            else:
                st.info("No Income Statement data available.")

        with tab_bal:
            if not data['balance_sheet'].empty:
                 st.dataframe(data['balance_sheet'], height=400)
            else:
                st.info("No Balance Sheet data available.")

        with tab_cf:
            if not data['cash_flow'].empty:
                st.dataframe(data['cash_flow'], height=400)
            else:
                 st.info("No Cash Flow data available.")

        st.divider()

        # --- SECTION 4: ACTIONS & CALENDAR ---
        col_div, col_cal = st.columns(2)
        with col_div:
            st.markdown('<div class="section-header">💰 Dividends</div>', unsafe_allow_html=True)
            if not data['dividends'].empty:
                st.line_chart(data['dividends'], color="#4CAF50")
            else:
                st.info("No dividend history.")

        with col_cal:
            st.markdown('<div class="section-header">📅 Earnings Calendar</div>', unsafe_allow_html=True)
            if data['calendar']:
                try:
                    cal_df = pd.DataFrame(data['calendar'])
                    st.dataframe(cal_df, use_container_width=True)
                except:
                    st.write(data['calendar'])
            else:
                 st.info("No upcoming earnings dates found.")

    except Exception as e:
        st.error(f"Could not fetch fundamental data: {e}")