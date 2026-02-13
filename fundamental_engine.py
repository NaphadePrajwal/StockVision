import yfinance as yf
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from css_styling import load_fundamental_css

def get_fundamental_data(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    
    def safe_get(key, default="N/A"):
        return info.get(key, default)

    # --- High-Res Logo Logic ---
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

        # --- Business Description ---
        with st.expander("📖 Business Description", expanded=False):
            if data['summary'] and data['summary'] != "N/A":
                st.markdown(f"""
                <p style="color: #e0e0e0; line-height: 1.6; font-size: 0.95rem;">
                {data['summary']}
                </p>
                """, unsafe_allow_html=True)
            else:
                st.info("No business summary available for this company.")
        
        # --- Key Financial Metrics Section ---
        st.markdown('<div class="section-header">📊 Key Financial Metrics</div>', unsafe_allow_html=True)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        # Helper to format large numbers
        def format_large(num):
            if num == "N/A" or num is None: 
                return "N/A"
            if isinstance(num, (int, float)):
                if num > 1e12: 
                    return f"{num/1e12:.2f}T"
                if num > 1e9: 
                    return f"{num/1e9:.2f}B"
                if num > 1e6: 
                    return f"{num/1e6:.2f}M"
                return f"{num:.2f}"
            return str(num)

        # Market Cap
        with kpi1:
            st.markdown("""
            <div class="fund-metric">
                <div class="fund-label">📈 Market Cap</div>
                <div class="fund-value">%s</div>
            </div>
            """ % f"{currency_symbol}{format_large(data['market_cap'])}", unsafe_allow_html=True)
        
        # Forward P/E
        with kpi1:
            forward_pe = data['forward_pe'] if data['forward_pe'] != "N/A" else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">📊 Forward P/E</div>
                <div class="fund-value">{forward_pe}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # EPS
        with kpi2:
            eps_val = f"{currency_symbol}{data['eps']}" if data['eps'] != "N/A" else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">💰 EPS (TTM)</div>
                <div class="fund-value">{eps_val}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # PEG Ratio
        with kpi2:
            peg = data['peg_ratio'] if data['peg_ratio'] != "N/A" else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">📈 PEG Ratio</div>
                <div class="fund-value">{peg}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ROE
        with kpi3:
            roe_val = f"{data['roe']*100:.2f}%" if data['roe'] != "N/A" and data['roe'] is not None else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">💹 ROE</div>
                <div class="fund-value">{roe_val}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # ROA
        with kpi3:
            roa_val = f"{data['roa']*100:.2f}%" if data['roa'] != "N/A" and data['roa'] is not None else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">📊 ROA</div>
                <div class="fund-value">{roa_val}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Debt-to-Equity
        with kpi4:
            dte = data['debt_to_equity'] if data['debt_to_equity'] != "N/A" else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">⚖️ D/E Ratio</div>
                <div class="fund-value">{dte}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # P/B Ratio
        with kpi4:
            pb = data['price_to_book'] if data['price_to_book'] != "N/A" else "N/A"
            st.markdown(f"""
            <div class="fund-metric">
                <div class="fund-label">📕 P/B Ratio</div>
                <div class="fund-value">{pb}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # --- FINANCIAL STATEMENTS SECTION ---
        st.markdown('<div class="section-header">💼 Financial Statements</div>', unsafe_allow_html=True)
        tab_inc, tab_bal, tab_cf = st.tabs(["💵 Income Statement", "⚖️ Balance Sheet", "💧 Cash Flow"])
        
        with tab_inc:
            if not data['income_stmt'].empty:
                st.subheader("Annual Income Statement")
                df_inc = data['income_stmt'].T.iloc[:5]
                
                # Create revenue and net income visualization
                fig = go.Figure(data=[
                    go.Bar(
                        name='Total Revenue', 
                        x=df_inc.index, 
                        y=df_inc.get('Total Revenue', [0]*5),
                        marker=dict(color='rgba(0, 180, 216, 0.8)', line=dict(color='#00B4D8', width=1))
                    ),
                    go.Bar(
                        name='Net Income', 
                        x=df_inc.index, 
                        y=df_inc.get('Net Income', [0]*5), 
                        marker=dict(color='rgba(0, 250, 154, 0.8)', line=dict(color='#00FA9A', width=1))
                    )
                ])
                fig.update_layout(
                    barmode='group', 
                    height=400, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(10, 14, 39, 0.5)',
                    font=dict(color='#e0e0e0'),
                    xaxis_title='Fiscal Year',
                    yaxis_title='Amount (USD)',
                    hovermode='x unified',
                    legend=dict(bgcolor='rgba(0,0,0,0.5)', bordercolor='#00B4D8', borderwidth=1)
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                <div style="background-color: rgba(0, 180, 216, 0.1); border-radius: 8px; padding: 15px; margin: 20px 0;">
                """, unsafe_allow_html=True)
                st.dataframe(data['income_stmt'], height=300, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("📭 No Income Statement data available.")

        with tab_bal:
            if not data['balance_sheet'].empty:
                st.subheader("Annual Balance Sheet")
                st.markdown("""
                <div style="background-color: rgba(0, 180, 216, 0.1); border-radius: 8px; padding: 15px;">
                """, unsafe_allow_html=True)
                st.dataframe(data['balance_sheet'], height=400, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("📭 No Balance Sheet data available.")

        with tab_cf:
            if not data['cash_flow'].empty:
                st.subheader("Annual Cash Flow")
                st.markdown("""
                <div style="background-color: rgba(0, 180, 216, 0.1); border-radius: 8px; padding: 15px;">
                """, unsafe_allow_html=True)
                st.dataframe(data['cash_flow'], height=400, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("📭 No Cash Flow data available.")

        st.divider()

        # --- DIVIDENDS & EARNINGS CALENDAR ---
        col_div, col_cal = st.columns(2)
        
        with col_div:
            st.markdown('<div class="section-header">💰 Dividend History</div>', unsafe_allow_html=True)
            if not data['dividends'].empty:
                fig_div = go.Figure()
                fig_div.add_trace(go.Bar(
                    x=data['dividends'].index,
                    y=data['dividends'].values,
                    marker=dict(color='#00FA9A', line=dict(color='#00B4D8', width=1)),
                    name='Dividend'
                ))
                fig_div.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(10, 14, 39, 0.5)',
                    font=dict(color='#e0e0e0'),
                    xaxis_title='Date',
                    yaxis_title='Dividend Amount',
                    hovermode='x unified'
                )
                st.plotly_chart(fig_div, use_container_width=True)
            else:
                st.info("📭 No dividend history available.")

        with col_cal:
            st.markdown('<div class="section-header">📅 Earnings Calendar</div>', unsafe_allow_html=True)
            if data['calendar']:
                try:
                    st.markdown(f"""
                    <div style="background-color: rgba(0, 180, 216, 0.1); border-left: 4px solid #00B4D8; padding: 15px; border-radius: 8px;">
                    <p style="color: #e0e0e0; margin: 0;"><strong>📌 Next Earnings:</strong></p>
                    """, unsafe_allow_html=True)
                    
                    cal_data = pd.DataFrame(data['calendar'].items(), columns=['Event', 'Date'])
                    st.dataframe(cal_data, use_container_width=True, hide_index=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                except:
                    st.write(data['calendar'])
            else:
                st.info("📭 No upcoming earnings dates found.")

    except Exception as e:
        st.error(f"❌ Could not fetch fundamental data: {e}")
