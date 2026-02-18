import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np
from datetime import datetime, time as dt_time
import pytz

st.set_page_config(layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# ✅ FIXED: Define NIFTY100_COMPLETE FIRST
NIFTY100_COMPLETE = [
    'RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 
    'HINDUNILVR', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 
    'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 
    'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'HCLTECH', 'SBIN', 
    'BAJFINANCE', 'TATASTEEL', 'GRASIM', 'HDFCLIFE', 'CIPLA', 'DIVISLAB', 
    'DRREDDY', 'EICHERMOT', 'COALINDIA', 'BRITANNIA', 'HINDALCO', 'BPCL',
    'BAJAJFINSV', 'APOLLOHOSP', 'HEROMOTOCO', 'SHRIRAMFIN', 'ADANIENT', 
    'TATACONSUM', 'GODREJCP', 'ADANIPORTS', 'TRENT', 'BAJAJ-AUTO', 'IOC',
    'INDUSINDBK', 'LICI', 'SBILIFE', 'PIDILITIND', 'SRTRANSFIN', 'VARUNBEV',
    'DIXON', 'HAL', 'LTFOODS', 'BEL', 'BAJAJHLDNG', 'JINDALSTEL', 'CHOLAFIN',
    'TORNTPOWER', 'HAVELLS', 'AMBUJACEM', 'MPHASIS', 'POLYCAB', 'SOLARINDS',
    'BORORENEW', 'TVSMOTOR', 'ZFCVINDIA', 'ABB', 'DABUR', 'KALPATPOWR',
    'BANKBARODA', 'GAIL', 'SHREECEM', 'SIEMENS', 'LTTS', 'ICICIPRULI',
    'JSWENERGY', 'TORNTPHARM', 'UNIONBANK', 'VEDANTA', 'NMDC', 'SAIL', 
    'PFC', 'RECLTD'
]

NIFTY_50 = ['RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'ICICIBANK', 'BHARTIARTL', 'ITC', 'KOTAKBANK', 
           'HINDUNILVR', 'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 
           'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL', 
           'ONGC', 'M&M', 'NTPC', 'TECHM', 'WIPRO', 'LTIM', 'HCLTECH', 'SBIN', 
           'BAJFINANCE', 'TATASTEEL', 'GRASIM', 'HDFCLIFE', 'CIPLA', 'DIVISLAB', 
           'DRREDDY', 'EICHERMOT', 'COALINDIA', 'BRITANNIA', 'HINDALCO', 'BPCL']

# IST Timezone
IST = pytz.timezone('Asia/Kolkata')

def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5:  # Sat/Sun
        return False
    market_open = dt_time(9, 15)
    market_close = dt_time(15, 30)
    return market_open <= now.time() <= market_close

# 🎨 STYLING
st.markdown("""
<style>
.main-header {font-size:4rem !important;font-weight:900 !important;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;}
.metric-card {background:linear-gradient(145deg,#1e3a8a,#3b82f6);padding:1.5rem;border-radius:15px;box-shadow:0 10px 30px rgba(59,130,246,0.3);border:2px solid rgba(255,255,255,0.1);}
.super-buy {background:linear-gradient(145deg,#10b981,#059669) !important;}
.strong-buy {background:linear-gradient(145deg,#3b82f6,#1d4ed8) !important;}
.buy {background:linear-gradient(145deg,#06b6d4,#0891b2) !important;}
.sell {background:linear-gradient(145deg,#ef4444,#dc2626) !important;}
.hold {background:linear-gradient(145deg,#eab308,#ca8a04) !important;}
.metric-live {box-shadow:0 0 20px #10b981 !important;animation:pulse 2s infinite;}
@keyframes pulse {0%{box-shadow:0 0 20px #10b981;}50%{box-shadow:0 0 40px #10b981;}}
.market-open {background:linear-gradient(145deg,#10b981,#059669) !important;}
.market-closed {background:linear-gradient(145deg,#6b7280,#4b5563) !important;}
</style>
""", unsafe_allow_html=True)

# 🔥 HEADER
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown('<h1 class="main-header">🚀 NIFTY 100 LIVE SCANNER</h1>', unsafe_allow_html=True)
    status = "🔴 **LIVE MARKET**" if is_market_open() else "📊 **MARKET CLOSED**"
    status_class = "market-open" if is_market_open() else "market-closed"
    st.markdown(f'<h2 style="text-align:center;font-weight:800;" class="{status_class}">{status}</h2>', unsafe_allow_html=True)

if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False

@st.cache_data(ttl=60)  # 1-MIN REFRESH
def get_nifty_live_data(symbol):
    try:
        ticker = yf.Ticker(symbol + '.NS')
        if is_market_open():
            hist = ticker.history(period="1d", interval="1m")
            if not hist.empty:
                live_price = hist['Close'].iloc[-1]
            else:
                hist = ticker.history(period="3mo")
                live_price = hist['Close'].iloc[-1]
        else:
            hist = ticker.history(period="3mo")
            live_price = hist['Close'].iloc[-1]
        
        if len(hist) >= 30:
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            macd = ta.trend.MACD(hist['Close'])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            histogram = macd.macd_diff().iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            change = ((live_price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            
            category = '🟦 NIFTY 50' if symbol in NIFTY_50 else '🟨 NIFTY NEXT 50'
            status = '🔴 LIVE' if is_market_open() else '📊 EOD'
            
            # Signal logic
            rsi_buy = rsi < 45; rsi_super = rsi < 35; rsi_sell = rsi > 65
            macd_bull = macd_line > signal_line; ma_bull = live_price > ma20
            confirmations = sum([rsi_super, macd_bull, ma_bull])
            
            if confirmations == 3: signal = '🚀 SUPER BUY'
            elif confirmations >= 2: signal = '🟢 STRONG BUY'
            elif rsi_buy or macd_bull: signal = '🟢 BUY'
            elif rsi_sell or not macd_bull: signal = '🔴 SELL'
            else: signal = '🟡 HOLD'
            
            return {
                'Stock': symbol, 'Price': f"₹{live_price:.0f}", 'Change': f"{change:.1f}%",
                'RSI': f"{rsi:.1f}", 'MACD': f"{macd_line:.2f}", 'Signal_Line': f"{signal_line:.2f}",
                'Histogram': f"{histogram:.2f}", 'MA20': f"₹{ma20:.0f}",
                'Price/MA20': '📈' if ma_bull else '📉', 'Signal': signal,
                'Category': category, 'Status': status, 'RSI_Value': rsi
            }
    except:
        return None

def display_metrics(all_data):
    super_buy = len([d for d in all_data if d['Signal']=='🚀 SUPER BUY'])
    strong_buy = len([d for d in all_data if d['Signal']=='🟢 STRONG BUY'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: st.metric("🚀 SUPER BUY", super_buy, "super-buy")
    with col2: st.metric("🟢 STRONG", strong_buy, "strong-buy")
    with col3: st.metric("🟢 BUY", len([d for d in all_data if d['Signal']=='🟢 BUY']), "buy")
    with col4: st.metric("🔴 SELL", len([d for d in all_data if d['Signal']=='🔴 SELL']), "sell")
    with col5: st.metric("🟡 HOLD", len(all_data) - super_buy - strong_buy, "hold")

# 🔥 MAIN CONTROLS
col_btn1, col_btn2 = st.columns([3,1])
with col_btn1:
    if st.button("🔥 **LAUNCH LIVE SCAN (50 Stocks)** 🔥", type="primary", use_container_width=True):
        st.session_state.scan_complete = True
        st.cache_data.clear()
        st.rerun()
with col_btn2:
    if st.button("🔄 REFRESH", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 📊 RESULTS
if st.session_state.scan_complete:
    st.markdown("---")
    progress = st.progress(0)
    all_data = []
    successful_scans = 0
    
    for i, symbol in enumerate(NIFTY100_COMPLETE[:50]):  # Top 50 for speed
        data = get_nifty_live_data(symbol)
        if data:
            all_data.append(data)
            successful_scans += 1
        progress.progress((i + 1) / 50)
        time.sleep(0.1)
    
    progress.empty()
    
    st.success(f"✅ **{successful_scans}/50 SCANNED** | {datetime.now(IST).strftime('%H:%M:%S IST')}")
    display_metrics(all_data)
    
    # RESULTS TABLE
    if all_data:
        df = pd.DataFrame(all_data).sort_values('RSI_Value')
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("💾 DOWNLOAD CSV", df.to_csv(index=False), "nifty100-live.csv")

st.markdown("---")
st.info(f"**🔴 LIVE** (9:15-3:30 IST) | **📊 EOD** after hours | 60s auto-refresh")
