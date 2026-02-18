import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import numpy as np
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="LIVE NIFTY 500", layout="wide", page_icon="📈")
st.title("📈 **LIVE NIFTY 500 SCANNER** - **REAL RSI DATA**")

# Real Nifty stocks by SEBI classification
LARGE_CAP = ['RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'KOTAKBANK', 'HINDUNILVR', 'ITC', 'LT', 'BHARTIARTL']
MID_CAP = ['TRENT', 'BEL', 'VARUNBEV', 'PIDILITIND', 'DIXON', 'POLYCAB', 'LAURUSLABS', 'METROPOLIS', 'NAVINFLUOR']
SMALL_CAP = ['CRAVATSYND', 'MPHASIS', 'MRF', 'MUTHOOTFIN', 'NH', 'PIIND', 'PRESTIGE']

@st.cache_data(ttl=300)  # Cache 5 minutes
def get_live_data(symbols, cap_type):
    """Fetch REAL market data + calculate RSI"""
    results = []
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol + '.NS')
            hist = ticker.history(period="1mo", interval="1d")
            
            if len(hist) >= 20:
                # REAL TECHNICAL INDICATORS
                hist['RSI'] = ta.momentum.RSIIndicator(hist['Close'], window=14).rsi()
                rsi = hist['RSI'].iloc[-1]
                price = hist['Close'].iloc[-1]
                ma20 = hist['Close'].rolling(20).mean().iloc[-1]
                change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
                
                # Cap-specific signals
                if cap_type == 'large':
                    strong_rsi, buy_rsi, sell_rsi = 40, 45, 65
                elif cap_type == 'mid':
                    strong_rsi, buy_rsi, sell_rsi = 35, 42, 68
                else:  # small
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
                    'Signal': signal,
                    'Time': datetime.now().strftime("%H:%M")
                })
        except Exception as e:
            continue
    
    return pd.DataFrame(results)

# MAIN CONTROLS
col1, col2, col3 = st.columns(3)
if col1.button("🔴 **LIVE SCAN LARGE CAP**", type="primary"):
    with st.spinner("Fetching LIVE data..."):
        st.session_state.live_large = get_live_data(LARGE_CAP, 'large')
    st.rerun()

if col2.button("🔴 **LIVE SCAN MID CAP**"):
    with st.spinner("Fetching LIVE data..."):
        st.session_state.live_mid = get_live_data(MID_CAP, 'mid')
    st.rerun()

if col3.button("🔴 **LIVE SCAN SMALL CAP**"):
    with st.spinner("Fetching LIVE data..."):
        st.session_state.live_small = get_live_data(SMALL_CAP, 'small')
    st.rerun()

# PRIMARY CAP TABS - LIVE DATA
tab1, tab2, tab3 = st.tabs(["🟢 **LARGE CAP** (REAL DATA)", "🟡 **MID CAP** (REAL DATA)", "🔴 **SMALL CAP** (REAL DATA)"])

# LARGE CAP TAB
with tab1:
    st.markdown("### 🏢 **LARGE CAP** - LIVE RSI DATA")
    
    if 'live_large' in st.session_state and not st.session_state.live_large.empty:
        col_main, col_signals = st.columns([3,1])
        
        with col_main:
            signal_tabs = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
            
            data = st.session_state.live_large
            
            with signal_tabs[0]:
                strong_df = data[data['Signal'] == '🟢 STRONG BUY']
                st.metric("🚀 LIVE STRONG BUY", len(strong_df))
                st.dataframe(strong_df)
            
            with signal_tabs[1]:
                buy_df = data[data['Signal'] == '🟢 BUY']
                st.metric("🟢 LIVE BUY", len(buy_df))
                st.dataframe(buy_df)
            
            with signal_tabs[2]:
                sell_df = data[data['Signal'] == '🔴 SELL']
                st.metric("🔴 LIVE SELL", len(sell_df))
                st.dataframe(sell_df)
            
            with signal_tabs[3]:
                hold_df = data[data['Signal'] == '🟡 HOLD']
                st.metric("🟡 LIVE HOLD", len(hold_df))
                st.dataframe(hold_df)
        
        with col_signals:
            st.download_button("💾 CSV", st.session_state.live_large.to_csv(index=False), "large-cap-live.csv")
    else:
        st.info("👆 Click **LIVE SCAN LARGE CAP** to fetch real data")

# MID CAP TAB
with tab2:
    st.markdown("### 📈 **MID CAP** - LIVE RSI DATA")
    
    if 'live_mid' in st.session_state and not st.session_state.live_mid.empty:
        col_main, col_signals = st.columns([3,1])
        
        with col_main:
            signal_tabs = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
            data = st.session_state.live_mid
            
            with signal_tabs[0]:
                strong_df = data[data['Signal'] == '🟢 STRONG BUY']
                st.metric("🚀 LIVE STRONG BUY", len(strong_df))
                st.dataframe(strong_df)
            
            with signal_tabs[1]:
                buy_df = data[data['Signal'] == '🟢 BUY']
                st.metric("🟢 LIVE BUY", len(buy_df))
                st.dataframe(buy_df)
            
            with signal_tabs[2]:
                sell_df = data[data['Signal'] == '🔴 SELL']
                st.metric("🔴 LIVE SELL", len(sell_df))
                st.dataframe(sell_df)
            
            with signal_tabs[3]:
                hold_df = data[data['Signal'] == '🟡 HOLD']
                st.metric("🟡 LIVE HOLD", len(hold_df))
                st.dataframe(hold_df)
        
        with col_signals:
            st.download_button("💾 CSV", st.session_state.live_mid.to_csv(index=False), "mid-cap-live.csv")
    else:
        st.info("👆 Click **LIVE SCAN MID CAP** to fetch real data")

# SMALL CAP TAB
with tab3:
    st.markdown("### 🚀 **SMALL CAP** - LIVE RSI DATA")
    
    if 'live_small' in st.session_state and not st.session_state.live_small.empty:
        col_main, col_signals = st.columns([3,1])
        
        with col_main:
            signal_tabs = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
            data = st.session_state.live_small
            
            with signal_tabs[0]:
                strong_df = data[data['Signal'] == '🟢 STRONG BUY']
                st.metric("🚀 LIVE STRONG BUY", len(strong_df))
                st.dataframe(strong_df)
            
            with signal_tabs[1]:
                buy_df = data[data['Signal'] == '🟢 BUY']
                st.metric("🟢 LIVE BUY", len(buy_df))
                st.dataframe(buy_df)
            
            with signal_tabs[2]:
                sell_df = data[data['Signal'] == '🔴 SELL']
                st.metric("🔴 LIVE SELL", len(sell_df))
                st.dataframe(sell_df)
            
            with signal_tabs[3]:
                hold_df = data[data['Signal'] == '🟡 HOLD']
                st.metric("🟡 LIVE HOLD", len(hold_df))
                st.dataframe(hold_df)
        
        with col_signals:
            st.download_button("💾 CSV", st.session_state.live_small.to_csv(index=False), "small-cap-live.csv")
    else:
        st.info("👆 Click **LIVE SCAN SMALL CAP** to fetch real data")

# STATUS
st.markdown("---")
st.info("""
**📊 LIVE DATA FEATURES**:
✅ **REAL RSI** calculated from 30-day history
✅ **REAL PRICES** from Yahoo Finance NSE
✅ **MA20 crossover** confirmation for Strong Buy
✅ **Cap-specific thresholds** (Large/Mid/Small)
✅ **5-minute auto-cache** refresh
✅ **CSV export** ready

**⏰ BEST DURING MARKET HOURS**: 9:15 AM - 3:30 PM IST
**🌙 After hours**: Shows last close + historical RSI

**INSTALL**:
```bash
pip install streamlit yfinance pandas ta numpy
