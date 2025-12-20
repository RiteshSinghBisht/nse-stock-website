import os
import logging
from nsepython import nsefetch

# --- ABSOLUTE PATH SETUP ---
# This gets the folder where config.py lives (e.g., /Users/ritesh.../nse_automation)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define all file paths relative to BASE_DIR
EXCEL_FILE = os.path.join(BASE_DIR, 'output', 'NSE_Stock_Data.xlsm')
LOG_FILE = os.path.join(BASE_DIR, 'logs', 'nse_data.log')
CHART_PATH = os.path.join(BASE_DIR, 'nifty_chart.png')
ICON_BULL = os.path.join(BASE_DIR, 'Charts', 'Bull.png')
ICON_BEAR = os.path.join(BASE_DIR, 'Charts', 'Bear.png')

# Ensure directories exist
os.makedirs(os.path.dirname(EXCEL_FILE), exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Trading hours (IST)
TRADING_HOURS = {
    'start': '09:15',
    'end': '15:30',
    'frequency': 'hourly'
}

# --- AI AGENT CONFIG ---
# Replace with your actual n8n Webhook URL
N8N_WEBHOOK_URL = "https://rb-21-04-2003.app.n8n.cloud/webhook/562c7120-c504-4664-9b0a-190154334bb4"

# Retry settings
MAX_RETRIES = 3

# --- DYNAMIC TICKER LOGIC ---

def get_nifty50_tickers():
    try:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
        payload = nsefetch(url)
        
        if 'data' in payload:
            live_tickers = [item['symbol'] for item in payload['data'] if item['priority'] == 0]
            if len(live_tickers) >= 50:
                print(f"✅ Successfully fetched {len(live_tickers)} dynamic Nifty 50 tickers.")
                return live_tickers
        print("⚠️ Warning: Dynamic fetch returned incomplete data. Using fallback list.")
    except Exception as e:
        print(f"⚠️ Warning: Could not fetch dynamic Nifty 50 list ({str(e)}). Using fallback list.")

    return [
        "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", 
        "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BHARTIARTL", "BPCL", 
        "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY", 
        "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", 
        "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", 
        "INFY", "ITC", "JSWSTEEL", "KOTAKBANK", "LT", 
        "LTIM", "M&M", "MARUTI", "NESTLEIND", "NTPC", 
        "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", 
        "SHRIRAMFIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL", 
        "TCS", "TECHM", "TITAN", "ULTRACEMCO", "WIPRO"
    ]

TICKERS = get_nifty50_tickers() # Production (Full List)