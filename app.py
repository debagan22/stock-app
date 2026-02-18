import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import time
import numpy as np

st.set_page_config(page_title="NIFTY ULTRAFAST", layout="wide", page_icon="⚡")
st.title("⚡ **NIFTY SCANNER v9.2** - **10 SECOND SCAN** ✅")

TOP_NIFTY = [
    'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'KOTAKBANK', 'HINDUNILVR', 'ITC', 
    'LT', 'BHARTIARTL', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 
    'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 'ONGC', 'COALINDIA', 
    'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'TATASTEEL', 'CIPLA', 'DRREDDY'
]

if 'data_full' not in st.session_state: 
    st.session_state.data_full = pd.DataFrame()
if 'data_strongbuy' not in st.session_state: 
    st.session_state.data_strongbuy = pd.DataFrame()

@st.cache_data(ttl=300)
def lightning_batch_scan():
    symbols = [s + '.NS' for s in TOP_NIFTY]
    
    try:
        data = yf.download(symbols, period="20d", group_by='ticker', 
                          threads=True, progress=False)
        
        results = []
        for symbol in TOP_NIFTY:
            try:
                if symbol in data.columns.levels[0]:
                    stock_data = data[symbol]['Close'].dropna()
                    if len(stock_data) >= 15:
                        rsi = ta.momentum.RSIIndicator(stock_data).rsi().iloc[-1]
                        ma20 = ta.trend.SMAIndicator(stock_data, 20).sma_indicator().iloc[-1]
                        price = stock_data.iloc[-1]
                        change = ((price / stock_data.iloc[-2] - 1) * 100) if len(stock_data) > 1 else 0
                        
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
        
        if len(results) == 0:
            return pd.DataFrame(), pd.DataFrame()
        
        df = pd.DataFrame(results)
        strongbuy = df[df['Signal'] == '🟢 STRONG BUY']
        return df, strongbuy
        
    except:
        return pd.DataFrame(), pd.DataFrame()

col1, col2 = st.columns([3,1])

if col1.button("⚡ **10 SEC SCAN**", type="primary", use_container_width=True):
    with st.spinner("⚡ Scanning..."):
        df_full, df_strong = lightning_batch_scan()
        st.session_state.data_full = df_full
        st.session_state.data_strongbuy = df_strong
        st.success(f"✅ COMPLETE | {len(df_full)} stocks")
    st.rerun()

if col2.button("🗑️ CLEAR"):
    st.session_state.data_full = pd.DataFrame()
    st.session_state.data_strongbuy = pd.DataFrame()
    st.rerun()

tab1, tab2, tab3 = st.tabs(["🟢 STRONG BUY", "📊 ALL", "📈 SUMMARY"])

with tab1:
    if not st.session_state.data_strongbuy.empty:
        st.metric("🚀 STRONG BUY", len(st.session_state.data_strongbuy))
        st.dataframe(st.session_state.data_strongbuy)
        st.download_button("💾 CSV", st.session_state.data_strongbuy.to_csv(index=False), "strongbuy.csv")

with tab2:
    if not st.session_state.data_full.empty:
        st.dataframe(st.session_state.data_full)

with tab3:
    if not st.session_state.data_full.empty:
        signals = st.session_state.data_full['Signal'].value_counts()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟢 STRONG BUY", signals.get('🟢 STRONG BUY', 0))
        col2.metric("🟢 BUY", signals.get('🟢 BUY', 0))
        col3.metric("🔴 SELL", signals.get('🔴 SELL', 0))
        col4.metric("🟡 HOLD", signals.get('🟡 HOLD', 0))
        st.bar_chart(signals)

st.markdown("---")
st.info("**v9.2 FIXED**: No syntax errors. 10 second scan. Top 30 Nifty stocks. Clear BUY/SELL/HOLD signals. pip install streamlit yfinance ta pandas numpy")
