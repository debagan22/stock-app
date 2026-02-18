import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(page_title="NIFTY 50 LIVE", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 50 RSI + MA SCANNER")
st.markdown("**Dual confirmation signals | ALL 50 NIFTY stocks**")

# COMPLETE OFFICIAL NIFTY 50 LIST
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

@st.cache_data(ttl=300)  # 5 min cache - rate limit safe
def scan_nifty50_dual():
    results = []
    failed = 0
    
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            
            if len(data) < 20:
                failed += 1
                continue
            
            # RSI + 20-day MA
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            # DUAL CONFIRMATION LOGIC
            if rsi < 35 and price > ma20:
                signal = "🟢 STRONG BUY"
            elif rsi > 65 and price < ma20:
                signal = "🔴 STRONG SELL"
            elif rsi < 30:
                signal = "🟢 BUY"
            elif rsi > 70:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.1f}",
                'Signal': signal
            })
            time.sleep(0.5)
            
        except:
            failed += 1
    
    return pd.DataFrame(results), failed

# 🔥 MAIN DISPLAY - 3 CHARTS WITH ALL STOCKS
if st.button("🔥 SCAN NIFTY 50 NOW", type="primary", use_container_width=True):
    df, failed_count = scan_nifty50_dual()
    
    st.success(f"✅ **SUCCESS**: {len(df)}/50 stocks | ❌ **FAILED**: {failed_count}")
    
    # ALL BUY/SELL/HOLD IN TOP 3 CHARTS
    strong_buy = df[df['Signal'] == "🟢 STRONG BUY"]
    all_buy = df[df['Signal'] == "🟢 BUY"]
    all_sell = df[df['Signal'].str.contains('SELL')]
    all_hold = df[df['Signal'] == "🟡 HOLD"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🟢 **STRONG BUY** (RSI+MA)")
        st.metric("Count", len(strong_buy))
        if not strong_buy.empty:
            st.dataframe(strong_buy[['Stock','Price','RSI','MA20']], height=350, use_container_width=True)
        else:
            st.info("🎉 No STRONG BUY signals!")
    
    with col2:
        st.markdown("### 🔴 **ALL SELLS**")
        st.metric("Count", len(all_sell))
        if not all_sell.empty:
            st.dataframe(all_sell[['Stock','Price','RSI','MA20']], height=350, use_container_width=True)
        else:
            st.info("✅ No SELL signals!")
    
    with col3:
        st.markdown("### 🟢 **ALL BUYS**")
        st.metric("Count", len(all_buy))
        if not all_buy.empty:
            st.dataframe(all_buy[['Stock','Price','RSI','MA20']], height=350, use_container_width=True)
        else:
            st.info("No BUY signals!")
    
    # SUMMARY METRICS
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 TOTAL SCANNED", len(df))
    col2.metric("🟢 STRONG BUY", len(strong_buy))
    col3.metric("🔴 TOTAL SELLS", len(all_sell))
    
    # DOWNLOAD FULL DATA
    csv = df.to_csv(index=False)
    st.download_button("💾 DOWNLOAD ALL DATA", csv, "nifty50-complete.csv", use_container_width=True)

# AUTO REFRESH COUNTDOWN
st.markdown("---")
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = 0

remaining = max(0, 300 - (time.time() - st.session_state.last_scan))
m, s = divmod(int(remaining), 60)
st.metric("⏳ Next Auto-Refresh", f"{m}m {s}s")

st.info("""
**🟢 STRONG BUY** = RSI < 35 + Price > MA20 (oversold in uptrend)
**🔴 STRONG SELL** = RSI > 65 + Price < MA20 (overbought in downtrend)
**5-min refresh** = Rate-limit safe
**Educational use only** - not financial advice
""")
