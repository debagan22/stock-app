import streamlit as st
import yfinance as yf
import pandas as pd
import ta

st.title("🇮🇳 Indian Stock Analyzer")

symbol = st.text_input("Enter stock (RELIANCE.NS, TCS.NS):").upper()

if symbol:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="3mo")
    
    if not data.empty:
        data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        macd = ta.trend.MACD(data['Close'])
        data['MACD'] = macd.macd()
        data['Signal'] = macd.macd_signal()
        
        st.line_chart(data[['Close', 'MACD', 'Signal']])
        
        latest = data.iloc[-1]
        col1, col2 = st.columns(2)
        col1.metric("Price", f"₹{latest['Close']:.2f}")
        col2.metric("RSI", f"{latest['RSI']:.1f}")
        
        if latest['RSI'] < 30:
            st.success("🟢 BUY signal")
        elif latest['RSI'] > 70:
            st.error("🔴 SELL signal")
        else:
            st.info("🟡 HOLD")
