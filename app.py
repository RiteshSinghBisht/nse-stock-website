
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import pytz
import time
import base64
from config import TICKERS
from nse_fetcher import fetch_nse_data, get_nifty_data
import os
import numpy as np # Added for safety

# --- Page Configuration ---
st.set_page_config(
    page_title="NSE Market Overview",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Theme Management ---
# 1. Initialize Default
if 'theme' not in st.session_state:
    st.session_state.theme = 'Light'

# 2. Check URL for Theme Override (Source of Truth)
# STRICTLY FORCE LIGHT MODE for now as per user request
url_theme = "Light" # st.query_params.get("theme")
if url_theme in ['Light']:
    st.session_state.theme = 'Light'

# 3. Persist Theme in Query Params (Optional but good for reloading)
# If the URL doesn't match the session (e.g. after a button click), sync it?
# Actually, for this specific issues, we just accept the URL or Session.

# Removed simple toggle function, using checkbox logic inline
# def toggle_theme():
#     st.session_state.theme = 'Dark' if st.session_state.theme == 'Light' else 'Light'

# --- Custom CSS for Corporate Minimalist Design ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #f8f9fa;
        color: #1e293b;
    }

    /* --- BACKGROUND STYLING (Light Mode) --- */
    .stApp {
        /* Base: Minimal Light Blue/Grey */
        background-color: #f8f9fa !important; 
        /* "Dark in up corners" effect: Subtle radial gradients at top-left/right */
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(30, 41, 59, 0.08), transparent 25%), 
            radial-gradient(circle at 100% 0%, rgba(30, 41, 59, 0.08), transparent 25%) !important;
        background-attachment: fixed !important;
    }

    /* --- SMOOTH THEME TRANSITION --- */
    /* Target all major color-changing elements */
    .stApp, 
    .stPlotlyChart, 
    div[data-testid="stMetric"],
    div[data-testid="stDataFrame"], /* Re-enabled for smoothness */
    h1, h2, h3, p {
        /* transition removed as per user request */
    }
    
    /* Header Styling - Force Dark Text */
    h1, h2, h3, h4, h5, h6, .stMarkdown p {
        color: #0f172a !important; 
        font-weight: 700;
    }
    
    /* Ensure all main text is dark regardless of theme settings */
    .stApp, .stMarkdown, .stText {
        color: #0f172a !important;
    }
    
    /* KPI Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    
    /* --- SCROLL REVEAL ANIMATION (Apple Style) --- */
    .scroll-reveal {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        will-change: opacity, transform;
    }
    
    .scroll-active {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #475569; /* Slightly darker slate for better contrast */
        font-size: 1rem !important; /* Increased from 0.85rem */
        font-weight: 600 !important;
        text-transform: capitalize; /* changed from uppercase for friendlier look or keep uppercase? User wants visual good. Let's keep distinct. */
        letter-spacing: 0.02em;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; /* Large, readable values */
        font-weight: 700 !important;
        color: #0f172a;
    }
    
    /* Table Styling (LIGHT MODE DEFAULT) */
    div[data-testid="stDataFrame"] {
        background-color: #ffffff !important; /* Explicit White Background */
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        /* overflow: hidden; Removed to ensure Toolbar (CSV, Fullscreen) is visible */
    }
    
    /* Strict Left Alignment and Header Styling */
    thead tr th {
        text-align: left !important;
        background-color: #f1f5f9 !important; /* Light gray background */
        color: #000000 !important; /* Black text */
        font-weight: 800 !important; /* Bold */
        font-size: 1rem !important;
    }
    [data-testid="stDataFrame"] td, 
    [data-testid="stDataFrame"] div[role="columnheader"], 
    [data-testid="stDataFrame"] div[role="gridcell"] {
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        color: #0f172a !important; /* Main Text Color */
    }
    
    /* Force Row Background White in Light Mode */
    [data-testid="stDataFrame"] div[role="row"] {
        background-color: #ffffff !important;
        color: #0f172a !important;
    }
    
    /* Table Header Styling - Light Grey - AGGRESSIVE OVERRIDE */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] div[role="columnheader"],
    [data-testid="stDataFrame"] div[role="row"]:first-child,
    [data-testid="stDataFrame"] [data-testid="glide-header"],
    [data-testid="stDataFrame"] header {
        background-color: #e2e8f0 !important; /* DISTINCT Light Grey */
        color: #0f172a !important; /* Dark Text */
        font-weight: 700 !important;
        border-bottom: 2px solid #cbd5e1 !important; /* Stronger header separator */
    }
    
    /* Force all cells within header row to be light */
    [data-testid="stDataFrame"] div[role="columnheader"] * {
        background-color: transparent !important;
        color: #0f172a !important;
    }
    
    /* Chart Section */
    .stPlotlyChart {
        background-color: white;
        border-radius: 12px;
        padding: 10px;
        border: 2px solid #000000 !important; /* Thicker black border */
        overflow: hidden; /* Fix: Ensure content doesn't cover rounded corners */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    /* Hover Animation for KPI Card - Removed as per user request (issues with border) */
    /* .stPlotlyChart:hover { transform: scale(1.02); ... } */
    
    /* Liquid Glass Button (Apple Style) - REMOVED */
    /* div[data-testid="stButton"] button { ... } */
    
    /* Force Light Hover on Table Rows for Readability */
    [data-testid="stDataFrame"] div[role="row"]:hover {
        background-color: #f1f5f9 !important; /* Very light subtle grey */
    }
    /* Ensure text color stays readable on hover */
    [data-testid="stDataFrame"] div[role="row"]:hover div {
        color: #0f172a !important;
    }
    
    /* Disable Selection/Focus Visuals (User requested to remove double-click behavior) */
    [data-testid="stDataFrame"] [aria-selected="true"] {
        background-color: transparent !important; 
        color: inherit !important;
    }
    [data-testid="stDataFrame"] [data-canvas-focus="true"] {
        display: none !important; /* Hide focus ring/ghost element entirely */
    }
    
    /* --- CUSTOM TOGGLE SWITCH (Dribbble Style) --- */
    /* Target the st.toggle component specifically */
    
    /* The Track */
    div[data-testid="stToggle"] {
        width: 60px !important;
    }
    
    label[data-testid="stWidgetLabel"] {
        display: none;
    }
    
    div[data-testid="stToggle"] p {
        display: none; /* Hide label text if it leaks */
    }

    /* The Slider Track */
    div[data-testid="stToggle"] div[role="presentation"] {
        background: linear-gradient(to right, #818cf8, #4f46e5) !important;
        height: 30px !important;
        width: 60px !important;
        border-radius: 30px !important;
        border: none !important;
    }
    
    /* The thumb (circle) inside the track */
    /* Streamlit toggle thumb is usually an internal div or span */
    div[data-testid="stToggle"] div[role="presentation"] > div {
        background-color: white !important;
        color: transparent !important; /* Hide default icon if any */
        height: 24px !important;
        width: 24px !important;
        border-radius: 50% !important;
        top: 3px !important;
        left: 3px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important;
    }
    
    /* ADD SUN ICON to the thumb via ::after */
    div[data-testid="stToggle"] div[role="presentation"] > div::after {
        content: '☀️';
        font-size: 16px;
        color: black; /* Sun color */
        display: block;
        opacity: 1;
    }

    /* DARK MODE STATE (Checked) */
    /* When checked, Streamlit moves the thumb. We need to style the track and thumb for Dark Mode */
    
    /* Use :has selector or aria-checked if possible. 
       Streamlit toggle structure: input[type="checkbox"]:checked + div 
    */
    
    /* In Dark Mode (based on class or state), styling changes: */
    /* We can target specific overriding styles if we know the state */
    
    /* Actually with st.toggle, the checked state styling is handled by Streamlit moving the thumb.
       We just need to change the ICON when it moves. */
       
    /* If the toggle is ON (aria-checked="true" on the switch role usually) */
    div[data-testid="stToggle"] div[aria-checked="true"] {
        background-color: #1e293b !important; /* Track color in dark mode */
    }

    div[data-testid="stToggle"] div[aria-checked="true"] > div::after {
        content: '🌙';
        color: black;
    }
    
    /* Force thumb position tweak if needed, but Streamlit handles movement. */
    
    </style>
    """, unsafe_allow_html=True)

# --- Dark Mode Overrides (Disabled for Light Mode Consistency) ---
# Logic removed to streamline Light Mode enforcement and prevent theme conflicts.
# The code block previously here injected dark CSS which clashed with the Force Light setting.

# --- Caching Data Fetch ---
@st.cache_data(show_spinner=False)  # Cache indefinitely until manual reset
def load_data():
    # --- Lottie Loading Overlay (Transparent Blur + Animation) ---
    loading_placeholder = st.empty()
    
    # --- Full Screen Lottie Overlay (Iframe Injection for Script Support) ---
    # We use srcdoc to inject the script AND position the iframe to cover the whole screen.
    # --- CSS Loading Overlay (Zero dependency, instant load) ---
    # Google-style bouncing dots
    loader_html = """
    <style>
        .loader-container {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(15, 23, 42, 0.9); backdrop-filter: blur(15px);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 999999;
        }
        
        /* RADAR SCANNER ANIMATION */
        .radar-spinner {
            width: 80px; height: 80px;
            border-radius: 50%;
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-top-color: #6366f1;
            position: relative;
            animation: spin 1.5s linear infinite;
            box-shadow: 0 0 20px rgba(99, 102, 241, 0.2);
        }
        
        .radar-spinner::before {
            content: '';
            position: absolute; top: 2px; left: 2px; right: 2px; bottom: 2px;
            border-radius: 50%;
            border: 2px solid transparent;
            border-top-color: #818cf8;
            animation: spin 2.5s linear infinite;
        }
        
        .radar-spinner::after {
            content: '';
            position: absolute; top: 8px; left: 8px; right: 8px; bottom: 8px;
            border-radius: 50%;
            border: 2px solid transparent;
            border-top-color: #c7d2fe;
            animation: spin 3.5s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            margin-top: 25px;
            color: #e2e8f0; font-family: 'Inter', sans-serif; font-weight: 500;
            font-size: 18px; letter-spacing: 1px; text-transform: uppercase;
            animation: pulseText 2s infinite ease-in-out;
        }
        
        @keyframes pulseText {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; text-shadow: 0 0 10px rgba(99, 102, 241, 0.5); }
        }
    </style>
    <div class="loader-container">
        <div class="radar-spinner"></div>
        <div class="loading-text">Scanning Market Data...</div>
    </div>
    """
    
    with loading_placeholder:
        st.markdown(loader_html, unsafe_allow_html=True)
    
    # Force refresh on rerun logic if needed, but cache handles usually
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Fetch Data (Animation plays while this runs)
    df, is_bearish = fetch_nse_data(TICKERS, timestamp)
    
    # Clear Animation
    loading_placeholder.empty()
    return df, is_bearish, timestamp

@st.cache_data(show_spinner=False) # Cache chart data indefinitely until manual reset
def load_chart_data():
    return get_nifty_data()

# --- Main App Layout ---


from components.navbar import inject_custom_navbar
from components.ai_assistant import render_ai_assistant
from components.about_us import show_about_us


# --- Trader Onboarding Wizard (Modal -- Auto Trigger) ---
@st.dialog("Trader Mindset")
def trader_onboarding():
    # 1. CSS for Flashy Cards & Animations (LIGHT MODE)
    st.markdown("""
    <style>
        /* Animation Keyframes */
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 40px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }
        
        /* FORCE LIGHT MODAL BACKGROUND */
        div[role="dialog"] {
            background-color: #ffffff !important;
        }
        div[role="dialog"] > div {
            background-color: #ffffff !important;
        }
        
        /* Card Styling for Buttons (LIGHT MODE) */
        div[data-testid="column"] > div > div > div > button, 
        div[data-testid="stColumn"] > div > div > div > button {
            background-color: #f0f2f6 !important; /* Light Grey Card */
            color: #0f172a !important; /* Dark Text */
            border: 1px solid rgba(0, 0, 0, 0.1) !important;
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 10px;
            animation: fadeInUp 0.8s ease-out both;
        }
        
        /* FORCE DARK TEXT IN MODAL */
        div[role="dialog"] h1, 
        div[role="dialog"] h2, 
        div[role="dialog"] h3, 
        div[role="dialog"] p, 
        div[role="dialog"] span, 
        div[role="dialog"] div,
        div[role="dialog"] button {
            color: #0f172a !important;
        }

        /* Generic Hover Transition */
        div[data-testid="column"] > div > div > div > button:hover,
        div[data-testid="stColumn"] > div > div > div > button:hover {
            transform: translateY(-5px);
        }

        /* LEFT COLUMN (Bullish / Safe) -> Light Green Hover */
        div[data-testid="column"]:nth-of-type(1) div[data-testid="stButton"] button:hover,
        div[data-testid="stColumn"]:nth-of-type(1) div[data-testid="stButton"] button:hover {
            background-color: rgba(34, 197, 94, 0.2) !important; 
            border-color: #22c55e !important;
            box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.3), 0 4px 6px -2px rgba(34, 197, 94, 0.15) !important;
        }

        /* RIGHT COLUMN (Bearish / Risky) -> Light Red Hover */
        div[data-testid="column"]:nth-of-type(2) div[data-testid="stButton"] button:hover,
        div[data-testid="stColumn"]:nth-of-type(2) div[data-testid="stButton"] button:hover {
            background-color: rgba(239, 68, 68, 0.2) !important;
            border-color: #ef4444 !important;
            box-shadow: 0 10px 15px -3px rgba(239, 68, 68, 0.3), 0 4px 6px -2px rgba(239, 68, 68, 0.15) !important;
        }
        
        h3 { animation: fadeInUp 0.5s ease-out both; }
        p { animation: fadeInUp 0.6s ease-out both; }
    </style>
    """, unsafe_allow_html=True)

    # Logic: 
    # Step 1: If 'trader_view' is missing, show Market View cards.
    # Step 2: If 'trader_view' is present but 'risk_appetite' is missing, show Risk cards.
    
    # --- Step 1: Market View ---
    if 'trader_view' not in st.session_state:
        st.markdown("### Step 1: Market View 🌍")
        st.caption("How is the market feeling today?")
        
        # Lottie Animation
        components.html(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                <script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.8.5/dist/dotlottie-wc.js" type="module"></script>
                <dotlottie-wc src="https://lottie.host/e6b969ce-85c8-4f5c-a989-1fffcbbf7327/UBnGHEUToc.lottie" style="width: 300px;height: 300px" autoplay loop></dotlottie-wc>
            </div>
            """,
            height=320,
        )
        
        col1, col2 = st.columns(2)
        with col1:
            # Bullish Card
            if st.button("🟢 BULLISH\n\nMarket is trending up", use_container_width=True):
                st.session_state['trader_view'] = "Bullish"
                st.rerun() # Rerun to start Step 2 immediately in the same dialog
        
        with col2:
            # Bearish Card
            if st.button("🔴 BEARISH\n\nMarket is trending down", use_container_width=True):
                st.session_state['trader_view'] = "Bearish"
                st.rerun()


# --- Step 2: Risk Appetite --- (Inside Wizard)
    elif 'risk_appetite' not in st.session_state:
        st.markdown("### Step 2: Risk Appetite ⚠️")
        st.caption(f"You are **{st.session_state['trader_view']}**. How much volatility can you handle?")
        
        # Lottie Animation (Reused)
        components.html(
            """
            <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
                <script src="https://unpkg.com/@lottiefiles/dotlottie-wc@0.8.5/dist/dotlottie-wc.js" type="module"></script>
                <dotlottie-wc src="https://lottie.host/e6b969ce-85c8-4f5c-a989-1fffcbbf7327/UBnGHEUToc.lottie" style="width: 300px;height: 300px" autoplay loop></dotlottie-wc>
            </div>
            """,
            height=320,
        )
        
        col1, col2 = st.columns(2)
        with col1:
            # Safe Card
            if st.button("🛡️ SAFE\n\nTight spreads, low volatility", use_container_width=True):
                st.session_state['risk_appetite'] = "Safe"
                st.session_state['last_filter_date'] = date.today() # Persistent Key
                st.session_state['trigger_scroll'] = True # Trigger Smooth Scroll
                st.rerun() 
        
        with col2:
            # Risky Card
            if st.button("🎢 RISKY\n\nHigh volatility, wide spreads", use_container_width=True):
                st.session_state['risk_appetite'] = "Risky"
                st.session_state['last_filter_date'] = date.today() # Persistent Key
                st.session_state['trigger_scroll'] = True # Trigger Smooth Scroll
                st.rerun()


def show_market_scanners(df):
    st.markdown("### 📊 Global Market Overview")
    
    # Helper for conditional color formatting
    def color_price_change(val):
        try:
            val = float(val)
            color = '#22c55e' if val > 0 else '#ef4444' if val < 0 else 'inherit'
            return f'color: {color}'
        except:
            return ''

    # DYNAMIC TABLE THEMING (Fix for Black/White Table Consistency)
    # DYNAMIC TABLE THEMING (Forced Light Mode)
    table_bg_color = '#ffffff'
    table_text_color = '#0f172a'
    table_border = '1px solid #e2e8f0' # Light Grey Border

    props = {
        'text-align': 'left',
        'background-color': table_bg_color,
        'color': table_text_color,
        'border': table_border # GRID LINES
    }

    # 1. Gainers & Losers
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption("🚀 Top Gainers")
        if not df.empty:
            # Select Data
            gainers = df.nlargest(10, 'Percentage Change')[['Ticker', 'Current Price', 'Percentage Change', 'Price Change']]
            
            # Apply Style
            styled_gainers = gainers.style.set_properties(**props).map(color_price_change, subset=['Price Change', 'Percentage Change'])
            
            st.dataframe(
                styled_gainers,
                hide_index=True,
                use_container_width=True,
                column_config={
                     "Ticker": st.column_config.LinkColumn("Ticker", display_text=r"t=(.*)"),
                     "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
                     "Percentage Change": st.column_config.NumberColumn(format="%.2f%%"),
                     "Price Change": st.column_config.NumberColumn("Change (₹)", format="₹%.2f"),
                }
            )

    with col2:
        st.caption("📉 Top Losers")
        if not df.empty:
            # Select Data
            losers = df.nsmallest(10, 'Percentage Change')[['Ticker', 'Current Price', 'Percentage Change', 'Price Change']]
            
            # Apply Style
            styled_losers = losers.style.set_properties(**props).map(color_price_change, subset=['Price Change', 'Percentage Change'])
            
            st.dataframe(
                styled_losers,
                hide_index=True,
                use_container_width=True,
                column_config={
                     "Ticker": st.column_config.LinkColumn("Ticker", display_text=r"t=(.*)"),
                     "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
                     "Percentage Change": st.column_config.NumberColumn(format="%.2f%%"),
                     "Price Change": st.column_config.NumberColumn("Change (₹)", format="₹%.2f"),
                }
            )
    
    st.markdown("---")

    # Removed Momentum & Volatility as per user request



def show_trader_zone(df):
    # --- Trader Zone Header with Reset Button ---
    tz_col1, tz_col2 = st.columns([6, 1])
    
    with tz_col1:
        st.markdown("## ⚡ Trader Zone")
        st.markdown("Scan the market for high-probability setups.")
        
    with tz_col2:
        # Reset Filters Button (Triggers Onboarding Again)
        st.markdown(
            """
            <style>
            /* ABSOLUTE LOCKDOWN: Reset Filters Button (Re-injecting to ensure scope) */
            div[data-testid="column"] button[kind="primary"] {
                transition: none !important;
                transform: none !important;
                animation: none !important;
                background-image: none !important;
                box-shadow: none !important;
                background-color: #0071e3 !important;
                color: white !important;
                border: 1px solid transparent !important;
            }
            div[data-testid="column"] button[kind="primary"]:hover,
            div[data-testid="column"] button[kind="primary"]:active,
            div[data-testid="column"] button[kind="primary"]:focus {
                transition: none !important;
                transform: none !important;
                animation: none !important;
                background-image: none !important;
                box-shadow: none !important;
                background-color: #0071e3 !important;
                color: white !important;
                border: 1px solid transparent !important;
                outline: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("Reset Filters", type="primary", key="tz_reset_filters_styled", use_container_width=True):
            # Clear Trader Preferences
            if 'trader_view' in st.session_state:
                del st.session_state['trader_view']
            if 'risk_appetite' in st.session_state:
                del st.session_state['risk_appetite']
            if 'last_filter_date' in st.session_state:
                del st.session_state['last_filter_date']
            st.rerun()
    
    # --- Logic Refinement: Auto-Trigger on Trader Page ---
    today = date.today()
    last_check = st.session_state.get('last_filter_date', None)
    
    # Check if preferences are missing or date has changed
    preferences_missing = 'trader_view' not in st.session_state or 'risk_appetite' not in st.session_state
    
    # Auto-Trigger Wizard if data is stale or missing
    if last_check != today or preferences_missing:
        trader_onboarding()
        
        # Stop execution removed to prevent UI disappearance behind modal
        # if preferences_missing: st.stop()
            
    # --- 3. Filter Logic (Defaults if missing) ---
    sentiment_choice = st.session_state.get('trader_view', 'Bullish')
    risk_choice = st.session_state.get('risk_appetite', 'Safe')
    
    # Defaults for rendering (Visual only, don't persist to session state logic)
    # This ensures the Wizard continues to show until the user explicitly chooses.


    # --- Persona Mapping (Professional Avatars) ---
    img_base_path = "assets/images"
    
    persona_map = {
        ("Bullish", "Safe"): {
            "name": "The Visionary",
            "image": f"{img_base_path}/pro_visionary_bull_safe_1765056832988.png",
            "quote": "“The stock market is a device for transferring money from the impatient to the patient.”"
        },
        ("Bullish", "Risky"): {
            "name": "The Momentum Trader",
            "image": f"{img_base_path}/pro_momentum_bull_risky_1765056851937.png",
            "quote": "“Trend is your friend until the end when it bends. Strike hard, strike fast.”"
        },
        ("Bearish", "Safe"): {
            "name": "The Hedge Fund Manager",
            "image": f"{img_base_path}/pro_hedge_manager_bear_safe_1765056871490.png",
            "quote": "“Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1.”"
        },
        ("Bearish", "Risky"): {
            "name": "The Short Seller",
            "image": f"{img_base_path}/pro_short_seller_bear_risky_1765056888285.png",
            "quote": "“Gravity is the only certainty. What goes up must come down.”"
        }
    }

    current_persona = persona_map.get((sentiment_choice, risk_choice), persona_map[("Bullish", "Safe")])

    # --- Persona Card Display (Framed) ---
    st.markdown('<div class="scroll-reveal">', unsafe_allow_html=True)
    with st.container(border=True):
        p_col1, p_col2, p_col3 = st.columns([1, 3, 1])
        
        with p_col1:
            try:
                st.image(current_persona["image"], use_container_width=True)
            except:
                st.markdown("📷") # Fallback
        
        with p_col2:
            st.markdown(f"### {current_persona['name']}")
            st.markdown(f"_{current_persona['quote']}_")
            st.markdown(f"**Status**: {sentiment_choice} | {risk_choice}")

        with p_col3:
            st.markdown("") # Empty placeholder


    
    st.markdown("---")

    # --- Predictive Return Calculator (Margin Based) ---
    st.markdown("### 💰 Capital & Leverage")

    # 1. Capital Input & Margin Info
    cap_col1, cap_col2 = st.columns([1, 1])
    
    with cap_col1:
        my_capital = st.number_input("My Capital (₹)", value=10000, step=5000)
    
    with cap_col2:
        buying_power = my_capital * 4
        st.markdown(f"""
        <div style="background-color: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; padding: 10px; border-radius: 8px; text-align: center;">
            <span style="color: #15803d; font-weight: 700; font-size: 0.9rem;">Broker Margin: 4x</span><br>
            <span style="color: #16a34a; font-weight: 800; font-size: 1.2rem;">Buying Power: ₹{buying_power:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)

    # --- Filtering the Data ---
    filtered_df = df.copy()
    
    # A. View Filter (Intraday Trend)
    if 'Intraday Trend' in filtered_df.columns:
        if sentiment_choice == "Bullish":
            filtered_df = filtered_df[filtered_df['Intraday Trend'].str.contains("Bullish", case=False, na=False)]
        else:
            filtered_df = filtered_df[filtered_df['Intraday Trend'].str.contains("Bearish", case=False, na=False)]
    
    # B. Ensure Numeric Columns
    cols = ['Resistance', 'Support', 'Current Price']
    for c in cols:
        if c in filtered_df.columns:
             filtered_df[c] = pd.to_numeric(filtered_df[c], errors='coerce')
    
    if all(c in filtered_df.columns for c in cols):
        # Calculate Spread
        filtered_df['Spread %'] = (filtered_df['Resistance'] - filtered_df['Support']) / filtered_df['Current Price']
        
        # --- REBUILT TRADER ZONE LOGIC (Spec-Based) ---
        
        # 1. Leveraged Quantity (Floor Division)
        # Avoid division by zero
        filtered_df = filtered_df[filtered_df['Current Price'] > 0]
        filtered_df['Leveraged Qty'] = (buying_power / filtered_df['Current Price']).astype(int)
        
        # 2. Targets & Estimated Profit
        if sentiment_choice == "Bullish":
            # Target = Resistance
            filtered_df['Achieved Price'] = filtered_df['Resistance']
            
            # Profit = (Target - Current) * Qty
            filtered_df['Estimated Profit'] = (filtered_df['Achieved Price'] - filtered_df['Current Price']) * filtered_df['Leveraged Qty']
            # Zero out negative profit (wrong view)
            filtered_df.loc[filtered_df['Estimated Profit'] < 0, 'Estimated Profit'] = 0
            
            # Risk Amount = Profit * 0.10
            filtered_df['Stop Loss (Risk)'] = filtered_df['Estimated Profit'] * 0.10
            
        else: # Bearish
            # Target = Support
            filtered_df['Achieved Price'] = filtered_df['Support']
            
            # Profit = (Current - Target) * Qty
            filtered_df['Estimated Profit'] = (filtered_df['Current Price'] - filtered_df['Achieved Price']) * filtered_df['Leveraged Qty']
            # Zero out negative profit
            filtered_df.loc[filtered_df['Estimated Profit'] < 0, 'Estimated Profit'] = 0
            
            # Risk Amount = Profit * 0.10
            filtered_df['Stop Loss (Risk)'] = filtered_df['Estimated Profit'] * 0.10

        # 3. Use Existing Link from Data Source (User Preferred Method)
        # This preserves the specific slug format (e.g. stocks/hcl-technologies-ltd?t=HCLTECH)
        if 'Link' in filtered_df.columns:
            filtered_df['Ticker'] = filtered_df['Link']
        
        # 4. Sort by 'Spread %' (Risk/Reward proxy)
        if risk_choice == "Risky":
            target_stocks = filtered_df.nlargest(15, 'Spread %')
        else:
            target_stocks = filtered_df.nsmallest(15, 'Spread %')
            
        # 5. Display Configuration
        if not target_stocks.empty:
             st.subheader(f"🎯 {risk_choice} {sentiment_choice} (Power: ₹{buying_power:,.0f})")
             
             display_cols = ['Ticker', 'Current Price', 'Leveraged Qty', 'Achieved Price', 'Estimated Profit', 'Stop Loss (Risk)']
             
             # Conditional Formatting using Styler
             def color_profit_loss(s):
                 if s.name == 'Estimated Profit':
                     return ['color: #16a34a; font-weight: bold'] * len(s) # Green
                 elif s.name == 'Stop Loss (Risk)':
                     return ['color: #ef4444; font-weight: bold'] * len(s) # Red
                 else:
                     return [''] * len(s)

             # FORCE LIGHT MODE TABLE PROPS (Matching Navbar)
             # Exclude Ticker from color styling so Links look like Links
             props = {
                 'text-align': 'left',
                 'background-color': '#ffffff',
                 'color': '#0f172a',
                 'border': '1px solid #e2e8f0'
             }
             
             subset_cols = [c for c in display_cols if c != 'Ticker']

             styled_res = target_stocks[display_cols].style.set_properties(**props, subset=subset_cols).apply(color_profit_loss, axis=0)
             
             st.dataframe(
                styled_res,
                use_container_width=True,
                hide_index=True,
                column_config={
                     "Ticker": st.column_config.LinkColumn("Ticker", display_text=r"t=(.*)", width="small"),
                     "Current Price": st.column_config.NumberColumn(format="₹%.2f"),
                     "Achieved Price": st.column_config.NumberColumn("Est. Achieved Price", format="₹%.2f"),
                     "Estimated Profit": st.column_config.NumberColumn("Estimated Profit 🚀", format="₹%.2f"),
                     "Stop Loss (Risk)": st.column_config.NumberColumn("Stop Loss Risk ⚠️", format="₹%.2f"),
                }
            )
        else:
            st.info("No stocks match your strict criteria today.")
    else:
        st.error("Essential data (Support/Resistance) missing for calculation.")

    st.markdown("---")
    



def show_home_dashboard(df, is_bearish, fetch_time):
    # Top Layout: Left (Info), Right (Chart)
    top_left, top_right = st.columns([3, 2])

    with top_left:
        # Header
        h_col1, h_col2 = st.columns([3, 1])
        with h_col1:
            st.title("NSE Market Overview")
            st.markdown(f"**Live Market Intelligence** | {datetime.now().strftime('%A, %d %B %Y')}")
            st.markdown(
                """
                <a href="/?page=trader_zone" target="_self" style="text-decoration: none; color: #667eea; font-weight: 500; font-size: 0.95rem;">
                    ℹ️ Tip: Use Trader Zone for stock deep calculation related to profit and loss.
                </a>
                """,
                unsafe_allow_html=True
            )
            st.caption("Disclaimer: This tool provides reference based on data. Please take advice from your advisor before investing.")
        with h_col2:
            pass # Theme Toggle Button - HIDDEN AS PER USER REQUEST
        
    with top_right:
        chart_df, chart_bearish = load_chart_data()
        
        # Calculate Nifty Header String for Chart Title
        nifty_title = "Nifty 50"
        
        if not chart_df.empty:
            if chart_df.index.tz is not None:
                chart_df.index = chart_df.index.tz_localize(None)

            # User Logic: Use Opening Price (First point of day) and Now Price
            current_nifty = chart_df.iloc[-1]
            open_nifty = chart_df.iloc[0] # Approximation of 'Open' from the series
            
            nifty_change_val = current_nifty - open_nifty
            nifty_change_pct = (nifty_change_val / open_nifty) * 100
            
            # Dynamic Title
            arrow = "▼" if nifty_change_pct < 0 else "▲"
            sign = "" if nifty_change_pct < 0 else "+"
            nifty_title_text = f"NIFTY 50: {current_nifty:.2f} ({sign}{nifty_change_pct:.2f}%)"
            
            # Conditional Styling (Green if +, Red if -)
            is_positive = nifty_change_pct >= 0
            line_color = '#22c55e' if is_positive else '#ef4444' # Green / Red
            fill_color = 'rgba(34, 197, 94, 0.1)' if is_positive else 'rgba(239, 68, 68, 0.1)'
            
            # Select Template based on Theme
            chart_template = 'plotly_dark' if st.session_state.theme == 'Dark' else 'plotly_white'
            chart_bg = '#0e1117' if st.session_state.theme == 'Dark' else 'white'
            # Conditional Title Color
            title_text_color = '#22c55e' if is_positive else '#ef4444' # Green if profit, Red if loss

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=chart_df.index,
                y=chart_df.values,
                mode='lines',
                line=dict(color=line_color, width=2),
                fill='tozeroy',
                fillcolor=fill_color,
                hovertemplate='%{y:.2f}'
            ))
            
            y_min = chart_df.min()
            y_max = chart_df.max()
            padding = (y_max - y_min) * 0.1
            if padding == 0: padding = y_max * 0.01

            grid_col = '#334155' if st.session_state.theme == 'Dark' else '#f1f5f9'
            
            fig.update_layout(
                template=chart_template,
                title=dict(
                    text=nifty_title_text,
                    font=dict(size=20, family="Inter, sans-serif", weight="bold", color=title_text_color),
                    x=0.0,
                    y=0.95
                ),
                height=180, # Increased Height
                margin=dict(l=15, r=15, t=30, b=15),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor=chart_bg,
                hovermode='x', 
                xaxis=dict(
                    visible=True, 
                    showgrid=False,
                    tickformat='%H:%M' # Show Time on X-Axis
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor=grid_col,
                    range=[y_min - padding, y_max + padding],
                    visible=True
                ),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("Chart data currently unavailable.")

    st.markdown("---")
    
    # KPIs (Full Width Row) - wrapped in Scroll Reveal
    st.markdown('<div class="scroll-reveal">', unsafe_allow_html=True)
    st.markdown("### Market Pulse")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    # Top Gainer logic
    if not df.empty:
        top_gainer = df.loc[df['Percentage Change'].idxmax()]
        kpi1.metric(
            label="🚀 Top Gainer",
            value=f"{top_gainer['Ticker']}",
            delta=f"+{top_gainer['Percentage Change']}%"
        )

        top_loser = df.loc[df['Percentage Change'].idxmin()]
        kpi2.metric(
            label="📉 Top Loser",
            value=f"{top_loser['Ticker']}",
            delta=f"{top_loser['Percentage Change']}%",
            delta_color="normal"
        )
    
    sentiment_text = "Bearish" if is_bearish else "Bullish"
    # User provided images
    bear_img_path = "assets/images/dashboard_bear.png"
    bull_img_path = "assets/images/dashboard_bull.png"
    
    selected_img_path = bear_img_path if is_bearish else bull_img_path
    
    def get_base64_image(image_path):
        if os.path.exists(image_path):
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        return ""

    img_b64 = get_base64_image(selected_img_path)
    trend_signal = "Momentum" 

    label_color = "rgba(250, 250, 250, 0.6)" if st.session_state.theme == 'Dark' else "rgba(49, 51, 63, 0.6)"
    momentum_color = "#22c55e" if not is_bearish else "#ef4444"

    html_kpi = f"""
    <div data-testid="stMetric" class="stMetric" style="display: flex; flex-direction: column; align-items: flex-start;">
        <label data-testid="stMetricLabel" style="font-size: 14px; color: {label_color}; margin-bottom: 4px;">📊 Market Sentiment</label>
        <div style="display: flex; align-items: center; gap: 8px;">
            <img src="data:image/png;base64,{img_b64}" width="45" style="border-radius: 4px;">
            <div data-testid="stMetricValue" style="font-size: 30px; font-weight: 700;">{sentiment_text}</div>
        </div>
        <div data-testid="stMetricDelta" style="font-size: 14px; color: {momentum_color}; margin-top: 4px;">{trend_signal}</div>
    </div>
    """
    
    with kpi3:
         st.markdown(html_kpi, unsafe_allow_html=True)

    kpi4.metric(
        label="Last Update",
        value=fetch_time.split(" ")[1],
        delta="Real-time"
    )
    st.markdown('</div>', unsafe_allow_html=True) # Close KPI scroll-reveal

    # Define columns for Filter/Header and Refresh Button
    t_col1, t_col2 = st.columns([6, 1])

    with t_col1:
        st.markdown('<div class="scroll-reveal">', unsafe_allow_html=True)
        st.markdown("### NSE Top 50 Stocks")
            
    with t_col2:
        # Apple-Style Reset Data Button
        # We target this specific button within this column layout for specificity
        
        st.markdown(
            """
            <style>
            /* ABSOLUTE LOCKDOWN: Reset Data Button */
            /* Target by attribute to ensure specificity overrides Streamlit defaults */
            div[data-testid="column"] button[kind="primary"] {
                transition: none !important;
                transform: none !important;
                animation: none !important;
                background-image: none !important;
                box-shadow: none !important;
                background-color: #0071e3 !important; /* Standard Apple Blue */
                color: white !important;
                border: 1px solid transparent !important;
            }
            
            /* KILL HOVER EFFECTS */
            div[data-testid="column"] button[kind="primary"]:hover {
                transition: none !important;
                transform: none !important;
                animation: none !important;
                background-image: none !important;
                box-shadow: none !important;
                background-color: #0071e3 !important; /* Keep same color */
                color: white !important;
                border: 1px solid transparent !important;
            }

            /* KILL ACTIVE/FOCUS EFFECTS */
            div[data-testid="column"] button[kind="primary"]:active,
            div[data-testid="column"] button[kind="primary"]:focus,
            div[data-testid="column"] button[kind="primary"]:focus-visible {
                transition: none !important;
                transform: none !important;
                animation: none !important;
                background-image: none !important;
                box-shadow: none !important;
                background-color: #0071e3 !important;
                color: white !important;
                outline: none !important;
                border: 1px solid transparent !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("Reset Data", type="primary", key="reset_data_absolute_fix", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 1. Handle Volume Display (0 -> "--")
    if 'Volume' in df.columns:
        # Create a display copy for the dashboard to avoid messing up numeric for other views if shared
        # But here df is local to this render, so it's okay BUT wait
        # If we convert to string here, we break numeric sorting if user clicks column header
        # Best to let st.dataframe handle formatting via column_config, but logic below does string conversion
        df['Volume'] = df['Volume'].apply(lambda x: "--" if x == 0 else f"{int(x):,}")

    # HYPERLINK LOGIC
    if 'Link' in df.columns:
        df['Ticker'] = df['Link']

    cols_to_drop = ['Timestamp', 'Link', 'Support (5 Days)']
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')

    # Removed Legacy String Conversion Logic to prevent 'nlargest' TypeError in subsequent calls
    # All formatting is now handled via st.column_config below, keeping df numeric.

    # DYNAMIC TABLE THEMING (Fix for Black Table in Light Mode)
    # We explicitly pass colors to Pandas Styler, which overrides Streamlit's default canvas theme.
    # DYNAMIC TABLE THEMING (Forced Light Mode)
    table_bg_color = '#ffffff'
    table_text_color = '#0f172a'
    table_border = '1px solid #e2e8f0'

    styled_df = df.style.set_properties(**{
        'text-align': 'left',
        'background-color': table_bg_color,
        'color': table_text_color,
        'border': table_border
    })
    
    if 'RSI (5 Min)' in df.columns:
        # RSI Bar Color (Light Indigo) - This specific subset overrides the global property above
        df['RSI (5 Min)'] = df['RSI (5 Min)'].fillna(0).astype(int)
    
    # Apply Bar Chart to RSI
    styled_df = styled_df.bar(subset=['RSI (5 Min)'], align='zero', color='#818cf8', vmin=0, vmax=100)

    def color_vals(val):
        try:
            clean_str = str(val).replace('₹','').replace('%','').replace(',','')
            clean_val = float(clean_str)
            color = '#22c55e' if clean_val > 0 else '#ef4444' if clean_val < 0 else 'inherit' # Modern Green/Red
            return f'color: {color}'
        except:
            return ''

    styled_df = styled_df.map(color_vals, subset=['Percentage Change', 'Price Change'])

    st.dataframe(
        styled_df,
        column_order=(
            "Ticker", "Open Price", "Current Price", "VWAP", 
            "Support", "Resistance",
            "Percentage Change", "Price Change", 
            "Correlation with Nifty", "RSI (5 Min)", "Supertrend", "Volume",
            "Intraday Trend"
        ),
        column_config={
            "Ticker": st.column_config.LinkColumn(
                "Ticker", 
                help="Click to view on Groww", 
                display_text=r"t=(.*)"
            ),
            "Open Price": st.column_config.NumberColumn("Open", format="₹%.2f"),
            "Current Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "VWAP": st.column_config.NumberColumn("VWAP", format="₹%.2f"),
            "Support": st.column_config.NumberColumn("Support", format="₹%.2f"),
            "Resistance": st.column_config.NumberColumn("Resist", format="₹%.2f"),
            "Correlation with Nifty": st.column_config.NumberColumn("Nifty Corr", format="%.2f"),
            "Percentage Change": st.column_config.NumberColumn("Change %", format="%.2f%%"),
            "Price Change": st.column_config.NumberColumn("Change ₹", format="₹%.2f"),
            "Volume": st.column_config.TextColumn("Volume"),
            "RSI (5 Min)": st.column_config.NumberColumn("RSI", format="%d"), 
            "Supertrend": st.column_config.TextColumn("Supertrend"),
            "Intraday Trend": st.column_config.TextColumn("Trend"),
        },
        use_container_width=True, 
        hide_index=True,
        height=600
    )
    st.markdown('</div>', unsafe_allow_html=True) # Close Table scroll-reveal



    st.markdown("---")
    # Append Scanners to Home Dashboard (Restored)
    show_market_scanners(df)
    
    # Info Tip (Moved from Trader Zone)
    st.info("ℹ️ **Tip**: Use Trader Zone for stock deep calculation related to profit and loss.")
    



def main():
    inject_custom_navbar()
    
    # --- Scroll Reveal JS Injection ---
    components.html(
        """
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const observerOptions = {
                    threshold: 0.1,
                    rootMargin: "0px"
                };

                const observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('scroll-active');
                            observer.unobserve(entry.target);
                        }
                    });
                }, observerOptions);

                function attachObserver() {
                    const elements = window.parent.document.querySelectorAll('.scroll-reveal');
                    elements.forEach(el => observer.observe(el));
                }

                setTimeout(attachObserver, 500); 

                const observerMutation = new MutationObserver(() => {
                    attachObserver();
                });
                
                observerMutation.observe(window.parent.document.body, { childList: true, subtree: true });
            });
        </script>
        """,
        height=0,
        width=0
    )

    # 1. Load Data
    with st.spinner('Analyzing market data...'):
        df, is_bearish, fetch_time = load_data()
        
    # Store for AI Assistant context
    if not df.empty:
        st.session_state['latest_market_data'] = df

    if df.empty:
        st.error("Market data unavailable. Please check connection.")
        return

    # Process Numeric Columns
    numeric_cols = ['Open Price', 'Current Price', 'Price Change', 'Percentage Change', 'RSI (5 Min)', 'VWAP', 'Correlation with Nifty', 'Volume', 'High', 'Low']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')


    # --- Multi-Page Routing ---
    page = st.query_params.get("page", "home")
    
    if page == "trader_zone":
        show_trader_zone(df)
    elif page == "about_us":
        show_about_us()
    else:
        show_home_dashboard(df, is_bearish, fetch_time)
        
    # --- Floating AI Assistant ---
    render_ai_assistant()

if __name__ == "__main__":
    main()
