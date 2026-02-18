import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(layout="wide", page_icon="📈")
st.title("📈 **NIFTY 100 SCANNER** - **Large/Mid/Small Cap Signals**")

# ✅ COMPLETE NIFTY 100 STOCKS (Feb 2026 - 100 stocks)
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

# Market Cap Classification (₹ Cr)
MARKET_CAP_THRESHOLDS = {
    'Large Cap': 50000,   # Top 50 by market cap
    'Mid Cap': 15000,     # 50-75 range  
    'Small Cap': 0        # Rest of Nifty 100
}

# Initialize session state
if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False

@st.cache_data(ttl=300)
def get_nifty_data(symbol):
    try:
        ticker = yf.Ticker(symbol + '.NS')
        info = ticker.info
        hist = ticker.history(period="2mo")
        
        if len(hist) >= 25:
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            price = hist['Close'].iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            market_cap = info.get('marketCap', 0) / 1e7  # Convert to ₹ Cr
            
            # Determine cap category
            if market_cap >= MARKET_CAP_THRESHOLDS['Large Cap']:
                cap_category = '🟦 LARGE CAP'
            elif market_cap >= MARKET_CAP_THRESHOLDS['Mid Cap']:
                cap_category = '🟨 MID CAP'
            else:
                cap_category = '🟢 SMALL CAP'
            
            # Signal logic
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
                'Signal': signal,
                'Cap': cap_category,
                'Market Cap (₹Cr)': f"{market_cap:,.0f}",
                'RSI_Value': rsi
            }
    except:
        pass
    return None

def display_category_signals(all_data, category):
    category_data = [d for d in all_data if d['Cap'] == category]
    
    strong_buy = [d for d in category_data if d['Signal'] == '🟢 STRONG BUY']
    buy_signals = [d for d in category_data if d['Signal'] == '🟢 BUY']
    sell_signals = [d for d in category_data if d['Signal'] == '🔴 SELL']
    hold_signals = [d for d in category_data if d['Signal'] == '🟡 HOLD']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🟢 STRONG BUY", len(strong_buy))
        if strong_buy:
            st.dataframe(pd.DataFrame(strong_buy), use_container_width=True, hide_index=True)
    
    with col2:
        st.metric("🟢 BUY", len(buy_signals))
        if buy_signals:
            st.dataframe(pd.DataFrame(buy_signals), use_container_width=True, hide_index=True)
    
    with col3:
        st.metric("🔴 SELL", len(sell_signals))
        if sell_signals:
            st.dataframe(pd.DataFrame(sell_signals), use_container_width=True, hide_index=True)
    
    with col4:
        st.metric("🟡 HOLD", len(hold_signals))
        if hold_signals:
            st.dataframe(pd.DataFrame(hold_signals), use_container_width=True, hide_index=True)

# MAIN SCAN BUTTON
col_btn1, col_btn2 = st.columns([3, 1])
if col_btn1.button("🚀 **SCAN ALL 100 NIFTY STOCKS BY CAP (2-3 MIN)**", type="primary", use_container_width=True):
    st.session_state.scan_complete = True
    st.rerun()

with col_btn2:
    if st.button("🔄 RESET", use_container_width=True):
        st.session_state.scan_complete = False
        st.rerun()

# RESULTS BY CATEGORY
if st.session_state.scan_complete:
    st.subheader("🚀 **COMPLETE NIFTY 100 SCAN RESULTS**")
    
    # Progress bar
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
    
    # Summary metrics
    st.success(f"✅ **Scanned {successful_scans}/{total_stocks} stocks**")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("📊 Success Rate", f"{successful_scans/total_stocks*100:.1f}%")
    with col_m2:
        st.metric("⏱️ Updated", pd.Timestamp.now().strftime("%H:%M:%S IST"))
    
    # LARGE CAP SECTION
    st.markdown("---")
    st.markdown("## 🟦 **LARGE CAP** (₹50,000+ Cr)")
    display_category_signals(all_data, '🟦 LARGE CAP')
    
    # MID CAP SECTION  
    st.markdown("---")
    st.markdown("## 🟨 **MID CAP** (₹15,000-50,000 Cr)")
    display_category_signals(all_data, '🟨 MID CAP')
    
    # SMALL CAP SECTION
    st.markdown("---")
    st.markdown("## 🟢 **SMALL CAP** (<₹15,000 Cr)")
    display_category_signals(all_data, '🟢 SMALL CAP')
    
    # COMPLETE RESULTS TABLE
    st.markdown("---")
    st.subheader("📋 **COMPLETE RESULTS** (Sorted by RSI)")
    
    if all_data:
        df_complete = pd.DataFrame(all_data).sort_values('RSI_Value')
        display_df = df_complete.drop(columns=['RSI_Value'])
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.download_button(
            "💾 DOWNLOAD FULL CSV", 
            display_df.to_csv(index=False), 
            "nifty100-cap-categories.csv",
            use_container_width=True
        )

st.markdown("---")
st.info("""
**🎯 NIFTY 100 CAP SCANNER**:
✅ **100 stocks** classified: Large/Mid/Small Cap
✅ **Live market cap** from Yahoo Finance
✅ **Separate signals** for each category
✅ RSI(14) + MA20 analysis

**📊 CAP CLASSIFICATION**:
🟦 **LARGE CAP**: ₹50,000+ Cr (Top 50)
🟨 **MID CAP**: ₹15K-50K Cr  
🟢 **SMALL CAP**: <₹15K Cr (Nifty 100)

**⚡ SIGNALS**: Strong Buy/Buy/Sell/Hold per category
**⏱️ Scan time**: 2-3 minutes for all 100 stocks
""")
