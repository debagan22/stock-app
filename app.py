import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Initialize session state
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = time.time()
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'failed' not in st.session_state:
    st.session_state.failed = 0

st.set_page_config(page_title="NIFTY 50 LIVE", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 50 RSI + MA SCANNER")
st.markdown("**4 Charts + LIVE COUNTDOWN | Auto + Manual Refresh**")

# NIFTY 50 stocks
nifty50 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "INFY.NS", "LICI.NS", "HINDUNILVR.NS", "MARUTI.NS",
    "M&M.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SUNPHARMA.NS", "ITC.NS", "HCLTECH.NS",
    "ULTRACEMCO.NS", "TITAN.NS", "ADANIPORTS.NS", "NTPC.NS", "ONGC.NS", "BEL.NS",
    "BAJAJFINSV.NS", "ASIANPAINT.NS", "NESTLEIND.NS", "TECHM.NS", "POWERGRID.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "WIPRO.NS",
    "COALINDIA.NS", "TATACONSUM.NS", "GRASIM.NS", "DIVISLAB.NS", "LTIM.NS",
    "DRREDDY.NS", "CIPLA.NS", "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    "BRITANNIA.NS", "APOLLOHOSP.NS", "TRENT.NS", "VARUNBEV.NS"
]

@st.cache_data(ttl=300)
def scan_nifty50():
    results = []
    failed = 0
    
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            if len(data) < 20:
                failed += 1
                continue
            
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            if rsi < 35 and price > ma20:
                signal = "🟢 STRONG BUY"
            elif rsi > 65 and price < ma20:
                signal = "🔴 STRONG SELL"
            elif rsi < 30:
                signal = "🟢 BUY"
            elif rsi > 70:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.1f}",
                'Signal': signal
            })
            time.sleep(0.5)
        except:
            failed += 1
    
    return pd.DataFrame(results), failed

# 🔥 CONTROL BUTTONS
col1, col2 = st.columns([3,1])
with col1:
    if st.button("🔥 MANUAL SCAN NOW", type="primary", use_container_width=True):
        df, failed = scan_nifty50()
        st.session_state.df = df
        st.session_state.failed = failed
        st.session_state.last_scan = time.ti
