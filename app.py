import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("🔥 NIFTY 500 FULL SCANNER")
st.markdown("**Nifty Analyzer**")

# Load NIFTY 500 symbols (top 50 for demo - full list in comments)
nifty500 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "HCLTECH.NS", "WIPRO.NS", "TITAN.NS",
    "NESTLEIND.NS", "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "NESTLEIND.NS", "COALINDIA.NS", "BAJFINANCE.NS",
    "GRASIM.NS", "HDFCLIFE.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "BAJAJFINSV.NS", "LTIM.NS",
    "ADANIPORTS.NS", "SHRIRAMFIN.NS", "TATASTEEL.NS", "UPL.NS", "BAJAJ-AUTO.NS"
    # Add full 500 from: https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv
]

if st.button("🚀 SCAN ALL 500 STOCKS", type="primary", help="Takes 8-10 mins"):
    with st.spinner("Scanning NIFTY 500..."):
        results = []
        progress = st.progress(0)
        
        for i, symbol in enumerate(nifty500):
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="20d", interval="1d")  # Fast data
                if len(data) < 10: 
                    progress.progress((i+1) / len(nifty500))
                    continue
                
                # Indicators
                data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
                latest_rsi = data['RSI'].iloc[-1]
                
                price = data['Close'].iloc[-1]
                change = ((price - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100
                
                # BUY/SELL/HOLD logic
                buy_signal = 1 if latest_rsi < 35 else 0
                sell_signal = 1 if latest_rsi > 65 else 0
                hold_signal = 1 if 35 <= latest_rsi <= 65 else 0
                
                results.append({
                    'Stock': symbol.replace('.NS',''),
                    'Price': f"₹{price:.1f}",
                    'Chg%': f"{change:+.1f}%",
                    'RSI': f"{latest_rsi:.1f}",
                    'BUY', buy_signal,
                    'SELL', sell_signal,
                    'HOLD', hold_signal
                })
                
                time.sleep(0.8)  # Safe delay
            except:
                pass
            
            progress.progress((i+1) / len(nifty500))
        
        # Results
        df = pd.DataFrame(results)
        st.success(f"✅ Scanned {len(df)} stocks!")
        
        st.subheader("📊 FULL RESULTS")
        st.dataframe(df, use_container_width=True)
        
        # Summary
        total_buy = df['BUY'].sum()
        total_sell = df['SELL'].sum()
        total_hold = df['HOLD'].sum()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 BUY", total_buy, delta=f"{total_buy/len(df)*100:.1f}%")
        col2.metric("🔴 SELL", total_sell, delta=f"{total_sell/len(df)*100:.1f}%")
        col3.metric("🟡 HOLD", total_hold, delta=f"{total_hold/len(df)*100:.1f}%")
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button("📥 Download Full Data", csv, "nifty500_signals.csv")

st.info("""
**To scan ALL 500 stocks:**
1. Download full list: https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv 
2. Replace `nifty500 = [...]` with full symbols + ".NS"
3. Takes ~10 mins but scans entire market!
""")
