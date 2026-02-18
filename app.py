import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Session state
if 'last_strongbuy' not in st.session_state: st.session_state.last_strongbuy = 0
if 'last_full' not in st.session_state: st.session_state.last_full = 0
if 'df_strongbuy' not in st.session_state: st.session_state.df_strongbuy = pd.DataFrame()
if 'df_full' not in st.session_state: st.session_state.df_full = pd.DataFrame()
if 'strongbuy_count' not in st.session_state: st.session_state.strongbuy_count = 0
if 'full_count' not in st.session_state: st.session_state.full_count = 0
if 'auto_strongbuy' not in st.session_state: st.session_state.auto_strongbuy = True
if 'selected_signal' not in st.session_state: st.session_state.selected_signal = "🟢 STRONG BUY"

st.set_page_config(page_title="NIFTY LIVE SCANNER", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 500 LIVE SCANNER")
st.markdown("**🤖 AUTO STRONG BUY | 📊 DROPDOWN SIGNALS**")

# 🔥 ALL 500 STOCKS
nifty500 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "LTIM.NS", "SUNPHARMA.NS", 
    "HCLTECH.NS", "TITAN.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "TECHM.NS", "POWERGRID.NS", "WIPRO.NS", "TATAMOTORS.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "COALINDIA.NS", "NTPC.NS", "ONGC.NS", "M&M.NS", "BAJAJFINSV.NS",
    "BEL.NS", "TATACONSUM.NS", "GRASIM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS",
    "TRENT.NS", "VARUNBEV.NS", "LICI.NS", "BAJAJ-AUTO.NS", "SHRIRAMFIN.NS",
    "GODREJCP.NS", "PIDILITIND.NS", "ADANIENT.NS", "AMBUJACEM.NS", "AUBANK.NS"
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

# 🔥 AUTO STRONG BUY (500 stocks, 45s)
@st.cache_data(ttl=60)
def scan_strongbuy_only():
    results = []
    progress = st.progress(0)
    for i, symbol in enumerate(nifty500):
        result = analyze_stock(symbol)
        if result and result['Signal'] == "🟢 STRONG BUY":
            results.append(result)
        progress.progress((i + 1) / len(nifty500))
        time.sleep(0.08)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 FULL SCAN ALL SIGNALS (120 stocks)
@st.cache_data(ttl=1800)
def scan_full_signals():
    results = []
    progress = st.progress(0)
    reliable_stocks = nifty500[:120]
    
    for i, symbol in enumerate(reliable_stocks):
        result = analyze_stock(symbol)
        if result: results.append(result)
        progress.progress((i + 1) / len(reliable_stocks))
        time.sleep(0.1)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 CONTROLS ROW 1
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_strongbuy = col1.toggle("🤖 AUTO STRONG BUY", value=st.session_state.auto_strongbuy)

if col2.button("🔥 FULL SCAN", type="primary", use_container_width=True):
    with st.spinner("🔥 Scanning all signals..."):
        st.session_state.df_full = scan_full_signals()
        st.session_state.last_full = time.time()
        st.session_state.full_count += 1
    st.rerun()

if col3.button("🔄 CLEAR", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 🔥 AUTO SCAN LOGIC
time_since_strongbuy = time.time() - st.session_state.last_strongbuy
if st.session_state.auto_strongbuy and time_since_strongbuy > 45:
    with st.spinner("🔍 Auto scanning STRONG BUY (500 stocks)..."):
        st.session_state.df_strongbuy = scan_strongbuy_only()
        st.session_state.last_strongbuy = time.time()
        st.session_state.strongbuy_count += 1
    st.rerun()

# 🔥 MAIN TABS
tab1, tab2 = st.tabs(["🟢 LIVE STRONG BUY", "📊 ALL SIGNALS"])

with tab1:
    if not st.session_state.df_strongbuy.empty:
        df = st.session_state.df_strongbuy
        st.success(f"✅ LIVE STRONG BUY | #{st.session_state.strongbuy_count} | {len(df)} stocks")
        st.dataframe(df.sort_values('RSI'), height=400, use_container_width=True)
        
        csv = df.to_csv(index=False)
        st.download_button("💾 DOWNLOAD STRONG BUY", csv, "strong-buy.csv")
    else:
        st.info("🤖 AUTO scanning 500 stocks for STRONG BUY...")

with tab2:
    st.markdown("### 📊 SELECT SIGNAL TYPE")
    
    # 🔥 DROPDOWN MENU FOR ALL SIGNALS
    signal_options = {
        "🟢 STRONG BUY": "🟢 STRONG BUY",
        "🟢 BUY": "🟢 BUY", 
        "🔴 STRONG SELL": "🔴 STRONG SELL",
        "🔴 SELL": "🔴 SELL",
        "🟡 HOLD": "🟡 HOLD",
        "📊 ALL SIGNALS": "ALL"
    }
    
    selected_signal = st.selectbox(
        "Choose Signal:", 
        options=list(signal_options.keys()),
        index=list(signal_options.keys()).index(st.session_state.selected_signal),
        help="Filter by signal type"
    )
    st.session_state.selected_signal = selected_signal
    
    if not st.session_state.df_full.empty:
        df = st.session_state.df_full
        
        # Filter by selected signal
        if selected_signal != "📊 ALL SIGNALS":
            filtered_df = df[df['Signal'] == selected_signal]
            st.success(f"✅ **{selected_signal}** | {len(filtered_df)} stocks | Scan #{st.session_state.full_count}")
        else:
            filtered_df = df
            st.success(f"✅ **ALL SIGNALS** | {len(filtered_df)} stocks | Scan #{st.session_state.full_count}")
        
        # Metrics for current selection
        col1, col2 = st.columns(2)
        col1.metric("📊 Count", len(filtered_df))
        if not filtered_df.empty:
            col2.metric("🔥 Best RSI", f"{filtered_df['RSI'].min():.1f}")
        
        st.dataframe(filtered_df.sort_values('RSI'), height=400, use_container_width=True)
        
        # Download filtered data
        csv_filtered = filtered_df.to_csv(index=False)
        st.download_button("💾 DOWNLOAD FILTERED", csv_filtered, f"{selected_signal.lower().replace(' ','_')}.csv")
        
    else:
        st.info("🔥 Click FULL SCAN first")

# 🔥 STATUS DASHBOARD
st.markdown("---")
st.subheader("📊 LIVE STATUS")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🤖 StrongBuy Scans", st.session_state.strongbuy_count)
col2.metric("🔥 Full Scans", st.session_state.full_count)
col3.metric("⏱️ Auto Timer", f"{time_since_strongbuy:.0f}s")
col4.metric("🟢 Live StrongBuys", len(st.session_state.df_strongbuy))

st.info("""
**🤖 AUTO**: Scans 500 stocks every 45s → **STRONG BUY ONLY**  
**🔥 MANUAL**: 120 stocks → **DROPDOWN: STRONG BUY | BUY | SELL | HOLD | ALL**  
**🎯 PERFECT**: Live opportunities + Complete analysis!
""")
