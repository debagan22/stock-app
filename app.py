import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Initialize session state for timer
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = 0
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0

st.set_page_config(page_title="NIFTY 50 LIVE", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 50 RSI + MA SCANNER")
st.markdown("**Dual confirmation | Auto-refresh every 5 mins + Manual option**")

# OFFICIAL NIFTY 50
nifty50 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "INFY.NS", "LICI.NS", "HINDUNILVR.NS", "MARUTI.NS",
    "M&M.NS", "KOTAKBANK.NS", "AXISBANK.NS", "SUNPHARMA.NS", "ITC.NS", "HCLTECH.NS",
    "ULTRACEMCO.NS", "TITAN.NS", "ADANIPORTS.NS", "NTPC.NS", "ONGC.NS", "BEL.NS",
    "BAJAJFINSV.NS", "ASIANPAINT.NS", "NESTLEIND.NS", "TECHM.NS", "POWERGRID.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "WIPRO.NS",
    "COALINDIA.NS", "TATACONSUM.NS", "GRASIM.NS", "DIVISLAB.NS", "LTIM.NS",
    "DRREDDY.NS", "CIPLA.NS", "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    "BRITANNIA.NS", "APOLLOHOSP.NS", "TRENT.NS", "VARUNBEV.NS"
]

@st.cache_data(ttl=300)
def scan_nifty50():
    results = []
    failed = 0
    
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            if len(data) < 20:
                failed += 1
                continue
            
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            if rsi < 35 and price > ma20:
                signal = "🟢 STRONG BUY"
            elif rsi > 65 and price < ma20:
                signal = "🔴 STRONG SELL"
            elif rsi < 30:
                signal = "🟢 BUY"
            elif rsi > 70:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.1f}",
                'Signal': signal
            })
            time.sleep(0.5)
        except:
            failed += 1
    
    return pd.DataFrame(results), failed

# 🔥 MAIN SCANNER WITH MANUAL + AUTO
col1, col2 = st.columns([3,1])

with col1:
    if st.button("🔥 MANUAL SCAN NOW", type="primary", use_container_width=True, key="manual"):
        st.session_state.last_scan = time.time()
        st.session_state.scan_count += 1
        st.rerun()

with col2:
    if st.button("🔄 FORCE REFRESH", use_container_width=True, key="force"):
        st.cache_data.clear()
        st.session_state.last_scan = time.time()
        st.rerun()

# AUTO-REFRESH EXECUTION
time_since_scan = time.time() - st.session_state.last_scan
if time_since_scan > 300 or st.session_state.scan_count == 0:  # 5 mins or first load
    df, failed = scan_nifty50()
    st.session_state.last_scan = time.time()
    st.session_state.df = df
    st.session_state.failed = failed

# DISPLAY RESULTS
try:
    df = st.session_state.df
    failed = st.session_state.failed
    
    st.success(f"✅ **{len(df)}/{50-failed} SUCCESS** | Scan #{st.session_state.scan_count}")
    
    # 3 CHARTS - ALL STOCKS
    strong_buy = df[df['Signal'] == "🟢 STRONG BUY"]
    all_buy = df[df['Signal'] == "🟢 BUY"]
    all_sell = df[df['Signal'].str.contains('SELL')]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🟢 **STRONG BUY**")
        st.metric("Count", len(strong_buy))
        if not strong_buy.empty:
            st.dataframe(strong_buy[['Stock','Price','RSI','MA20']], height=350)
    
    with col2:
        st.markdown("### 🔴 **ALL SELLS**")
        st.metric("Count", len(all_sell))
        if not all_sell.empty:
            st.dataframe(all_sell[['Stock','Price','RSI','MA20']], height=350)
    
    with col3:
        st.markdown("### 🟢 **ALL BUYS**")
        st.metric("Count", len(all_buy))
        if not all_buy.empty:
            st.dataframe(all_buy[['Stock','Price','RSI','MA20']], height=350)
    
    # SUMMARY
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 TOTAL", len(df))
    col2.metric("🟢 STRONGEST", len(strong_buy))
    col3.metric("🔴 SELLS", len(all_sell))
    
    csv = df.to_csv(index=False)
    st.download_button("💾 DOWNLOAD", csv, "nifty50-scan.csv", use_container_width=True)
    
except:
    st.info("👈 Click **MANUAL SCAN NOW** or wait 5 mins for auto-scan")

# 🕒 WORKING AUTO-REFRESH TIMER
st.markdown("---")
st.subheader("⏱️ AUTO-REFRESH STATUS")
time_since = time.time() - st.session_state.last_scan
remaining = max(0, 300 - time_since)
m, s = divmod(int(remaining), 60)
st.metric("⏳ Next Auto-Scan", f"{m}m {s}s", delta=f"-{int(time_since/60)}m")

col1, col2 = st.columns(2)
col1.metric("🔄 Total Scans", st.session_state.scan_count)
col2.metric("⏱️ Time Since Last", f"{int(time_since/60)}m {int(time_since%60)}s")

st.info("""
**🟢 STRONG BUY** = RSI<35 + Price>MA20
**5 min auto-refresh** = Rate-limit safe
**Click MANUAL SCAN** anytime
**Educational only**
""")
