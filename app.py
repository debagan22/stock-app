import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("📊 NIFTY SCANNER")
st.markdown("**Stock Analyzer**")

nifty_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS"
]

@st.cache_data(ttl=60)
def scan_market():
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
            time.sleep(0.6)
        except:
            pass
    return pd.DataFrame(results)

# LIVE DATA
df = scan_market()
st.success(f"✅ Scanned {len(df)} stocks (Auto-refresh 60s)")

# SPLIT INTO 3 DATAFRAMES
buy_df = df[df['Signal'] == '🟢 BUY'].copy()
sell_df = df[df['Signal'] == '🔴 SELL'].copy()
hold_df = df[df['Signal'] == '🟡 HOLD'].copy()

# 3 SIDE-BY-SIDE CHARTS
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🟢 **BUY STOCKS**")
    if not buy_df.empty:
        st.metric("Count", len(buy_df))
        st.dataframe(buy_df[['Stock', 'Price', 'RSI']], height=300)
    else:
        st.info("No BUY signals")

with col2:
    st.subheader("🔴 **SELL STOCKS**")
    if not sell_df.empty:
        st.metric("Count", len(sell_df))
        st.dataframe(sell_df[['Stock', 'Price', 'RSI']], height=300)
    else:
        st.info("No SELL signals")

with col3:
    st.subheader("🟡 **HOLD STOCKS**")
    if not hold_df.empty:
        st.metric("Count", len(hold_df))
        st.dataframe(hold_df[['Stock', 'Price', 'RSI']], height=300)
    else:
        st.info("No HOLD signals")

# OVERALL SUMMARY
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("🟢 BUY", len(buy_df))
col2.metric("🔴 SELL", len(sell_df))
col3.metric("🟡 HOLD", len(hold_df))

st.caption("⏱️ Auto-refreshes every 60s | 📥 CSV below")
st.dataframe(df, height=200)
