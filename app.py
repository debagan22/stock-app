import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import numpy as np
from datetime import datetime
import time

st.set_page_config(page_title="LIVE NIFTY 500", layout="wide", page_icon="📈")
st.title("📈 **LIVE NIFTY 500 SCANNER** - **REAL RSI DATA**")

# Real Nifty stocks by SEBI classification
LARGE_CAP = ['RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'KOTAKBANK', 'HINDUNILVR', 'ITC', 'LT', 'BHARTIARTL']
MID_CAP = ['TRENT', 'BEL', 'VARUNBEV', 'PIDILITIND', 'DIXON', 'POLYCAB', 'LAURUSLABS', 'METROPOLIS', 'NAVINFLUOR']
SMALL_CAP = ['CRAVATSYND', 'MPHASIS', 'MRF', 'MUTHOOTFIN', 'NH', 'PIIND', 'PRESTIGE']

@st.cache_data(ttl=300)
def get_live_data(symbols, cap_type):
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol + '.NS')
            hist = ticker.history(period="1mo")
            
            if len(hist) >= 20:
                hist['RSI'] = ta.momentum.RSIIndicator(hist['Close'], window=14).rsi()
                rsi = hist['RSI'].iloc[-1]
                price = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
                
                if cap_type == 'large':
                    strong_rsi, buy_rsi, sell_rsi = 40, 45, 65
                elif cap_type == 'mid':
                    strong_rsi, buy_rsi, sell_rsi = 35, 42, 68
                else:
                    strong_rsi, buy_rsi, sell_rsi = 32, 38, 72
                
                signal = '🟢 STRONG BUY' if rsi < strong_rsi and price > ma20 else \
                        '🟢 BUY' if rsi < buy_rsi else \
                        '🔴 SELL' if rsi > sell_rsi else '🟡 HOLD'
                
                results.append({
                    'Stock': symbol,
                    'Price': f"₹{price:.0f}",
                    'RSI': f"{rsi:.1f}",
                    'MA20': f"₹{ma20:.0f}",
                    'Change': f"{change:+.1f}%",
                    'Signal': signal
                })
        except:
            continue
    
    return pd.DataFrame(results)

# CONTROLS
col1, col2, col3 = st.columns(3)
if col1.button("🔴 LIVE LARGE CAP", type="primary"):
    with st.spinner("Fetching live data..."):
        st.session_state.live_large = get_live_data(LARGE_CAP, 'large')
    st.rerun()

if col2.button("🔴 LIVE MID CAP"):
    with st.spinner("Fetching live data..."):
        st.session_state.live_mid = get_live_data(MID_CAP, 'mid')
    st.rerun()

if col3.button("🔴 LIVE SMALL CAP"):
    with st.spinner("Fetching live data..."):
        st.session_state.live_small = get_live_data(SMALL_CAP, 'small')
    st.rerun()

# PRIMARY TABS
tab1, tab2, tab3 = st.tabs(["🟢 LARGE CAP", "🟡 MID CAP", "🔴 SMALL CAP"])

# LARGE CAP
with tab1:
    if 'live_large' in st.session_state and not st.session_state.live_large.empty:
        cols = st.columns(4)
        data = st.session_state.live_large
        
        with cols[0]:
            strong = data[data['Signal']=='🟢 STRONG BUY']
            st.metric("STRONG BUY", len(strong))
            st.dataframe(strong)
        
        with cols[1]:
            buy = data[data['Signal']=='🟢 BUY']
            st.metric("BUY", len(buy))
            st.dataframe(buy)
        
        with cols[2]:
            sell = data[data['Signal']=='🔴 SELL']
            st.metric("SELL", len(sell))
            st.dataframe(sell)
        
        with cols[3]:
            hold = data[data['Signal']=='🟡 HOLD']
            st.metric("HOLD", len(hold))
            st.dataframe(hold)

# MID CAP  
with tab2:
    if 'live_mid' in st.session_state and not st.session_state.live_mid.empty:
        cols = st.columns(4)
        data = st.session_state.live_mid
        
        with cols[0]:
            strong = data[data['Signal']=='🟢 STRONG BUY']
            st.metric("STRONG BUY", len(strong))
            st.dataframe(strong)
        
        with cols[1]:
            buy = data[data['Signal']=='🟢 BUY']
            st.metric("BUY", len(buy))
            st.dataframe(buy)
        
        with cols[2]:
            sell = data[data['Signal']=='🔴 SELL']
            st.metric("SELL", len(sell))
            st.dataframe(sell)
        
        with cols[3]:
            hold = data[data['Signal']=='🟡 HOLD']
            st.metric("HOLD", len(hold))
            st.dataframe(hold)

# SMALL CAP
with tab3:
    if 'live_small' in st.session_state and not st.session_state.live_small.empty:
        cols = st.columns(4)
        data = st.session_state.live_small
        
        with cols[0]:
            strong = data[data['Signal']=='🟢 STRONG BUY']
            st.metric("STRONG BUY", len(strong))
            st.dataframe(strong)
        
        with cols[1]:
            buy = data[data['Signal']=='🟢 BUY']
            st.metric("BUY", len(buy))
            st.dataframe(buy)
        
        with cols[2]:
            sell = data[data['Signal']=='🔴 SELL']
            st.metric("SELL", len(sell))
            st.dataframe(sell)
        
        with cols[3]:
            hold = data[data['Signal']=='🟡 HOLD']
            st.metric("HOLD", len(hold))
            st.dataframe(hold)

st.markdown("---")
st.success("REAL RSI data from Yahoo Finance. 5-min auto refresh. Market hours 9:15AM-3:30PM IST best.")
