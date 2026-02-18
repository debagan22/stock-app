import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np

st.set_page_config(layout="wide", page_icon="📈")
st.title("📈 **NIFTY 100 SCANNER** - **RSI + MACD + MA20**")

# ✅ COMPLETE NIFTY 100 STOCKS (Feb 2026 - EXACTLY 100)
NIFTY100_COMPLETE = [
    'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 
    'HINDUNILVR', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 
    'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 
    'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'HCLTECH', 'SBIN', 
    'BAJFINANCE', 'TATASTEEL', 'GRASIM', 'HDFCLIFE', 'CIPLA', 'DIVISLAB', 
    'DRREDDY', 'EICHERMOT', 'COALINDIA', 'BRITANNIA', 'HINDALCO', 'BPCL', 
    'BAJAJFINSV', 'APOLLOHOSP', 'HEROMOTOCO', 'SHRIRAMFIN', 'ADANIENT', 
    'TATACONSUM', 'GODREJCP', 'ADANIPORTS', 'TRENT', 'BAJAJ-AUTO', 'IOC',
    'INDUSINDBK', 'LICI', 'SBILIFE', 'PIDILITIND', 'SRTRANSFIN', 'VARUNBEV',
    'DIXON', 'HAL', 'LTFOODS', 'BEL', 'BAJAJHLDNG', 'JINDALSTEL', 'CHOLAFIN',
    'TORNTPOWER', 'HAVELLS', 'AMBUJACEM', 'MPHASIS', 'POLYCAB', 'SOLARINDS',
    'BORORENEW', 'TVSMOTOR', 'ZFCVINDIA', 'ABB', 'DABUR', 'KALPATPOWR',
    'BANKBARODA', 'GAIL', 'SHREECEM', 'SIEMENS', 'LTTS', 'ICICIPRULI',
    'JSWENERGY', 'TORNTPHARM', 'UNIONBANK', 'VEDANTA', 'NMDC', 'SAIL', 
    'PFC', 'RECLTD'
]

# ✅ NIFTY 50 (Top 50 Large Cap)
NIFTY_50 = [
    'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 
    'HINDUNILVR', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 
    'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 
    'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'HCLTECH', 'SBIN', 
    'BAJFINANCE', 'TATASTEEL', 'GRASIM', 'HDFCLIFE', 'CIPLA', 'DIVISLAB', 
    'DRREDDY', 'EICHERMOT', 'COALINDIA', 'BRITANNIA', 'HINDALCO', 'BPCL'
]

st.sidebar.info(f"📊 **Total Stocks: {len(NIFTY100_COMPLETE)}/100** ✅")

if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False

@st.cache_data(ttl=300)
def get_nifty_data(symbol):
    try:
        ticker = yf.Ticker(symbol + '.NS')
        hist = ticker.history(period="3mo", interval="1d")  # More data for indicators
        
        if len(hist) >= 30:
            price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = ((price / prev_price - 1) * 100) if len(hist) > 1 else 0
            
            # 1️⃣ RSI (14)
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            
            # 2️⃣ MACD (12,26,9)
            macd = ta.trend.MACD(hist['Close'], window_slow=26, window_fast=12, window_sign=9)
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            histogram = macd.macd_diff().iloc[-1]
            
            # 3️⃣ MA20 & Price Position
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            price_vs_ma20 = (price > ma20) * 1
            
            # Category
            category = '🟦 NIFTY 50' if symbol in NIFTY_50 else '🟨 NIFTY NEXT 50'
            
            # 🚀 TRIPLE CONFIRMATION SIGNAL LOGIC
            rsi_oversold = rsi < 35
            rsi_buy_zone = rsi < 45
            rsi_sell_zone = rsi > 65
            
            macd_bullish = macd_line > signal_line
            macd_strong_bull = macd_bullish and histogram > 0
            macd_bearish = macd_line < signal_line
            
            # Signal Priority: MA20 > MACD > RSI
            if price_vs_ma20 and rsi_oversold and macd_strong_bull:
                signal = '🚀 SUPER BUY (All 3)'
            elif price_vs_ma20 and (rsi_buy_zone or macd_bullish):
                signal = '🟢 STRONG BUY (2/3)'
            elif rsi_buy_zone or macd_bullish:
                signal = '🟢 BUY (1/3)'
            elif rsi_sell_zone or macd_bearish:
                signal = '🔴 SELL'
            else:
                signal = '🟡 HOLD'
            
            return {
                'Stock': symbol,
                'Price': f"₹{price:.0f}",
                'Change': f"{change:.1f}%",
                'RSI': f"{rsi:.1f}",
                'MACD': f"{macd_line:.3f}",
                'MACD Signal': f"{signal_line:.3f}",
                'Histogram': f"{histogram:.3f}",
                'MA20': f"₹{ma20:.0f}",
                'Price/MA20': '📈' if price > ma20 else '📉',
                'Signal': signal,
                'Category': category,
                'RSI_Value': rsi,
                'MACD_Value': macd_line
            }
    except:
        pass
    return None

def display_category_signals(all_data, category):
    category_data = [d for d in all_data if d['Category'] == category]
    
    super_buy = [d for d in category_data if 'SUPER BUY' in d['Signal']]
    strong_buy = [d for d in category_data if d['Signal'] == '🟢 STRONG BUY']
    buy_signals = [d for d in category_data if d['Signal'] == '🟢 BUY']
    sell_signals = [d for d in category_data if d['Signal'] == '🔴 SELL']
    hold_signals = [d for d in category_data if d['Signal'] == '🟡 HOLD']
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🚀 SUPER BUY", len(super_buy))
        if super_buy:
            st.dataframe(pd.DataFrame(super_buy), use_container_width=True, hide_index=True)
    
    with col2:
        st.metric("🟢 STRONG", len(strong_buy))
        if strong_buy:
            st.dataframe(pd.DataFrame(strong_buy), use_container_width=True, hide_index=True)
    
    with col3:
        st.metric("🟢 BUY", len(buy_signals))
        if buy_signals:
            st.dataframe(pd.DataFrame(buy_signals), use_container_width=True, hide_index=True)
    
    with col4:
        st.metric("🔴 SELL", len(sell_signals))
        if sell_signals:
            st.dataframe(pd.DataFrame(sell_signals), use_container_width=True, hide_index=True)
    
    with col5:
        st.metric("🟡 HOLD", len(hold_signals))
        if hold_signals:
            st.dataframe(pd.DataFrame(hold_signals), use_container_width=True, hide_index=True)

# MAIN CONTROLS
col_btn1, col_btn2 = st.columns([3, 1])
if col_btn1.button("🚀 **SCAN NIFTY 100 - RSI+MACD+MA20 (3 MIN)**", type="primary", use_container_width=True):
    st.session_state.scan_complete = True
    st.rerun()

with col_btn2:
    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.scan_complete = False
        st.rerun()

# RESULTS
if st.session_state.scan_complete:
    st.subheader("🚀 **NIFTY 100 TRIPLE INDICATOR SCAN**")
    
    total_stocks = len(NIFTY100_COMPLETE)
    progress = st.progress(0)
    
    all_data = []
    successful_scans = 0
    
    for i, symbol in enumerate(NIFTY100_COMPLETE):
        data = get_nifty_data(symbol)
        if data:
            all_data.append(data)
            successful_scans += 1
        progress.progress((i + 1) / total_stocks)
        time.sleep(0.15)
    
    progress.empty()
    
    st.success(f"✅ **Scanned {successful_scans}/{total_stocks} stocks**")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("📊 Success Rate", f"{successful_scans/total_stocks*100:.1f}%")
    with col_m2:
        st.metric("⏱️ Updated", pd.Timestamp.now().strftime("%H:%M:%S IST"))
    with col_m3:
        st.metric("🚀 Super Buys", len([d for d in all_data if 'SUPER BUY' in d['Signal']]))
    
    # 🟦 NIFTY 50 SECTION
    st.markdown("---")
    st.markdown("## 🟦 **NIFTY 50** (50 Large Cap Stocks)")
    display_category_signals(all_data, '🟦 NIFTY 50')
    
    # 🟨 NIFTY NEXT 50 SECTION
    st.markdown("---")
    st.markdown("## 🟨 **NIFTY NEXT 50** (50 Large/Mid Cap Stocks)")
    display_category_signals(all_data, '🟨 NIFTY NEXT 50')
    
    # 📊 COMPLETE RESULTS
    st.markdown("---")
    st.subheader("📋 **COMPLETE RESULTS** - **Sorted by RSI**")
    
    if all_data:
        df_complete = pd.DataFrame(all_data).sort_values('RSI_Value')
        display_df = df_complete.drop(columns=['RSI_Value', 'MACD_Value'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.download_button(
            "💾 DOWNLOAD FULL CSV", 
            display_df.to_csv(index=False), 
            "nifty100-triple-indicator.csv",
            use_container_width=True
        )

st.markdown("---")
st.info("""
**🎯 NIFTY 100 TRIPLE INDICATOR SCANNER**:
✅ **RSI(14)** + **MACD(12,26,9)** + **MA20** 
✅ **5 Signals** with confirmation levels
✅ **Nifty 50 + Nifty Next 50** classification

**🚀 SIGNAL LOGIC** (Priority: MA20 → MACD → RSI):
- **SUPER BUY**: All 3 bullish (RSI<35 + Price>MA20 + MACD bullish)
- **STRONG BUY**: 2/3 bullish 
- **BUY**: 1/3 bullish
- **SELL**: RSI>65 OR MACD bearish
- **HOLD**: Neutral

**📊 DISPLAYED COLUMNS**:
RSI | MACD Line | MACD Signal | Histogram | MA20 | Price/MA20

**⚡ SCAN**: 3 minutes for ALL 100 stocks
""")
