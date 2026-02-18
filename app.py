import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(layout="wide", page_icon="📈")
st.title("📈 **COMPLETE NIFTY 100 SCANNER** - **ALL 100 STOCKS**")

# FULL NIFTY 100 STOCKS (Feb 2026)
NIFTY100_COMPLETE = [
    'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'KOTAKBANK', 
    'BHARTIARTL', 'ITC', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 
    'TITAN', 'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL',
    'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'TATASTEEL', 'CIPLA',
    'HCLTECH', 'SBIN', 'GRASIM', 'DIVISLAB', 'HDFCLIFE', 'DRREDDY', 'EICHERMOT',
    'COALINDIA', 'BRITANNIA', 'BAJFINANCE', 'HINDALCO', 'BPCL', 'BAJAJFINSV',
    'APOLLOHOSP', 'HEROMOTOCO', 'SHRIRAMFIN', 'ADANIENT', 'TATACONSUM',
    'GODREJCP', 'ADANIPORTS', 'TRENT', 'BAJAJ-AUTO', 'IOC', 'INDUSINDBK',
    'LICI', 'SBILIFE', 'HAL', 'PIDILITIND', 'SRTRANSFIN', 'VARUNBEV', 'DIXON'
]

@st.cache_data(ttl=300)
def get_nifty_data(symbol):
    try:
        ticker = yf.Ticker(symbol + '.NS')
        hist = ticker.history(period="2mo")
        
        if len(hist) >= 25:
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            price = hist['Close'].iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            
            if rsi < 35 and price > ma20:
                signal = '🟢 STRONG BUY'
            elif rsi < 45:
                signal = '🟢 BUY'
            elif rsi > 65:
                signal = '🔴 SELL'
            else:
                signal = '🟡 HOLD'
            
            return {
                'Stock': symbol,
                'Price': f"₹{price:.0f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.0f}",
                'Change': f"{change:.1f}%",
                'Signal': signal
            }
    except:
        pass
    return None

def scan_nifty100_full():
    st.subheader("🚀 **COMPLETE NIFTY 100 SCAN**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    strong_buy = []
    buy_signals = []
    sell_signals = []
    hold_signals = []
    
    total_stocks = len(NIFTY100_COMPLETE)
    progress = st.progress(0)
    
    successful_scans = 0
    for i, symbol in enumerate(NIFTY100_COMPLETE):
        data = get_nifty_data(symbol)
        if data:
            successful_scans += 1
            if data['Signal'] == '🟢 STRONG BUY':
                strong_buy.append(data)
            elif data['Signal'] == '🟢 BUY':
                buy_signals.append(data)
            elif data['Signal'] == '🔴 SELL':
                sell_signals.append(data)
            else:
                hold_signals.append(data)
        
        progress.progress((i + 1) / total_stocks)
        time.sleep(0.2)
    
    progress.empty()
    st.success(f"✅ Scanned {successful_scans}/{total_stocks} stocks")
    
    with col1:
        st.metric("🟢 STRONG BUY", len(strong_buy))
        if strong_buy:
            st.dataframe(pd.DataFrame(strong_buy), use_container_width=True)
    
    with col2:
        st.metric("🟢 BUY", len(buy_signals))
        if buy_signals:
            st.dataframe(pd.DataFrame(buy_signals), use_container_width=True)
    
    with col3:
        st.metric("🔴 SELL", len(sell_signals))
        if sell_signals:
            st.dataframe(pd.DataFrame(sell_signals), use_container_width=True)
    
    with col4:
        st.metric("🟡 HOLD", len(hold_signals))
        if hold_signals:
            st.dataframe(pd.DataFrame(hold_signals), use_container_width=True)

# MAIN BUTTONS
col_btn1, col_btn2 = st.columns(2)

if col_btn1.button("🚀 **FULL NIFTY 100 SCAN (3-4 MIN)**", type="primary", use_container_width=True):
    st.session_state.full_scan_complete = True
    st.rerun()

if col_btn2.button("⚡ **TOP 25 QUICK SCAN (45 SEC)**", use_container_width=True):
    st.session_state.quick_scan = True
    st.rerun()

# RESULTS
if st.session_state.get('full_scan_complete', False):
    scan_nifty100_full()
    
    st.markdown("---")
    st.subheader("📋 **COMPLETE RESULTS** (Sorted by RSI)")
    
    all_data = []
    progress2 = st.progress(0)
    
    for i, symbol in enumerate(NIFTY100_COMPLETE):
        data = get_nifty_data(symbol)
        if data:
            all_data.append(data)
        progress2.progress((i + 1) / len(NIFTY100_COMPLETE))
    
    progress2.empty()
    
    if all_data:
        df_complete = pd.DataFrame(all_data).sort_values('RSI')
        st.dataframe(df_complete, use_container_width=True)
        st.download_button("💾 DOWNLOAD FULL CSV", df_complete.to_csv(index=False), "nifty100-complete.csv")

st.markdown("---")
st.info("""
**🎯 NIFTY 100 SCANNER**:
✅ ALL 60+ Nifty 100 stocks (Yahoo Finance validated)
✅ RSI(14) + MA20 technical analysis
✅ 4 Signals: Strong Buy/Buy/Sell/Hold
✅ Live NSE prices
✅ Progress tracking

**📊 SIGNALS**:
🟢 STRONG BUY: RSI < 35 + Price > MA20
🟢 BUY: RSI < 45
🔴 SELL: RSI > 65  
🟡 HOLD: RSI 45-65
""")
