import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Initialize session state
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = time.time()
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 0
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'failed' not in st.session_state:
    st.session_state.failed = 0
if 'total' not in st.session_state:
    st.session_state.total = 0
if 'refresh_trigger' not in st.session_state:
    st.session_state.refresh_trigger = 0

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 500 RSI + MA SCANNER")
st.markdown("**500 stocks | 4 TABS + LIVE COUNTDOWN | Auto + Manual Refresh**")

# NIFTY 500 stocks (100 for speed)
nifty500 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "LTIM.NS", "SUNPHARMA.NS", 
    "HCLTECH.NS", "TITAN.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "TECHM.NS", "POWERGRID.NS", "WIPRO.NS", "TATAMOTORS.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "COALINDIA.NS", "NTPC.NS", "ONGC.NS", "M&M.NS", "BAJAJFINSV.NS",
    "BEL.NS", "TATACONSUM.NS", "GRASIM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS",
    "TRENT.NS", "VARUNBEV.NS", "LICI.NS", "BAJAJ-AUTO.NS", "SHRIRAMFIN.NS"
]

@st.cache_data(ttl=300)
def scan_nifty500():
    results = []
    failed = 0
    
    for symbol in nifty500:
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
                'RSI': float(rsi),
                'MA20': float(ma20),
                'Signal': signal
            })
            time.sleep(0.2)
        except:
            failed += 1
    
    return pd.DataFrame(results), failed, len(nifty500)

# 🔥 CONTROL BUTTONS WITH REFRESH TRIGGER
col1, col2, col3, col4 = st.columns([2.5, 1, 1, 1])
with col1:
    if st.button("🔥 MANUAL SCAN NOW", type="primary", use_container_width=True, key="scan_main"):
        with st.spinner("Scanning NIFTY 500..."):
            df, failed, total = scan_nifty500()
            st.session_state.df = df
            st.session_state.failed = failed
            st.session_state.total = total
            st.session_state.last_scan = time.time()
            st.session_state.scan_count += 1
        st.session_state.refresh_trigger += 1
        st.rerun()

with col2:
    if st.button("🔄 REFRESH DATA", use_container_width=True, key="refresh_data"):
        st.cache_data.clear()
        st.session_state.refresh_trigger += 1
        st.rerun()

with col3:
    if st.button("⏹️ PAUSE AUTO", use_container_width=True, key="pause_auto"):
        st.session_state.last_scan = time.time() + 10000

with col4:
    if st.button("🔄 TICK NOW", use_container_width=True, key="tick_now"):
        st.session_state.refresh_trigger += 1
        st.rerun()

# AUTO-REFRESH
time_since_scan = time.time() - st.session_state.last_scan
if time_since_scan > 300 or st.session_state.scan_count == 0:
    with st.spinner("Auto-scanning NIFTY 500..."):
        df, failed, total = scan_nifty500()
        st.session_state.df = df
        st.session_state.failed = failed
        st.session_state.total = total
        st.session_state.last_scan = time.time()
        st.session_state.scan_count += 1

# 🔥 4 TABS DISPLAY
if not st.session_state.df.empty:
    df = st.session_state.df
    failed = st.session_state.failed
    total = st.session_state.total
    
    st.success(f"✅ SUCCESS: {len(df)}/{total-failed} stocks | Scan #{st.session_state.scan_count}")
    
    strong_buy = df[df['Signal'] == "🟢 STRONG BUY"].copy()
    all_sell = df[df['Signal'].str.contains('SELL', na=False)].copy()
    all_buy = df[df['Signal'] == "🟢 BUY"].copy()
    all_hold = df[df['Signal'] == "🟡 HOLD"].copy()
    
    tab1, tab2, tab3, tab4 = st.tabs(["🟢 STRONG BUY", "🔴 SELL", "🟢 BUY", "🟡 HOLD"])
    
    with tab1:
        st.markdown("### 🟢 **STRONG BUY** (RSI<35 + Price>MA20)")
        col1, col2 = st.columns(2)
        col1.metric("Count", len(strong_buy))
        col2.metric("Lowest RSI", round(strong_buy['RSI'].min(), 1) if not strong_buy.empty else 0)
        if not strong_buy.empty:
            st.dataframe(strong_buy[['Stock','Price','RSI','MA20']].sort_values('RSI'), height=400, use_container_width=True)
    
    with tab2:
        st.markdown("### 🔴 **SELL** (RSI>65/70)")
        col1, col2 = st.columns(2)
        col1.metric("Count", len(all_sell))
        col2.metric("Highest RSI", round(all_sell['RSI'].max(), 1) if not all_sell.empty else 0)
        if not all_sell.empty:
            st.dataframe(all_sell[['Stock','Price','RSI','MA20']].sort_values('RSI', ascending=False), height=400, use_container_width=True)
    
    with tab3:
        st.markdown("### 🟢 **BUY** (RSI<30)")
        col1, col2 = st.columns(2)
        col1.metric("Count", len(all_buy))
        col2.metric("Lowest RSI", round(all_buy['RSI'].min(), 1) if not all_buy.empty else 0)
        if not all_buy.empty:
            st.dataframe(all_buy[['Stock','Price','RSI','MA20']].sort_values('RSI'), height=400, use_container_width=True)
    
    with tab4:
        st.markdown("### 🟡 **HOLD** (RSI 30-70)")
        col1, col2 = st.columns(2)
        col1.metric("Count", len(all_hold))
        col2.metric("Avg RSI", round(all_hold['RSI'].mean(), 1) if not all_hold.empty else 0)
        if not all_hold.empty:
            st.dataframe(all_hold[['Stock','Price','RSI','MA20']].head(20), height=400, use_container_width=True)
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎯 TOTAL", len(df))
    col2.metric("🟢 STRONG BUY", len(strong_buy))
    col3.metric("🔴 SELLS", len(all_sell))
    col4.metric("🟡 HOLD", len(all_hold))
    
    csv = df.to_csv(index=False)
    st.download_button("💾 DOWNLOAD CSV", csv, "nifty500-complete.csv", use_container_width=True)

else:
    st.info("👈 Click **MANUAL SCAN NOW** to start")

# 🔥 **LIVE COUNTDOWN TIMER** - Updates on EVERY interaction
st.markdown("---")
st.subheader("⏱️ **LIVE COUNTDOWN**")

time_since = time.time() - st.session_state.last_scan
remaining = max(0, 300 - time_since)
m, s = divmod(int(remaining), 60)

# VISUAL INDICATOR: Timer color + refresh button
timer_color = "#ff4b2b" if remaining < 60 else "#56ab2f" if remaining < 180 else "#ffa500"
refresh_icon = "🔴" if remaining < 60 else "🟡" if remaining < 180 else "🟢"

st.markdown(f"""
<div style='text-align: center; font-size: 6rem; font-weight: bold; 
     color: {timer_color}; 
     background: linear-gradient(45deg, #f8f9fa, #e9ecef); 
     padding: 3rem; border-radius: 30px; border: 6px solid {timer_color};
     box-shadow: 0 15px 40px rgba(0,0,0,0.3);'>
    ⏳ **{m}:{s:02d}**
</div>
<div style='text-align: center; font-size: 1.5rem; color: #666; font-weight: 500; margin-top: 1rem;'>
    {refresh_icon} Click **🔄 TICK NOW** to update timer | Auto-scan in **{m}m {s}s**
</div>
""", unsafe_allow_html=True)

# TIMER CONTROLS
col1, col2, col3 = st.columns(3)
col1.metric("🔄 Scans Done", st.session_state.scan_count)
col2.metric("⏱️ Since Last Scan", f"{int(time_since//60):02d}:{int(time_since%60):02d}")
col3.metric("📊 Stocks Scanned", len(st.session_state.df) if not st.session_state.df.empty else 0)

st.info("""
**✅ HOW TIMER WORKS** (Streamlit limitation):
• Timer **UPDATES on every click/refresh** 
• Click **🔄 TICK NOW** anytime to see live countdown
• **🔴 RED** = <1min | **🟡 YELLOW** = <3min | **🟢 GREEN** = Safe
• Auto-scan triggers at **0:00**
**🟢 STRONG BUY** = RSI<35 + Price>MA20 | **4 TABS** show all stocks!
""")
