import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(layout="wide", page_icon="📈")
st.title("📈 **COMPLETE NIFTY 100 SCANNER** - **ALL 100 STOCKS**")

# FULL NIFTY 100 STOCKS LIST (Feb 2026)
NIFTY100_COMPLETE = [
    'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'HINDUNILVR', 'KOTAKBANK', 
    'BHARTIARTL', 'ITC', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 
    'TITAN', 'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL',
    'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'TATASTEEL', 'CIPLA',
    'HCLTECH', 'SBIN', 'GRASIM', 'DIVISLAB', 'HDFCLIFE', 'DRREDDY', 'EICHERMOT',
    'COALINDIA', 'BRITANNIA', 'BAJFINANCE', 'HINDALCO', 'BPCL', 'BAJAJFINSV',
    'APOLLOHOSP', 'HEROMOTOCO', 'SHRIRAMFIN', 'ADANIENT', 'ULTRACEMCO',
    'TATACONSUM', 'GODREJCP', 'ADANIPORTS', 'TRENT', 'BAJAJ-AUTO', 'IOC',
    'INDUSINDBK', 'LICI', 'SBILIFE', 'HAL', 'PIDILITIND', 'SRTRANSFIN',
    'VARUNBEV', 'DIXON', 'JINDALSTEL', 'CHOLAFIN', 'BEL', 'PFC', 'BAJAJHLDNG',
    'HINDPETRO', 'AMBUJACEM', 'SAIL', 'DLF', 'NMDC', 'ADANIGREEN', 'HAVELLS',
    'TATAPOWER', 'ZYDUSLIFE', 'ABB', 'INDUSTOWER', 'JSWENERGY', 'POLICYBZR',
    'PERSISTENT', 'PAGEIND', 'COROMANDEL', 'MINDTREE', 'OIL', 'TORNTPOWER',
    'UPL', 'BANKBARODA', 'CANBK', 'GAIL', 'IDFCFIRSTB', 'NARECOCORE',
    'PNB', 'AUBANK', 'ABBOTINDIA', 'ACC', 'APOLLOTYRE', 'ASHOKLEY',
    'AUROPHARMA', 'BOSCHLTD'
]

@st.cache_data(ttl=300)
def get_nifty_data(symbol):
    """RSI + MA20 + 4 Signals"""
    try:
        ticker = yf.Ticker(symbol + '.NS')
        hist = ticker.history(period="2mo")
        
        if len(hist) >= 25:
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            price = hist['Close'].iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            
            # SIGNAL LOGIC
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
    """Scan ALL 100 Nifty stocks"""
    st.subheader("🚀 **COMPLETE NIFTY 100 SCAN** (100 stocks)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    strong_buy, buy_signals, sell_signals, hold_signals = [], [], [], []
    
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
        
        progress.progress((i+1)/total_stocks)
        time.sleep(0.2)  # Faster rate limiting
    
    progress.empty()
    
    st.success(f"✅ **Scanned {successful_scans}/{total_stocks} stocks**")
    
    # 4 SIGNAL COLUMNS
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

# MAIN CONTROLS
if st.button("🚀 **SCAN ALL 100 NIFTY STOCKS (3-4 MIN)**", type="primary", use_container_width=True):
    with st.spinner("🔄 Scanning ALL Nifty 100 stocks..."):
        st.session_state.full_scan_complete = True
    st.rerun()

# QUICK SCAN OPTION (Top 25)
if st.button("⚡ **QUICK SCAN - TOP 25 NIFTY (45 SEC)**", use_container_width=True):
    with st.spinner("🔄 Quick scan Top 25..."):
        st.session_state.quick_scan = True
    st.rerun()

# RESULTS
if st.session_state.get('full_scan_complete', False):
    scan_nifty100_full()
    
    st.markdown("---")
    st.subheader("📋 **FULL NIFTY 100 RESULTS** (Sorted by RSI)")
    
    all_data = []
    for sy
import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(layout="wide")
st.title("🔴 **LIVE NIFTY SCANNER** - **RSI + MA20 + 4 Signals**")

# PROVEN WORKING NSE SYMBOLS
LARGE_CAP = ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY']
MID_CAP = ['TRENT', 'BEL']
SMALL_CAP = ['LAURUSLABS']

@st.cache_data(ttl=300)
def get_full_data(symbol):
    """RSI + MA20 + 4 Trading Signals"""
    try:
        ticker = yf.Ticker(symbol + '.NS')
        hist = ticker.history(period="2mo")
        
        if len(hist) >= 25:
            # RSI(14)
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            price = hist['Close'].iloc[-1]
            ma20 = hist['Close'].rolling(window=20).mean().iloc[-1]
            change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            
            # 4 SIGNAL LOGIC (RSI + MA20)
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

def scan_category(symbols, title):
    """Scan with progress + signals"""
    st.subheader(title)
    col1, col2, col3, col4 = st.columns(4)
    
    strong_buy, buy_signals, sell_signals, hold_signals = [], [], [], []
    
    progress = st.progress(0)
    
    for i, symbol in enumerate(symbols):
        data = get_full_data(symbol)
        if data:
            if data['Signal'] == '🟢 STRONG BUY':
                strong_buy.append(data)
            elif data['Signal'] == '🟢 BUY':
                buy_signals.append(data)
            elif data['Signal'] == '🔴 SELL':
                sell_signals.append(data)
            else:
                hold_signals.append(data)
        
        progress.progress((i+1)/len(symbols))
        time.sleep(0.3)
    
    progress.empty()
    
    # DISPLAY 4 SIGNALS
    with col1:
        st.metric("🟢 STRONG BUY", len(strong_buy))
        if strong_buy:
            st.dataframe(pd.DataFrame(strong_buy))
    
    with col2:
        st.metric("🟢 BUY", len(buy_signals))
        if buy_signals:
            st.dataframe(pd.DataFrame(buy_signals))
    
    with col3:
        st.metric("🔴 SELL", len(sell_signals))
        if sell_signals:
            st.dataframe(pd.DataFrame(sell_signals))
    
    with col4:
        st.metric("🟡 HOLD", len(hold_signals))
        if hold_signals:
            st.dataframe(pd.DataFrame(hold_signals))

# SCAN BUTTONS
col1, col2, col3 = st.columns(3)
if col1.button("🟢 LARGE CAP SCAN", type="primary"):
    st.session_state.large_scanned = True
    st.rerun()

if col2.button("🟡 MID CAP SCAN"):
    st.session_state.mid_scanned = True
    st.rerun()

if col3.button("🔴 SMALL CAP SCAN"):
    st.session_state.small_scanned = True
    st.rerun()

# LARGE CAP
if st.session_state.get('large_scanned', False):
    st.markdown("### 🏢 **LARGE CAP**")
    scan_category(LARGE_CAP, "Large Cap Results")

# MID CAP
if st.session_state.get('mid_scanned', False):
    st.markdown("### 📈 **MID CAP**")
    scan_category(MID_CAP, "Mid Cap Results")

# SMALL CAP
if st.session_state.get('small_scanned', False):
    st.markdown("### 🚀 **SMALL CAP**")
    scan_category(SMALL_CAP, "Small Cap Results")

st.info("""
**✅ SIGNAL LOGIC** (RSI + MA20):
🟢 STRONG BUY: RSI < 35 + Price > MA20
🟢 BUY: RSI < 45
🔴 SELL: RSI > 65  
🟡 HOLD: RSI 45-65

**📊 COLUMNS**:
Price | RSI(14) | MA20 | Change% | Signal

**⏰ After hours**: Last closing data + historical RSI
**9:15AM-3:30PM**: Live intraday prices
""")
