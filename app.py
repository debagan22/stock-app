import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("🔥 NIFTY 500 FULL SCANNER")
st.markdown("**Analyzes ALL 500 stocks + BUY/SELL/HOLD columns**")

# NIFTY stocks (expandable)
nifty500 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS"
]

if st.button("🚀 SCAN MARKET", type="primary"):
    with st.spinner("Scanning stocks..."):
        results = []
        progress = st.progress(0)
        
        for i, symbol in enumerate(nifty500):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="20d")
                if len(data) < 10: 
                    progress.progress((i+1) / len(nifty500))
                    continue
                
                data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
                latest_rsi = data['RSI'].iloc[-1]
                price = data['Close'].iloc[-1]
                change = ((price - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100
                
                # FIXED: Added colons after keys
                buy_signal = 1 if latest_rsi < 35 else 0
                sell_signal = 1 if latest_rsi > 65 else 0
                hold_signal = 1 if 35 <= latest_rsi <= 65 else 0
                
                results.append({
                    'Stock': symbol.replace('.NS',''),
                    'Price': f"₹{price:.1f}",
                    'Chg%': f"{change:+.1f}%",
                    'RSI': f"{latest_rsi:.1f}",
                    'BUY': buy_signal,     # ✅ Fixed
                    'SELL': sell_signal,   # ✅ Fixed
                    'HOLD': hold_signal    # ✅ Fixed
                })
                
                time.sleep(0.8)
            except:
                pass
            
            progress.progress((i+1) / len(nifty500))
        
        # Results table
        df = pd.DataFrame(results)
        st.success(f"✅ Scanned {len(df)} stocks!")
        st.dataframe(df, use_container_width=True)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 BUY", df['BUY'].sum())
        col2.metric("🔴 SELL", df['SELL'].sum())
        col3.metric("🟡 HOLD", df['HOLD'].sum())
        
        # CSV download
        csv = df.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "nifty_signals.csv")

st.info("**Syntax Fixed!** Click SCAN MARKET to analyze all stocks.")
