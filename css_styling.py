# css_styling.py
"""
Central CSS styling module for consistent theming across the StockVision app.
Import this module in any file and call the styling functions.
"""

import streamlit as st

def load_global_css():
    """
    Load global CSS styling for the entire app.
    Call this ONCE at the beginning of main.py
    """
    st.markdown("""
    <style>
    /* ===== ROOT THEME ===== */
    :root {
        --primary-color: #00B4D8;
        --secondary-color: #0077B6;
        --success-color: #00FA9A;
        --danger-color: #FF4B4B;
        --warning-color: #FFB703;
        --dark-bg: #0a0e27;
        --card-bg: #1a2332;
        --border-color: #2d3748;
        --text-primary: #e0e0e0;
        --text-secondary: #a0a0a0;
    }

    /* ===== GLOBAL STYLES ===== */
    body {
        background-color: var(--dark-bg);
        color: var(--text-primary);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* ===== MAIN TITLE ===== */
    h1 {
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800 !important;
        letter-spacing: 1px;
        text-shadow: 0 0 20px rgba(0, 180, 216, 0.3);
        margin-bottom: 30px !important;
    }

    /* ===== HEADERS ===== */
    h2, h3 {
        color: #00B4D8 !important;
        font-weight: 700 !important;
        border-left: 4px solid #00B4D8;
        padding-left: 12px;
        margin-top: 25px;
    }

    h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }

    /* ===== BUTTONS ===== */
    div.stButton > button {
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 180, 216, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 180, 216, 0.5);
        background: linear-gradient(135deg, #0099CC 0%, #006699 100%);
    }

    div.stButton > button:active {
        transform: translateY(0px);
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
        border-bottom: 2px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 20px;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: var(--text-secondary);
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg) !important;
        color: #00B4D8 !important;
        border-bottom: 3px solid #00B4D8;
    }

    .stTabs [aria-selected="false"]:hover {
        background-color: rgba(0, 180, 216, 0.1);
        color: #00B4D8;
    }

    /* ===== INPUT FIELDS ===== */
    input, textarea, select {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        padding: 10px 12px !important;
        transition: all 0.3s ease;
    }

    input:focus, textarea:focus, select:focus {
        border-color: #00B4D8 !important;
        box-shadow: 0 0 10px rgba(0, 180, 216, 0.3) !important;
    }

    /* ===== METRIC CARDS ===== */
    div[data-testid="stMetric"] {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        border-color: #00B4D8;
        box-shadow: 0 8px 20px rgba(0, 180, 216, 0.2);
    }

    div[data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    div[data-testid="stMetricValue"] {
        color: #00B4D8 !important;
        font-weight: 800 !important;
        font-size: 1.6rem !important;
    }

    div[data-testid="stMetricDelta"] {
        color: var(--success-color) !important;
        font-weight: 700 !important;
    }

    /* ===== CARDS (Containers) ===== */
    .card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .card:hover {
        border-color: #00B4D8;
        box-shadow: 0 8px 20px rgba(0, 180, 216, 0.2);
    }

    /* ===== EXPANDER ===== */
    .streamlit-expander {
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        background-color: var(--card-bg) !important;
    }

    [data-testid="stExpander"] button {
        background-color: transparent !important;
        border: none !important;
        color: #00B4D8 !important;
        font-weight: 700 !important;
    }

    [data-testid="stExpander"] button:hover {
        background-color: rgba(0, 180, 216, 0.1) !important;
    }

    /* ===== INFO/SUCCESS/ERROR BOXES ===== */
    .stAlert {
        border-radius: 8px !important;
        border-left: 4px solid !important;
        padding: 15px 20px !important;
        background-color: rgba(0, 0, 0, 0.3) !important;
    }

    .stAlert-info {
        border-left-color: #00B4D8 !important;
        background-color: rgba(0, 180, 216, 0.1) !important;
    }

    .stAlert-success {
        border-left-color: var(--success-color) !important;
        background-color: rgba(0, 250, 154, 0.1) !important;
    }

    .stAlert-error {
        border-left-color: var(--danger-color) !important;
        background-color: rgba(255, 75, 75, 0.1) !important;
    }

    .stAlert-warning {
        border-left-color: var(--warning-color) !important;
        background-color: rgba(255, 183, 3, 0.1) !important;
    }

    /* ===== DIVIDER ===== */
    hr, .stDivider {
        border-color: var(--border-color) !important;
        margin: 25px 0 !important;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background-color: var(--dark-bg);
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] [data-testid="stImage"] {
        margin-bottom: 20px;
    }

    /* ===== SELECTBOX ===== */
    [data-baseweb="select"] {
        background-color: var(--card-bg) !important;
        border-color: var(--border-color) !important;
        border-radius: 6px !important;
    }

    /* ===== SLIDER ===== */
    [data-baseweb="slider"] {
        margin: 20px 0;
    }

    /* ===== DATAFRAME ===== */
    [data-testid="stDataFrame"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    .stDataFrame {
        border-radius: 8px !important;
    }

    /* ===== CAPTION & SMALL TEXT ===== */
    .stCaption {
        color: var(--text-secondary) !important;
    }

    small {
        color: var(--text-secondary) !important;
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--card-bg);
    }

    ::-webkit-scrollbar-thumb {
        background: #00B4D8;
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #0077B6;
    }

    /* ===== LINK STYLING ===== */
    a {
        color: #00B4D8 !important;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 600;
    }

    a:hover {
        color: #00FA9A !important;
        text-decoration: underline;
    }

    /* ===== CODE BLOCK ===== */
    code {
        background-color: rgba(0, 180, 216, 0.1) !important;
        color: #00FA9A !important;
        border-radius: 4px;
        padding: 2px 6px;
        font-size: 0.9em;
    }

    pre {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 15px !important;
    }

    </style>
    """, unsafe_allow_html=True)


def load_card_css():
    """Custom card styling for AI predictions"""
    st.markdown("""
    <style>
    .ai-card {
        background: linear-gradient(135deg, rgba(0, 180, 216, 0.1) 0%, rgba(0, 119, 182, 0.05) 100%);
        border: 1px solid rgba(0, 180, 216, 0.3);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0, 180, 216, 0.1);
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }

    .ai-card:hover {
        border-color: #00B4D8;
        box-shadow: 0 12px 30px rgba(0, 180, 216, 0.25);
        transform: translateY(-5px);
    }

    .ai-title {
        color: #a0a0a0;
        font-size: 0.95rem;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }

    .ai-value {
        color: #00B4D8;
        font-size: 2rem;
        font-weight: 800;
        margin: 10px 0;
    }

    .ai-pos {
        color: #00FA9A;
        font-weight: 700;
        font-size: 1.1rem;
    }

    .ai-neg {
        color: #FF4B4B;
        font-weight: 700;
        font-size: 1.1rem;
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #00B4D8;
        margin: 30px 0 15px 0;
        border-bottom: 2px solid #00B4D8;
        padding-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    </style>
    """, unsafe_allow_html=True)


def load_fundamental_css():
    """Enhanced CSS for fundamental data display"""
    st.markdown("""
    <style>
    /* Fundamental Data Styling */
    .fund-metric {
        background: linear-gradient(135deg, rgba(0, 180, 216, 0.1) 0%, rgba(0, 119, 182, 0.05) 100%);
        border: 1px solid rgba(0, 180, 216, 0.3);
        border-radius: 10px;
        padding: 18px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .fund-metric:hover {
        border-color: #00B4D8;
        box-shadow: 0 8px 20px rgba(0, 180, 216, 0.15);
        transform: translateY(-3px);
    }

    .fund-label {
        color: #a0a0a0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .fund-value {
        color: #00B4D8;
        font-size: 1.6rem;
        font-weight: 800;
    }

    .fund-header {
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 1.8rem;
        font-weight: 800;
        margin-bottom: 20px;
    }

    .financial-statement {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        overflow: hidden;
    }

    .financial-statement tbody tr:hover {
        background-color: rgba(0, 180, 216, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)


def load_news_css():
    """Enhanced CSS for news section"""
    st.markdown("""
    <style>
    .news-container {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }

    .news-container:hover {
        border-color: #00B4D8;
        box-shadow: 0 8px 20px rgba(0, 180, 216, 0.15);
    }

    .news-title {
        color: #00B4D8;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }

    .news-source {
        color: #a0a0a0;
        font-size: 0.9rem;
    }

    .sentiment-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        margin-right: 10px;
    }

    .sentiment-positive {
        background-color: rgba(0, 250, 154, 0.2);
        color: #00FA9A;
        border: 1px solid #00FA9A;
    }

    .sentiment-negative {
        background-color: rgba(255, 75, 75, 0.2);
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
    }

    .sentiment-neutral {
        background-color: rgba(255, 183, 3, 0.2);
        color: #FFB703;
        border: 1px solid #FFB703;
    }
    </style>
    """, unsafe_allow_html=True)


def load_chart_css():
    """Enhanced CSS for charts and graphs"""
    st.markdown("""
    <style>
    .chart-container {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }

    .chart-title {
        color: #00B4D8;
        font-weight: 700;
        font-size: 1.2rem;
        margin-bottom: 20px;
        border-bottom: 2px solid #00B4D8;
        padding-bottom: 10px;
    }

    /* Plotly chart styling */
    .plotly-graph-div {
        border-radius: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)
