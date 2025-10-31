import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import math

def get_data(ticker):

    tk = yf.Ticker(f"{ticker}.NS")
    data = tk.history(period='10y', interval='1d')
    data = data.drop(columns=['Stock Splits', 'Dividends'])
    return data

def detect_double_tops(df,
                       price_col="Close",
                       window=15,
                       min_sep=5,
                       max_sep=90,
                       tolerance=0.01,
                       min_drop=0.03,
                       lookahead=30):
    """
    Returns a list of detected double-top candidate dicts.
    Parameters:
      - window: local maxima window (symmetric)
      - min_sep/max_sep: min/max bars between peaks
      - tolerance: allowed relative difference between peaks
      - min_drop: required % drop below neckline to consider breakdown
      - lookahead: bars after p2 to search for breakdown
    """
    prices = df[price_col].values
    n = len(prices)
    peaks = []
    # find local maxima (simple approach)
    for i in range(window, n-window):
        slice_win = prices[i-window:i+window+1]
        if prices[i] == slice_win.max() and prices[i] > prices[i-1] and prices[i] > prices[i+1]:
            peaks.append(i)
    patterns = []
    for i, p1 in enumerate(peaks):
        for p2 in peaks[i+1:]:
            sep = p2 - p1
            if sep < min_sep or sep > max_sep:
                continue
            trough_rel = np.argmin(prices[p1:p2+1])
            trough = p1 + trough_rel
            p1p, p2p, trp = prices[p1], prices[p2], prices[trough]
            rel_diff = abs(p1p - p2p) / max(p1p, p2p)
            if rel_diff > tolerance:
                continue
            if not (trp < p1p and trp < p2p):
                continue
            breakdown_price = trp * (1 - min_drop)
            breakdown_idx = None
            end_idx = min(n, p2 + lookahead + 1)
            for j in range(p2+1, end_idx):
                if prices[j] <= breakdown_price:
                    breakdown_idx = j
                    break
            confirmed = breakdown_idx is not None
            patterns.append({
                "p1_idx": p1,
                "p2_idx": p2,
                "trough_idx": trough,
                "p1_date": df.index[p1],
                "p2_date": df.index[p2],
                "trough_date": df.index[trough],
                "p1_price": float(p1p),
                "p2_price": float(p2p),
                "trough_price": float(trp),
                "rel_diff": float(rel_diff),
                "breakdown_idx": breakdown_idx,
                "breakdown_date": (df.index[breakdown_idx] if breakdown_idx is not None else None),
                "confirmed": confirmed
            })
    return patterns

tickers = [
    # Nifty 50
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",
    "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "ETERNAL",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY",
    "ITC", "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT",
    "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC",
    "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SHRIRAMFIN",
    "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO",
    # Nifty Next 50
    "ABB", "ADANIENSOL", "ADANIGREEN", "ADANIPOWER", "AMBUJACEM",
    "BAJAJHLDNG", "BAJAJHFL", "BANKBARODA", "BPCL", "BRITANNIA",
    "BOSCHLTD", "CANBK", "CGPOWER", "CHOLAFIN", "DABUR",
    "DIVISLAB", "DLF", "DMART", "GAIL", "GODREJCP",
    "HAVELLS", "HAL", "HYUNDAI", "ICICIGI", "ICICIPRULI",
    "INDHOTEL", "IOC", "INDIGO", "NAUKRI", "IRFC",
    "JINDALSTEL", "JSWENERGY", "LICI", "LODHA", "LTIM",
    "PIDILITIND", "PFC", "PNB", "RECLTD", "MOTHERSON",
    "SHREECEM", "SIEMENS", "SWIGGY", "TATAPOWER", "TORNTPHARM",
    "TVSMOTOR", "UNITDSPR", "VBL", "VEDL", "ZYDUSLIFE"
]


data_for_tickers = [get_data(t) for t in tickers]
results = [detect_double_tops(df) for df in data_for_tickers]
summary = []

for index, company_results in enumerate(results):
    true_count = 0
    false_count = 0
    
    if company_results:
        for result in company_results:
            if result.get('confirmed', False):
                true_count += 1
            else:
                false_count += 1
        
        summary.append({
            "Company": tickers[index],
            "True_Count": true_count,
            "False_Count": false_count
        })
    else:
        summary.append({
            "Company": tickers[index],
            "True_Count": 0,
            "False_Count": 0
        })

df_summary = pd.DataFrame(summary)
total_true = df_summary['True_Count'].values.sum()
total_false = df_summary['False_Count'].values.sum()
totaldetections = total_true + total_false
probtrue = total_true/totaldetections
probfalse = total_false/totaldetections
print(f"Total detections: {totaldetections}")
print(f"Total true detections: {total_true} and Probability of true detection: {probtrue}")
print(f"Total false detections: {total_false} and Probability of false detection: {probfalse}")