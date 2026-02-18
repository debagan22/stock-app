import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.title("🔥 NIFTY FULL MARKET SCANNER")
st.markdown("**Scans 50+ major NIFTY stocks automatically**")

# FULL NIFTY 50 + major stocks list
nifty_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "HCLTECH.NS", "WIPRO.NS", "TITAN.NS",
    "NESTLEIND.NS", "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "COALINDIA.NS", "BAJFINANCE.NS", "GRASIM.NS",
    "HDFCLIFE.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "BAJAJFINSV.NS", "LTIM.NS",
    "ADANIPORTS.NS", "SHRIRAMFIN.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS",
    "HCLTECH.NS", "TATACONSUM.NS", "TRENT.NS", "SHRIRAMCIT.NS"
]

if st.button("🚀 SCAN ALL STOCKS", type="primary"):
    st.spinner("Scanning full market...")
    results = []
    progress = st.progress(0)
    
    for i, symbol in enumerate(nifty_stocks):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="20d")
            
            if len(data) < 10:
                progress.progress((i+1) / len(nifty_stocks))
                continue
            
            # RSI Analysis
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            latest_rsi = data['RSI'].iloc[-1]
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100
            
            # Single Signal column
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
            
            time.sleep(0.7)  # Rate limit safe
            
        except:
            pass
        
        progress.progress((i+1) / len(nifty_stocks))
    
    # Show ALL results
    df = pd.DataFrame(results)
    st.success(f"✅ Scanned **{len(df)} stocks**!")
    st.dataframe(df, use_container_width=True, height=600)
    
    # Summary
    buy_count = len(df[df['Signal']=='🟢 BUY'])
    sell_count = len(df[df['Signal']=='🔴 SELL'])
    hold_count = len(df[df['Signal']=='🟡 HOLD'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 BUY", buy_count)
    col2.metric("🔴 SELL", sell_count)
    col3.metric("🟡 HOLD", hold_count)
    
    # Download
    csv = df.to_csv(index=False)
    st.download_button("📥 Download Full CSV", csv, "nifty_full_scan.csv")

st.caption("**Scans 47 major NIFTY stocks** - Click SCAN ALL STOCKS!")
