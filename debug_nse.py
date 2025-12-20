from nsepython import nse_quote, nse_eq
import json

symbol = "RELIANCE"

print(f"--- Debugging Data Fetch for {symbol} ---")

try:
    # Attempt 1: Using nse_quote
    print("\n1. Testing nse_quote():")
    data_quote = nse_quote(symbol)
    print(f"Type: {type(data_quote)}")
    print(f"Raw Output: {data_quote}")

except Exception as e:
    print(f"nse_quote failed: {e}")

try:
    # Attempt 2: Using nse_eq (Alternative function)
    print("\n2. Testing nse_eq():")
    data_eq = nse_eq(symbol)
    print(f"Type: {type(data_eq)}")
    # Print only keys to avoid spamming the console if it's a huge JSON
    if isinstance(data_eq, dict):
        print(f"Keys found: {list(data_eq.keys())}")
        if 'priceInfo' in data_eq:
            print(f"Price Info: {data_eq['priceInfo']}")
    else:
        print(f"Raw Output: {data_eq}")

except Exception as e:
    print(f"nse_eq failed: {e}")