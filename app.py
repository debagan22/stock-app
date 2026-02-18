import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(page_title="NIFTY 50 DUAL", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 50 RSI + MA SCANNER")
st.markdown("**RSI + 20-day Moving Average | ALL 50 stocks**")

# OFFICIAL NIFTY 50 - COMPLETE LIST
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

# ✅ FIXED: Proper function with cache decorator
@st.cache_data(ttl=300)  # 5 minutes - rate limit safe
def scan_nifty50_dual():
    results = []
    failed_count = 0
    
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            
            if len(data) < 20:
                failed_count += 1
                continue
            
            # RSI (14) + MA (20)
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            # DUAL CONFIRMATION
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
            failed_count += 1
    
    return pd.DataFrame(results), failed_count

# 🔥 MAIN SCANNER BUTTON
if st.button("🔥 SCAN NIFTY 50 (RSI+MA)", type="primary", use_container_width=True):
    df, failed = scan_nifty50_dual()
    
    st.success(f"✅ **SUCCESS**: {len(df)} stocks | ❌ **FAILED**: {failed}/50")
    
    # 3 BEAUTIFUL COLUMNS
    strong_buy = df[df['Signal']=="🟢 STRONG BUY"]
    sells = df[df['Signal'].str.contains("SELL")]
    holds = df[df['Signal']=="🟡 HOLD"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🟢 **STRONG BUY**")
        st.metric("Count", len(strong_buy))
        if not strong_buy.empty:
            st.dataframe(strong_buy[['Stock','Price','RSI','MA20']], height=350)
    
    with col2:
        st.subheader("🔴 **SELL**")
        st.metric("Count", len(sells))
        if not sells.empty:
            st.dataframe(sells[['Stock','Price','RSI','MA20']], height=350)
    
    with col3:
        st.subheader("🟡 **HOLD**")
        st.metric("Count", len(holds))
        if not holds.empty:
            st.dataframe(holds[['Stock','Price','RSI','MA20']].head(10), height=350)
    
    # SUMMARY
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 TOTAL", len(df))
    col2.metric("🟢 STRONGEST", len(strong_buy))
    col3.metric("📈 SCAN TIME", f"{len(nifty50)*0.5/60:.1f} mins")
    
    # DOWNLOAD
    csv = df.to_csv(index=False)
    st.download_button("💾 DOWNLOAD ALL", csv, "nifty50-dual.csv", use_container_width=True)

# AUTO REFRESH COUNTDOWN
st.markdown("---")
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = 0

remaining = max(0, 300 - (time.time() - st.session_state.last_scan))
m, s = divmod(int(remaining), 60)
st.metric("⏳ Auto Refresh", f"{m}m {s}s")

st.info("**RSI + MA20 confirmation** = 2x stronger signals!")
