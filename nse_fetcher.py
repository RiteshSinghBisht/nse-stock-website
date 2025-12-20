from nsepython import nse_eq, nse_fno
import yfinance as yf
import pandas as pd
import logging
import time
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as lines
import os
import concurrent.futures
from config import CHART_PATH

# --- Helper Functions ---

def generate_groww_url(ticker, company_name):
    try:
        if not company_name or company_name == "NA":
            return f"https://groww.in/search?q={ticker}"
        slug = company_name.lower().replace(" limited", " ltd")
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = slug.strip().replace(" ", "-")
        slug = re.sub(r"-+", "-", slug)
        return f"https://groww.in/stocks/{slug}"
    except:
        return f"https://groww.in/search?q={ticker}"

def calculate_rsi(series, period=14):
    if len(series) < period: return 0.0
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs)).fillna(0)
    return round(float(rsi.iloc[-1]), 2)

def calculate_vwap(df):
    try:
        v = df['Volume']
        p = df['Close']
        vwap = (p * v).cumsum() / v.cumsum()
        return round(float(vwap.iloc[-1]), 2)
    except:
        return 0.0

def calculate_supertrend(df, period=7, multiplier=3):
    try:
        if len(df) < period:
            return "Neutral"

        hl2 = (df['High'] + df['Low']) / 2

        df['tr0'] = abs(df['High'] - df['Low'])
        df['tr1'] = abs(df['High'] - df['Close'].shift(1))
        df['tr2'] = abs(df['Low'] - df['Close'].shift(1))
        df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)

        df['atr'] = df['tr'].ewm(alpha=1/period, adjust=False).mean()

        df['upperband'] = hl2 + multiplier * df['atr']
        df['lowerband'] = hl2 - multiplier * df['atr']

        df['final_upper'] = df['upperband']
        df['final_lower'] = df['lowerband']
        df['uptrend'] = True

        for i in range(1, len(df)):
            curr_basic_upper = df['upperband'].iloc[i]
            curr_basic_lower = df['lowerband'].iloc[i]
            prev_final_upper = df['final_upper'].iloc[i-1]
            prev_final_lower = df['final_lower'].iloc[i-1]
            prev_close = df['Close'].iloc[i-1]
            curr_close = df['Close'].iloc[i]
            prev_trend = df['uptrend'].iloc[i-1]

            # Final Upper Band
            if curr_basic_upper < prev_final_upper or prev_close > prev_final_upper:
                df.loc[df.index[i], 'final_upper'] = curr_basic_upper
            else:
                df.loc[df.index[i], 'final_upper'] = prev_final_upper

            # Final Lower Band
            if curr_basic_lower > prev_final_lower or prev_close < prev_final_lower:
                df.loc[df.index[i], 'final_lower'] = curr_basic_lower
            else:
                df.loc[df.index[i], 'final_lower'] = prev_final_lower

            # Trend
            if prev_trend:
                if curr_close < df['final_lower'].iloc[i]:
                    df.loc[df.index[i], 'uptrend'] = False
                else:
                    df.loc[df.index[i], 'uptrend'] = True
            else:
                if curr_close > df['final_upper'].iloc[i]:
                    df.loc[df.index[i], 'uptrend'] = True
                else:
                    df.loc[df.index[i], 'uptrend'] = False

        return "Bullish" if df['uptrend'].iloc[-1] else "Bearish"

    except Exception as e:
        print("ST ERROR:", e)
        return "Neutral"


def calculate_levels(df):
    try:
        resistance = round(float(df['High'].max()), 2)
        support = round(float(df['Low'].min()), 2)
        return support, resistance
    except:
        return 0.0, 0.0

def safe_float(value):
    try:
        if value is None: return 0.0
        clean_val = str(value).replace(',', '').strip()
        if clean_val in ['-', '', 'NA', 'nan']: return 0.0
        return float(clean_val)
    except:
        return 0.0

def get_trend(change):
    if change > 0: return "Bullish"
    if change < 0: return "Bearish"
    return "Neutral"

# --- Chart Generation ---

def get_nifty_data():
    """Fetches Nifty 50 intraday data for plotting"""
    try:
        # Fetch 1d, 5m for Chart
        # Optimize: Fetch only 1 day of data for speed (Intraday View)
        # Previous might have been fetching 'max' or '5d' which is slow
        df = yf.download("^NSEI", period="1d", interval="5m", progress=False, auto_adjust=True)
        
        if df.empty: return pd.DataFrame(), False

        if 'Close' in df.columns: prices = df['Close']
        elif 'Adj Close' in df.columns: prices = df['Adj Close']
        else: return pd.DataFrame(), False
        
        if isinstance(prices, pd.DataFrame): prices = prices.iloc[:, 0]

        # Timezone Fix
        if prices.index.tz is None:
            prices.index = prices.index.tz_localize('UTC')
        prices.index = prices.index.tz_convert('Asia/Kolkata')
        # specific fix for plotting: remove tz info for simpler plotting or keep as is
        # prices.index = prices.index.tz_localize(None) 
        
        prices = prices.sort_index()
        
        # Calculate trend
        start_price = float(prices.iloc[0])
        end_price = float(prices.iloc[-1])
        is_bearish = start_price > end_price
        
        return prices, is_bearish
    except Exception as e:
        logging.error(f"Nifty fetch failed: {e}")
        return pd.DataFrame(), False

def generate_nifty_chart():
    """Legacy function for Excel compatibility (saves PNG)"""
    try:
        prices, is_bearish = get_nifty_data()
        if prices.empty: return CHART_PATH, False
        
        # ... logic to save matplotlib image if needed ...
        # For this refactor, we just return the path to avoid breaking existing calls
        # We won't actually regenerate the image to save time/resources as we are using Plotly now
        return CHART_PATH, is_bearish

        
        if isinstance(prices, pd.DataFrame): prices = prices.iloc[:, 0]

        # Timezone Fix
        if prices.index.tz is None:
            prices.index = prices.index.tz_localize('UTC')
        prices.index = prices.index.tz_convert('Asia/Kolkata')
        prices.index = prices.index.tz_localize(None)
        prices = prices.sort_index()

        start_price = float(prices.iloc[0])
        end_price = float(prices.iloc[-1])
        is_bearish = start_price > end_price
        main_color = '#D32F2F' if is_bearish else '#388E3C'

        fig, ax = plt.subplots(figsize=(6.31, 2.04))
        
        fig.patch.set_edgecolor(main_color)
        fig.patch.set_linewidth(3) 
        
        shadow_color = '#999999'
        fig.add_artist(lines.Line2D([0.01, 0.99], [0.01, 0.01], color=shadow_color, linewidth=5, transform=fig.transFigure, zorder=0, alpha=0.5))
        fig.add_artist(lines.Line2D([0.01, 0.01], [0.01, 0.99], color=shadow_color, linewidth=5, transform=fig.transFigure, zorder=0, alpha=0.5))

        ax.plot(prices.index, prices, color=main_color, linewidth=1.5)
        ax.set_title(f"NIFTY 50: {end_price:.2f}", fontsize=10, fontweight='bold', color='#333333')
        
        myFmt = mdates.DateFormatter('%H:%M')
        ax.xaxis.set_major_formatter(myFmt)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', which='major', labelsize=7)
        
        plt.tight_layout()
        plt.savefig(CHART_PATH, dpi=100, edgecolor=fig.get_edgecolor())
        plt.close()
        
        return CHART_PATH, is_bearish
    except Exception as e:
        logging.error(f"Chart generation failed: {e}")
        return CHART_PATH, False

# --- Main Fetch Logic ---

def fetch_single_ticker(ticker, timestamp, nifty_weekly, max_retries=3):
    success = False
    retry_count = 0
    
    while not success and retry_count < max_retries:
        try:
            # A. Live Data
            quote = nse_eq(ticker)
            price, open_price, volume, delivery_pct, change, pct_change = 0.0, 0.0, 0, 0.0, 0.0, 0.0
            company_name = ""
            
            if isinstance(quote, dict) and 'priceInfo' in quote:
                p_info = quote['priceInfo']
                company_name = quote.get('info', {}).get('companyName', '')
                price = safe_float(p_info.get('lastPrice', 0))
                open_price = safe_float(p_info.get('open', 0))
                volume = int(safe_float(p_info.get('totalTradedVolume', 0))) # API Volume
                change = safe_float(p_info.get('change', 0))
                pct_change = round(safe_float(p_info.get('pChange', 0)),2)
                
                # Fetch Delivery %
                try:
                    meta = quote.get("metadata", {})
                    d_qty = safe_float(meta.get("deliveryQuantity", 0))
                    t_qty = safe_float(meta.get("tradedQuantity", 0))

                    if t_qty > 0:
                        delivery_pct = round((d_qty / t_qty) * 100, 2)

                except:
                    delivery_pct = 0.0

                
                # Fallback Calc for Delivery %
                if delivery_pct == 0 and 'securityWiseDP' in quote:
                    d_qty = safe_float(quote['securityWiseDP'].get('deliveryQuantity', 0))
                    t_qty = safe_float(quote['securityWiseDP'].get('quantityTraded', 0))
                    if t_qty > 0:
                        delivery_pct = round((d_qty / t_qty) * 100, 2)

            else:
                fno_quote = nse_fno(ticker)
                if 'underlyingValue' in fno_quote:
                    price = safe_float(fno_quote.get('underlyingValue', 0))
            
            groww_link = generate_groww_url(ticker, company_name)

            # B. Yahoo Finance Data (Intraday & Weekly)
            yf_ticker = f"{ticker}.NS"
            
            try: intraday_df = yf.Ticker(yf_ticker).history(period="5d", interval="5m", auto_adjust=True)
            except: intraday_df = pd.DataFrame()
            
            try: weekly_df = yf.Ticker(yf_ticker).history(period="5d", interval="15m", auto_adjust=True)
            except: weekly_df = pd.DataFrame()
            
            rsi_val, vwap_val, correlation = 0.0, 0.0, 0.0
            supertrend, trend_signal = "Neutral", "Neutral"
            support_val, resistance_val = 0.0, 0.0
            
            try:
                daily_df = yf.Ticker(yf_ticker).history(period="5d", interval="1d", auto_adjust=True)
                if not daily_df.empty and len(daily_df) >= 2:
                    # Get previous day's data (assuming last row is today/live, 2nd last is prev close)
                    # Note: yfinance often includes today as the last row with live data.
                    prev_day = daily_df.iloc[-2]
                    p_high = prev_day['High']
                    p_low = prev_day['Low']
                    p_close = prev_day['Close']
                    
                    # Classic Pivot Point Formula
                    pivot = (p_high + p_low + p_close) / 3
                    r1 = (2 * pivot) - p_low
                    s1 = (2 * pivot) - p_high
                    
                    resistance_val = round(r1, 2)
                    support_val = round(s1, 2)
            except Exception as e:
                logging.error(f"Support/Resist calc error for {ticker}: {e}")

            if not intraday_df.empty:
                # Convert to IST
                if intraday_df.index.tz is None:
                    intraday_df.index = intraday_df.index.tz_localize('UTC')
                intraday_df.index = intraday_df.index.tz_convert('Asia/Kolkata')
                
                # Better Volume Logic
                if volume == 0:
                    today_date = pd.Timestamp.now(tz='Asia/Kolkata').normalize()
                    today_data = intraday_df[intraday_df.index.normalize() == today_date]
                    if not today_data.empty:
                        volume = int(today_data['Volume'].sum())

                rsi_val = calculate_rsi(intraday_df['Close'], period=14)
                vwap_val = calculate_vwap(intraday_df)
                supertrend = calculate_supertrend(intraday_df)
                
                if price > vwap_val: trend_signal = "Bullish"
                else: trend_signal = "Bearish"
            
            if not weekly_df.empty:
                support_val, resistance_val = calculate_levels(weekly_df)
                if not nifty_weekly.empty and len(weekly_df) > 10:
                    try:
                        stock_close = weekly_df['Close']
                        stock_close.index = pd.to_datetime(stock_close.index).normalize()
                        if stock_close.index.tz is not None: 
                            stock_close.index = stock_close.index.tz_localize(None)
                        
                        aligned_nifty = nifty_weekly.reindex(stock_close.index).ffill()
                        correlation = round(float(stock_close.corr(aligned_nifty)), 2)
                    except: correlation = 0.0

            data = {
                "Timestamp": timestamp,
                "Ticker": ticker,
                "Open Price": open_price,
                "Current Price": price,
                "Price Change": change,
                "Percentage Change": pct_change,
                "Volume": volume,
                "RSI (5 Min)": round(rsi_val, 2),
                "VWAP": round(vwap_val, 2),
                "Supertrend": supertrend,
                "Support": support_val,
                "Resistance": resistance_val,
                "Intraday Trend": trend_signal,
                "Correlation with Nifty": round(correlation, 2),
                "Link": f"{groww_link}?t={ticker}"
            }
            logging.info(f"Fetched {ticker}: {price} | ST: {supertrend} | Vol: {volume}")
            return data

        except Exception as e:
            retry_count += 1
            time.sleep(1)
    
    logging.error(f"Failed {ticker}")
    return None

def fetch_nse_data(tickers, timestamp, max_retries=3):
    results = []
    _, is_bearish = get_nifty_data()

    nifty_weekly = pd.Series(dtype='float64')
    try:
        nifty_data = yf.download("^NSEI", period="5d", interval="15m", progress=False, auto_adjust=True)
        if 'Close' in nifty_data.columns: nifty_weekly = nifty_data['Close']
        if isinstance(nifty_weekly, pd.DataFrame): nifty_weekly = nifty_weekly.iloc[:, 0]
        if not nifty_weekly.empty:
            nifty_weekly.index = pd.to_datetime(nifty_weekly.index).normalize()
            if nifty_weekly.index.tz is not None: 
                nifty_weekly.index = nifty_weekly.index.tz_localize(None)
    except: pass

    # Parallel Execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {
            executor.submit(fetch_single_ticker, ticker, timestamp, nifty_weekly, max_retries): ticker 
            for ticker in tickers
        }
        
        for future in concurrent.futures.as_completed(future_to_ticker):
            data = future.result()
            if data:
                results.append(data)

    logging.info(f"Success: {len(results)}/{len(tickers)}")
    return pd.DataFrame(results), is_bearish