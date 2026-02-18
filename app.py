import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("🔴 LIVE NIFTY SCANNER - Auto Refresh")
st.markdown("**Scans 47 stocks + auto-refreshes every 60s**")

# 47 major NIFTY stocks
nifty_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "HCLTECH.NS", "WIPRO.NS", "TITAN.NS",
    "NESTLEIND.NS", "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "COALINDIA.NS", "BAJFINANCE.NS", "GRASIM.NS",
    "HDFCLIFE.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "BAJAJFINSV.NS", "LTIM.NS",
    "ADANIPORTS.NS", "SHRIRAMFIN.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS"
]

@st.cache_data(ttl=50)  # Cache 50s (refresh every 60s)
def scan_stocks():
    results = []
    for symbol in nifty_stocks:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="20d")
            if len(data) < 10: continue
            
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            latest_rsi = data['RSI'].iloc[-1]
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100
            
            if latest_rsi < 35:
                signal = "🟢 BUY"
            elif latest_rsi > 65:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'Change': f"{change:+.1f}%",
                'RSI': f"{latest_rsi:.1f}",
                'Signal': signal
            })
            time.sleep(0.5)  # Rate limit protection
        except:
            pass
    return pd.DataFrame(results)

# AUTO-REFRESH COUNTDOWN
countdown = 60
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = 0

# Show live data
df = scan_stocks()
st.success(f"✅ LIVE: Scanned **{len(df)} stocks**")

st.subheader("📊 REAL-TIME RESULTS")
st.dataframe(df, use_container_width=True, height=600)

# Live summary
buy_count = len(df[df['Signal']=='🟢 BUY'])
sell_count = len(df[df['Signal']=='🔴 SELL'])
hold_count = len(df[df['Signal']=='🟡 HOLD'])

col1, col2, col3 = st.columns(3)
col1.metric("🟢 BUY", buy_count)
col2.metric("🔴 SELL", sell_count)
col3.metric("🟡 HOLD", hold_count)

# COUNTDOWN TIMER
st.markdown("---")
st.info(f"⏱️ **Next auto-refresh: {countdown - int(time.time() - st.session_state.last_scan)}s**")
st.session_state.last_scan = time.time()

# Download
csv = df.to_csv(index=False)
st.download_button("📥 Download CSV", csv, "live_nifty_scan.csv")

# FORCE REFRESH EVERY 60s
time.sleep(60)
st.rerun()
