import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(page_title="NIFTY 50 DUAL", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 50 RSI + MA SCANNER")
st.markdown("**RSI + 20-day Moving Average Confirmation | ALL 50 stocks**")

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
def scan_nifty50_dual():
    results = []
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")  # Need 30 days for MA
            if len(data) < 20: continue
            
            # RSI (14-day)
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            rsi = data['RSI'].iloc[-1]
            
            # 20-day Simple Moving Average
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            # ✅ DUAL CONFIRMATION LOGIC
            if rsi < 35 and price > ma20:  # RSI oversold + Above MA (bullish trend)
                signal = "🟢 STRONG BUY"
            elif rsi > 65 and price < ma20:  # RSI overbought + Below MA (bearish trend)
                signal = "🔴 STRONG SELL"
            elif rsi < 30 or (rsi < 40 and price > ma20):  # Pure oversold or pullback in uptrend
                signal = "🟢 BUY"
            elif rsi > 70 or (rsi > 60 and price < ma20):  # Pure overbought or pullback in downtrend
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.1f}",
                'Trend': "📈" if price > ma20 else "📉",
                'Signal': signal
            })
            time.sleep(0.5)
        except:
            pass
    return pd.DataFrame(results)

# 🔥 LIVE SCANNER
if st.button("🔥 SCAN NIFTY 50 (RSI+MA)", type="primary", use_container_width=True):
    df = scan_nifty50_dual()
    
    # 3 CONFIRMED SIGNAL CHARTS
    strong_buy = df[df['Signal']=="🟢 STRONG BUY"]
    buy = df[df['Signal']=="🟢 BUY"]
    sell = df[(df['Signal']=="🔴 STRONG SELL") | (df['Signal']=="🔴 SELL")]
    hold = df[df['Signal']=="🟡 HOLD"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🟢 **STRONG BUY** (RSI+MA)")
        st.metric("Count", len(strong_buy))
        st.dataframe(strong_buy[['Stock','Price','RSI','MA20']], height=350)
    
    with col2:
        st.subheader("🔴 **SELL** (RSI+MA)")
        st.metric("Count", len(sell))
        st.dataframe(sell[['Stock','Price','RSI','MA20']], height=350)
    
    with col3:
        st.subheader("🟡 **HOLD/WATCH**")
        st.metric("Count", len(hold))
        st.dataframe(hold[['Stock','Price','RSI','MA20']].head(10), height=350)
    
    # 📊 SUMMARY
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 TOTAL", len(df))
    col2.metric("🟢 STRONG BUY", len(strong_buy))
    col3.metric("🔴 CONFIRMED SELL", len(sell))
    
    csv = df.to_csv(index=False)
    st.download_button("💾 DOWNLOAD FULL DATA", csv, "nifty50-dual.csv")

st.success("✅ **RSI + 20-day MA Confirmation** | Much stronger signals!")
st.info("**Logic**: RSI oversold + price above MA20 = STRONG BUY\nRSI overbought + price below MA20 = STRONG SELL")
