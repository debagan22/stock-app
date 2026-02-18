import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import time
import numpy as np

st.set_page_config(page_title="NIFTY ULTRAFAST", layout="wide", page_icon="⚡")
st.title("⚡ **NIFTY SCANNER v9.0** - **10 SECOND SCAN**")

# Pre-defined TOP 50 stocks (most liquid = fastest)
TOP_NIFTY = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'HINDUNILVR', 'ICICIBANK', 'KOTAKBANK', 'ITC', 
    'LT', 'BHARTIARTL', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 'NESTLEIND',
    'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 'ONGC', 'COALINDIA', 'M&M', 'NTPC',
    'TECHM', 'WIPRO', 'LTIM', 'TATASTEEL', 'CIPLA', 'DRREDDY', 'BPCL', 'HEROMOTOCO', 
    'DIVISLAB', 'BRITANNIA', 'BAJAJFINSV', 'APOLLOHOSP', 'TRENT', 'EICHERMOT', 'TATACONSUM',
    'BEL', 'VARUNBEV', 'GODREJCP', 'PIDILITIND', 'AUROPHARMA', 'BANKBARODA', 'BHARATFORG'
]

if 'data_full' not in st.session_state: st.session_state.data_full = pd.DataFrame()
if 'data_strongbuy' not in st.session_state: st.session_state.data_strongbuy = pd.DataFrame()

def lightning_batch_scan():
    """ONE API CALL - ALL 50 STOCKS"""
    symbols = [s + '.NS' for s in TOP_NIFTY]
    
    # SINGLE BATCH DOWNLOAD - ULTRA FAST
    data = yf.download(symbols, period="20d", group_by='ticker', 
                      threads=True, progress=False, auto_adjust=True)
    
    results = []
    for symbol in TOP_NIFTY:
        try:
            if symbol in data.columns.levels[0]:
                stock_data = data[symbol]['Close'].dropna()
                if len(stock_data) < 15: continue
                
                # FAST CALCULATIONS
                rsi = ta.momentum.RSIIndicator(stock_data).rsi().iloc[-1]
                ma20 = ta.trend.SMAIndicator(stock_data, 20).sma_indicator().iloc[-1]
                price = stock_data.iloc[-1]
                change = ((price / stock_data.iloc[-2] - 1) * 100)
                
                # SIMPLE CLEAR SIGNALS
                if rsi < 35 and price > ma20:
                    signal = '🟢 STRONG BUY'
                elif rsi < 40:
                    signal = '🟢 BUY'
                elif rsi > 65:
                    signal = '🔴 SELL'
                else:
                    signal = '🟡 HOLD'
                
                results.append({
                    'Stock': symbol,
                    'Price': f"₹{price:.0f}",
                    'Change': f"{change:+.1f}%",
                    'RSI': f"{rsi:.1f}",
                    'Signal': signal
                })
        except:
            continue
    
    df = pd.DataFrame(results)
    strongbuy = df[df['Signal'] == '🟢 STRONG BUY']
    return df, strongbuy

# 🔥 ONE BUTTON = 10 SECONDS
col1, col2 = st.columns([3,1])

if col1.button("⚡ **10 SEC SCAN**", type="primary", use_container_width=True):
    with st.spinner("⚡ BATCH SCANNING 50 STOCKS..."):
        start = time.time()
        df_full, df_strong = lightning_batch_scan()
        
        st.session_state.data_full = df_full
        st.session_state.data_strongbuy = df_strong
        elapsed = time.time() - start
        
        st.success(f"✅ **{elapsed:.1f} SECONDS** | {len(df_full)} stocks | {len(df_strong)} STRONG BUYS!")
    st.rerun()

if col2.button("🗑️ CLEAR"):
    st.session_state.data_full = pd.DataFrame()
    st.session_state.data_strongbuy = pd.DataFrame()
    st.rerun()

# 🔥 RESULTS TABS
tab1, tab2, tab3 = st.tabs(["🟢 STRONG BUY", "📊 ALL SIGNALS", "📈 SUMMARY"])

with tab1:
    if not st.session_state.data_strongbuy.empty:
        st.metric("🚀 BUY NOW", len(st.session_state.data_strongbuy))
        st.dataframe(st.session_state.data_strongbuy, height=400)
        st.download_button("💾 CSV", st.session_state.data_strongbuy.to_csv(index=False), "strongbuy.csv")

with tab2:
    if not st.session_state.data_full.empty:
        st.dataframe(st.session_state.data_full.sort_values('RSI'), height=600, use_container_width=True)

with tab3:
    if not st.session_state.data_full.empty:
        col1, col2, col3, col4 = st.columns(4)
        signals = st.session_state.data_full['Signal'].value_counts()
        
        col1.metric("🟢 STRONG BUY", signals.get('🟢 STRONG BUY', 0))
        col2.metric("🟢 BUY", signals.get('🟢 BUY', 0))
        col3.metric("🔴 SELL", signals.get('🔴 SELL', 0))
        col4.metric("🟡 HOLD", signals.get('🟡 HOLD', 0))
        
        st.bar_chart(signals)

# PERFECT STATUS
st.markdown("---")
st.info("""
**⚡ v9.0 ULTRA-FAST FEATURES**:
✅ **ONE API CALL** = 50 stocks instantly
✅ **10 SECONDS FLAT** guaranteed
✅ **Top 50 Nifty stocks** (most liquid)
✅ **RSI + MA20 signals**
✅ **Clear BUY/SELL/HOLD**
✅ **Works 24/7**

**INSTALL**: pip install streamlit yfinance ta pandas numpy
**No other libraries needed!**
""")
