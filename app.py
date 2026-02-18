import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("🤖 Indian Stock Auto Analyzer")
st.markdown("**Scans top NIFTY stocks & gives BUY/HOLD/SELL signals**")

# Top 10 NIFTY stocks (change as needed)
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
          "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"]

@st.cache_data(ttl=600)  # Refresh every 10 mins
def analyze_stock(symbol):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="3mo")
    if data.empty:
        return None
    
    # Calculate indicators
    data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['Signal'] = macd.macd_signal()
    
    latest = data.iloc[-1]
    price = latest['Close']
    
    # Smart signals
    rsi = latest['RSI']
    macd_status = "bull" if latest['MACD'] > latest['Signal'] else "bear"
    
    if rsi < 30 and macd_status == "bull":
        signal = "🟢 BUY"
    elif rsi > 70 or macd_status == "bear":
        signal = "🔴 SELL" 
    else:
        signal = "🟡 HOLD"
    
    return {
        'Symbol': symbol.replace('.NS',''),
        'Price': f"₹{price:.2f}",
        'RSI': f"{rsi:.1f}",
        'Signal': signal
    }

# Analyze all stocks
progress = st.progress(0)
results = []

for i, symbol in enumerate(stocks):
    result = analyze_stock(symbol)
    if result:
        results.append(result)
    progress.progress((i+1) / len(stocks))

# Results table
st.subheader("📊 Latest Analysis")
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True)

# Summary
buys = len(df[df['Signal'] == '🟢 BUY'])
sells = len(df[df['Signal'] == '🔴 SELL'])
holds = len(df[df['Signal'] == '🟡 HOLD'])

col1, col2, col3 = st.columns(3)
col1.metric("🟢 BUY", buys)
col2.metric("🔴 SELL", sells) 
col3.metric("🟡 HOLD", holds)

st.info(f"**Market Summary**: {buys} BUY | {sells} SELL | {holds} HOLD signals")
st.warning("⚠️ For education only - not financial advice!")
