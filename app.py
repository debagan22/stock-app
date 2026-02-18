import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("🔴 LIVE Indian Stock Analyzer")
st.markdown("**Auto-refreshes every 30s with real-time BUY/SELL signals**")

# Top NIFTY stocks
stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", 
          "ICICIBANK.NS", "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS"]

# Auto-refresh button
if st.button("🔄 Refresh Now") or st.session_state.get('refresh', False):
    st.session_state.refresh = True
    st.rerun()

# Auto-refresh timer
placeholder = st.empty()
with placeholder.container():
    st.write("⏱️ **Next auto-refresh:** 30s")
    
    # Analyze all stocks
    progress = st.progress(0)
    results = []
    
    for i, symbol in enumerate(stocks):
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1mo")  # More recent data for faster load
        
        if not data.empty:
            # Real-time indicators
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            macd = ta.trend.MACD(data['Close'])
            data['MACD'] = macd.macd()
            data['MACD_Signal'] = macd.macd_signal()
            
            latest = data.iloc[-1]
            price = latest['Close']
            change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            
            # Live signals
            rsi = latest['RSI']
            macd_bull = latest['MACD'] > latest['MACD_Signal']
            
            if rsi < 35 and macd_bull and change > 0:
                signal = "🟢 **STRONG BUY**"
            elif rsi > 65 or not macd_bull:
                signal = "🔴 **SELL**"
            else:
                signal = "🟡 **HOLD**"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                '₹ Price': f"{price:.2f}",
                'Chg %': f"{change:+.2f}%",
                'RSI': f"{rsi:.1f}",
                'Signal': signal
            })
        
        progress.progress((i+1) / len(stocks))
    
    # Live results table
    df = pd.DataFrame(results)
    st.subheader("📈 **LIVE MARKET SIGNALS**")
    st.dataframe(df, use_container_width=True, height=400)
    
    # Live summary
    buys = len(df[df['Signal'].str.contains('BUY')])
    sells = len(df[df['Signal'].str.contains('SELL')])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 STRONG BUY", buys)
    col2.metric("🔴 SELL", sells)
    col3.metric("🟡 HOLD", len(stocks) - buys - sells)
    
    st.markdown(f"---")
    st.caption("⚠️ Educational tool only - not financial advice. Data from Yahoo Finance")

# Auto-refresh countdown
time.sleep(30)
st.rerun()
