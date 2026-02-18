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
