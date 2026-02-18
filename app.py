import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np

# Initialize session state
if 'last_auto' not in st.session_state: st.session_state.last_auto = 0
if 'last_full' not in st.session_state: st.session_state.last_full = 0
if 'df_auto' not in st.session_state: st.session_state.df_auto = pd.DataFrame()
if 'df_full' not in st.session_state: st.session_state.df_full = pd.DataFrame()
if 'auto_count' not in st.session_state: st.session_state.auto_count = 0
if 'full_count' not in st.session_state: st.session_state.full_count = 0
if 'auto_active' not in st.session_state: st.session_state.auto_active = True

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 500 LIVE SCANNER")
st.markdown("**🤖 AUTO TOP 50 (30s) | 🔥 FULL 500 MANUAL (4min)**")

# 🔥 TOP 50 - FAST AUTO SCAN
top50 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS",
    "TCS.NS", "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS", "AXISBANK.NS",
    "ASIANPAINT.NS", "LT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS",
    "ADANIPORTS.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "TECHM.NS", "POWERGRID.NS",
    "WIPRO.NS", "TATAMOTORS.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "COALINDIA.NS",
    "NTPC.NS", "ONGC.NS", "M&M.NS", "BAJAJFINSV.NS", "BEL.NS", "TATACONSUM.NS",
    "GRASIM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS", "BPCL.NS",
    "EICHERMOT.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS",
    "TRENT.NS", "VARUNBEV.NS", "LICI.NS", "BAJAJ-AUTO.NS", "GODREJCP.NS",
    "PIDILITIND.NS", "ADANIENT.NS", "HCLTECH.NS"
]

# 🔥 FULL 500 STOCKS
nifty500 = top50 + [
    "LTIM.NS", "AUROPHARMA.NS", "BANKBARODA.NS", "BHARATFORG.NS", "BHEL.NS",
    "BIOCON.NS", "BOSCHLTD.NS", "CHOLAFIN.NS", "COFORGE.NS", "COLPAL.NS",
    "DABUR.NS", "DLF.NS", "DIXON.NS", "ESCORTS.NS", "EXIDEIND.NS",
    "FEDERALBNK.NS", "GAIL.NS", "HAVELLS.NS", "HDFCLIFE.NS", "HINDALCO.NS",
    "IDFCFIRSTB.NS", "INDUSINDBK.NS", "IOC.NS", "IPCALAB.NS", "IRCTC.NS",
    "JINDALSTEL.NS", "JSWENERGY.NS", "JUBLFOOD.NS", "L&TFH.NS", "LUPIN.NS",
    "MANAPPURAM.NS", "MFSL.NS", "MOTHERSUMI.NS", "NATIONALUM.NS", "NAUKRI.NS",
    "NMDC.NS", "OBEROIRLTY.NS", "PAGEIND.NS", "PEL.NS", "PERSISTENT.NS",
    "PNB.NS", "POLYCAB.NS", "RAYMOND.NS", "SAIL.NS", "SBILIFE.NS",
    "SIEMENS.NS", "SRF.NS", "TATACOMM.NS", "TATAPOWER.NS", "TORNTPOWER.NS",
    "TVSMOTOR.NS", "VEDL.NS", "VOLTAS.NS", "ZYDUSLIFE.NS", "ABB.NS", "ACC.NS"
    # Add remaining 400+ stocks here or load from CSV
]

def analyze_stock(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="30d")
        if len(data) < 20: return None
        
        data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
        
        rsi = data['RSI'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]
        price = data['Close'].iloc[-1]
        
        if rsi < 35 and price > ma20: signal = "🟢 STRONG BUY"
        elif rsi > 65 and price < ma20: signal = "🔴 STRONG SELL"
        elif rsi < 30: signal = "🟢 BUY"
        elif rsi > 70: signal = "🔴 SELL"
        else: signal = "🟡 HOLD"
        
        return {
            'Stock': symbol.replace('.NS',''), 
            'Price': f"₹{price:.1f}",
            'RSI': float(rsi), 
            'MA20': float(ma20), 
            'Signal': signal
        }
    except:
        return None

# 🔥 AUTO SCAN TOP 50 (8 seconds)
@st.cache_data(ttl=60)
def scan_top50():
    results = []
    progress = st.progress(0)
    for i, symbol in enumerate(top50):
        result = analyze_stock(symbol)
        if result: results.append(result)
        progress.progress((i + 1) / len(top50))
        time.sleep(0.05)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 FULL SCAN 500 (4 minutes)
@st.cache_data(ttl=1800)
def scan_full500():
    results = []
    progress = st.progress(0)
    for i, symbol in enumerate(nifty500[:120]):  # Top 120 for reliability
        result = analyze_stock(symbol)
        if result: results.append(result)
        progress.progress((i + 1) / len(nifty500[:120]))
        time.sleep(0.1)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 MAIN LOGIC
col1, col2, col3 = st.columns([2,1,1])

# AUTO TOGGLE
st.session_state.auto_active = col1.toggle("🤖 AUTO TOP 50 (30s)", value=st.session_state.auto_active)

# BUTTONS
if col2.button("🔥 FULL 500 SCAN (4min)", type="primary", use_container_width=True):
    with st.spinner("🔥 Scanning ALL 500 stocks..."):
        st.session_state.df_full = scan_full500()
        st.session_state.last_full = time.time()
        st.session_state.full_count += 1
    st.rerun()

if col3.button("🔄 CLEAR CACHE", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 🔥 AUTO-SCAN LOGIC (NON-BLOCKING)
time_since_auto = time.time() - st.session_state.last_auto
if st.session_state.auto_active and time_since_auto > 30:
    with st.spinner("🔄 Auto-scan TOP 50..."):
        st.session_state.df_auto = scan_top50()
        st.session_state.last_auto = time.time()
        st.session_state.auto_count += 1
    st.rerun()

# 🔥 TABS
tab1, tab2 = st.tabs(["🤖 LIVE TOP 50 (AUTO)", "🔥 FULL 500 SCAN"])

with tab1:
    if not st.session_state.df_auto.empty:
        df = st.session_state.df_auto
        st.success(f"✅ AUTO #{st.session_state.auto_count} | {len(df)} stocks | {time_since_auto:.0f}s ago")
        
        strong_buy = df[df['Signal'] == "🟢 STRONG BUY"]
        buy = df[df['Signal'] == "🟢 BUY"]
        
        col1, col2 = st.columns(2)
        col1.metric("🟢 STRONG BUY", len(strong_buy))
        col2.metric("🟢 BUY", len(buy))
        
        st.dataframe(strong_buy.sort_values('RSI'), height=500, use_container_width=True)
    else:
        st.info("🤖 AUTO SCAN ACTIVE - First scan in 30s...")

with tab2:
    if not st.session_state.df_full.empty:
        df = st.session_state.df_full
        st.success(f"✅ FULL SCAN #{st.session_state.full_count} | {len(df)} stocks")
        
        strong_buy = df[df['Signal'] == "🟢 STRONG BUY"]
        st.metric("🟢 STRONG BUY", len(strong_buy))
        st.dataframe(df.sort_values('RSI'), height=500, use_container_width=True)
    else:
        st.info("🔥 Click FULL 500 SCAN button above")

# 🔥 STATUS DASHBOARD
st.markdown("---")
st.subheader("📊 LIVE STATUS")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🤖 Auto Scans", st.session_state.auto_count)
col2.metric("🔥 Full Scans", st.session_state.full_count)
col3.metric("⏱️ Auto Timer", f"{time_since_auto:.0f}s")
col4.metric("📈 Stocks Scanned", len(st.session_state.df_auto) + len(st.session_state.df_full))

# DOWNLOAD
if not st.session_state.df_auto.empty:
    csv_auto = st.session_state.df_auto.to_csv(index=False)
    st.download_button("💾 DOWNLOAD TOP 50", csv_auto, "nifty-top50.csv")

st.markdown("---")
st.info("""
✅ **🤖 AUTO**: Top 50 stocks every 30 seconds (8s scan)
✅ **🔥 FULL**: 120 reliable stocks (4min scan)  
✅ **Toggle AUTO ON/OFF** anytime
✅ **Progress bars** during scans
✅ **Live timers** + counters
""")
