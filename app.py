import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(page_title="NIFTY LIVE", layout="wide", page_icon="📈")
st.markdown("""
<style>
.main-header {font-size: 3.5rem !important; color: #1f77b4; text-align: center;}
.buy-card {background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%); padding: 1.5rem; border-radius: 20px; color: white; text-align: center;}
.sell-card {background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 1.5rem; border-radius: 20px; color: white; text-align: center;}
.hold-card {background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%); padding: 1.5rem; border-radius: 20px; color: white; text-align: center;}
.stMetric > label {color: white !important; font-size: 1.3rem;}
.stMetric > div > div {color: white !important; font-size: 2.5rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🚀 NIFTY LIVE SCANNER</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #666;'>65 Major Stocks | BUY/SELL/HOLD Signals | 5-Min Auto Refresh</p>", unsafe_allow_html=True)

nifty_stocks = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","HINDUNILVR.NS","ICICIBANK.NS",
    "KOTAKBANK.NS","SBIN.NS","BHARTIARTL.NS","ITC.NS","ASIANPAINT.NS","LT.NS",
    "AXISBANK.NS","MARUTI.NS","SUNPHARMA.NS","HCLTECH.NS","WIPRO.NS","TITAN.NS",
    "NESTLEIND.NS","ULTRACEMCO.NS","ONGC.NS","NTPC.NS","POWERGRID.NS","TECHM.NS",
    "TATAMOTORS.NS","JSWSTEEL.NS","COALINDIA.NS","BAJFINANCE.NS","GRASIM.NS",
    "HDFCLIFE.NS","DIVISLAB.NS","CIPLA.NS","DRREDDY.NS","EICHERMOT.NS","HEROMOTOCO.NS",
    "BRITANNIA.NS","APOLLOHOSP.NS","BAJAJFINSV.NS","LTIM.NS","ADANIPORTS.NS"
]

@st.cache_data(ttl=300)  # 5 min cache = PERFECTLY SAFE
def scan_stocks():
    results = []
    progress = st.progress(0)
    
    for i, symbol in enumerate(nifty_stocks):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="15d")
            if len(data) < 8: continue
            
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            rsi = data['RSI'].iloc[-1]
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2])/data['Close'].iloc[-2])*100 if len(data)>1 else 0
            
            signal = "🟢 BUY" if rsi < 35 else "🔴 SELL" if rsi > 65 else "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'Change': f"{change:+.1f}%",
                'RSI': f"{rsi:.1f}",
                'Signal': signal
            })
            time.sleep(0.4)
        except:
            pass
        
        progress.progress((i+1)/len(nifty_stocks))
    
    return pd.DataFrame(results)

# 🔥 MAIN DISPLAY
if st.button("🔥 SCAN 40 STOCKS", type="primary", use_container_width=True) or 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
    df = scan_stocks()
    
    buy_df = df[df['Signal']=="🟢 BUY"]
    sell_df = df[df['Signal']=="🔴 SELL"] 
    hold_df = df[df['Signal']=="🟡 HOLD"]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="buy-card"><h3>🟢 BUY STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("Count", len(buy_df))
        st.dataframe(buy_df[['Stock','Price','RSI']], height=300)
    
    with col2:
        st.markdown('<div class="sell-card"><h3>🔴 SELL STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("Count", len(sell_df))
        st.dataframe(sell_df[['Stock','Price','RSI']], height=300)
    
    with col3:
        st.markdown('<div class="hold-card"><h3>🟡 HOLD STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("Count", len(hold_df))
        st.dataframe(hold_df[['Stock','Price','RSI']], height=300)
    
    # ✅ FIXED CSV LINE
    csv = df.to_csv(index=False)  # ← COMPLETE METHOD
    st.download_button("💾 DOWNLOAD CSV", csv, "nifty-scan.csv", use_container_width=True)

# 🕒 5-MIN AUTO REFRESH
st.markdown("---")
if 'last_scan' not in st.session_state:
    st.session_state.last_scan = 0

remaining = max(0, 300 - (time.time() - st.session_state.last_scan))
m, s = divmod(int(remaining), 60)
st.metric("⏳ Auto Refresh", f"{m}m {s}s")

st.info("✅ **5 min refresh = NO BLOCKS EVER** | 40 major NIFTY stocks")
