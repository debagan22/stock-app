import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
from concurrent.futures import ThreadPoolExecutor

st.title("🔴 LIVE Indian Stock Analyzer")
st.markdown("**Live Updates 30 Sec**")

stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
          "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"]

@st.cache_data(ttl=1200)  # Cache 20 mins
def safe_fetch(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo", timeout=10)
        if data.empty:
            return None
        
        # Quick indicators (less computation)
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        macd = ta.trend.MACD(data['Close'], window_slow=26, window_fast=12)
        latest = data.iloc[-1]
        
        rsi = latest['RSI']
        price = latest['Close']
        change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) > 1 else 0
        
        # Simple signals
        if rsi < 35:
            signal = "🟢 BUY"
        elif rsi > 65:
            signal = "🔴 SELL"
        else:
            signal = "🟡 HOLD"
            
        return {
            'Stock': symbol.replace('.NS',''),
            '₹Price': f"{price:.2f}",
            'Chg%': f"{change:+.1f}%",
            'RSI': f"{rsi:.1f}",
            'Signal': signal
        }
    except:
        return None

# Manual refresh only (no auto)
if st.button("🔄 ANALYZE MARKET NOW", type="primary"):
    with st.spinner("Scanning 10 stocks..."):
        results = []
        progress = st.progress(0)
        
        for i, symbol in enumerate(stocks):
            result = safe_fetch(symbol)
            if result:
                results.append(result)
            time.sleep(1)  # 1 sec delay between requests
            progress.progress((i+1) / len(stocks))
    
    if results:
        df = pd.DataFrame(results)
        st.success("✅ Analysis Complete!")
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Summary stats
        buys = len(df[df['Signal']=='🟢 BUY'])
        sells = len(df[df['Signal']=='🔴 SELL'])
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 BUY", buys)
        col2.metric("🔴 SELL", sells)
        col3.metric("🟡 HOLD", len(results)-buys-sells)
        
        st.balloons()
    else:
        st.error("No data received. Try again in 5 mins.")

st.info("👉 Click ANALYZE button for fresh data. Wait 15s between clicks.")
st.caption("⚠️ Educational use only - not financial advice")
