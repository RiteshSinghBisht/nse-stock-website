import pandas as pd
from nse_fetcher import get_nifty_data
import yfinance as yf

print("--- Testing get_nifty_data() ---")
prices, is_bearish = get_nifty_data()
print(f"Is Bearish: {is_bearish}")
print(f"Data Type: {type(prices)}")
print(f"Empty: {prices.empty if isinstance(prices, (pd.DataFrame, pd.Series)) else 'N/A'}")

if not prices.empty:
    print("\n--- Head ---")
    print(prices.head())
    print("\n--- Tail ---")
    print(prices.tail())
    print("\n--- Index ---")
    print(prices.index)
else:
    print("Prices series is empty!")
    
    # Deep dive if empty
    print("\n--- Raw Download Check ---")
    df = yf.download("^NSEI", period="1d", interval="5m", progress=False, auto_adjust=True)
    print("Raw Columns:", df.columns)
    print("Raw Head:", df.head())
