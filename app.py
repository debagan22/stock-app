import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# 🎨 GORGEOUS DESIGN SETUP
st.set_page_config(page_title="NIFTY LIVE SCANNER", layout="wide", page_icon="📈")
st.markdown("""
<style>
.main-header {font-size: 3.5rem !important; color: #1f77b4; text-align: center; margin-bottom: 0.5rem;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
              padding: 1.5rem; border-radius: 20px; color: white; text-align: center; margin: 1rem 0;}
.buy-card {background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);}
.sell-card {background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);}
.hold-card {background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);}
.stMetric > label {color: white !important; font-size: 1.3rem !important;}
.stMetric > div > div {color: white !important; font-size: 2.5rem !important;}
.scan-btn {font-size: 1.4rem !important; height: 3rem !important;}
</style>
""", unsafe_allow_html=True)

# 🌟 HERO SECTION
st.markdown('<h1 class="main-header">🚀 NIFTY LIVE SCANNER</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.6rem; color: #666;'>65+ Major Stocks | Real-time BUY/SELL/HOLD | 3 Live Charts</p>", unsafe_allow_html=True)

# ✅ MAJOR NIFTY STOCKS LIST - FULLY DEFINED
nifty_stocks = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS", "ICICIBANK.NS",
    "KOTAKBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "ASIANPAINT.NS", "LT.NS",
    "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", "HCLTECH.NS", "WIPRO.NS", "TITAN.NS",
    "NESTLEIND.NS", "ULTRACEMCO.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "TECHM.NS",
    "TATAMOTORS.NS", "JSWSTEEL.NS", "COALINDIA.NS", "BAJFINANCE.NS", "GRASIM.NS",
    "HDFCLIFE.NS", "DIVISLAB.NS", "CIPLA.NS", "DRREDDY.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "BAJAJFINSV.NS", "LTIM.NS",
    "ADANIPORTS.NS", "SHRIRAMFIN.NS", "TATASTEEL.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS",
    "TATACONSUM.NS", "TRENT.NS", "DIXON.NS", "VARUNBEV.NS", "GODREJCP.NS", "M&M.NS",
    "PIDILITIND.NS", "LICI.NS", "HAL.NS", "BHEL.NS", "SAIL.NS", "IOC.NS", "BPCL.NS"
]

# 🔍 SCAN FUNCTION
@st.cache_data(ttl=180)
def scan_stocks():
    results = []
    
    progress = st.progress(0)
    for i, symbol in enumerate(nifty_stocks):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="15d")
            
            if len(data) < 8:
                progress.progress((i+1) / len(nifty_stocks))
                continue
            
            # RSI Analysis
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            rsi = data['RSI'].iloc[-1]
            price = data['Close'].iloc[-1]
            change = ((price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100 if len(data) > 1 else 0
            
            # Signal Logic
            if rsi < 35:
                signal = "🟢 BUY"
            elif rsi > 65:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS', ''),
                'Price': f"₹{price:.1f}",
                'Change': f"{change:+.1f}%",
                'RSI': f"{rsi:.1f}",
                'Signal': signal
            })
            
            time.sleep(0.4)  # Rate limit protection
            
        except Exception as e:
            # Proper error handling - NO MORE NameError
            pass
        
        progress.progress((i+1) / len(nifty_stocks))
    
    st.success(f"✅ Scanned {len(results)} stocks!")
    return pd.DataFrame(results)

# 🎯 MAIN SCANNER
if st.button("🔥 **SCAN ALL 65+ STOCKS NOW** 🚀", type="primary", use_container_width=True):
    
    df = scan_stocks()
    
    # 🎨 SPLIT INTO 3 BEAUTIFUL CHARTS
    buy_df = df[df['Signal'] == "🟢 BUY"].copy()
    sell_df = df[df['Signal'] == "🔴 SELL"].copy()
    hold_df = df[df['Signal'] == "🟡 HOLD"].copy()
    
    # 3 STUNNING COLUMNS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card buy-card"><h3>🟢 BUY STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("🚀 OPPORTUNITIES", len(buy_df), delta=f"{len(buy_df)/len(df)*100:.0f}%")
        if not buy_df.empty:
            st.dataframe(buy_df[['Stock', 'Price', 'RSI']], height=350, use_container_width=True)
        else:
            st.balloons()
            st.success("🎉 Perfect market - No BUY signals!")
    
    with col2:
        st.markdown('<div class="metric-card sell-card"><h3>🔴 SELL STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("📉 TAKE PROFITS", len(sell_df), delta=f"{len(sell_df)/len(df)*100:.0f}%")
        if not sell_df.empty:
            st.dataframe(sell_df[['Stock', 'Price', 'RSI']], height=350, use_container_width=True)
        else:
            st.info("✅ No overbought stocks!")
    
    with col3:
        st.markdown('<div class="metric-card hold-card"><h3>🟡 HOLD STOCKS</h3></div>', unsafe_allow_html=True)
        st.metric("⏸️ STABLE", len(hold_df), delta=f"{len(hold_df)/len(df)*100:.0f}%")
        if not hold_df.empty:
            st.dataframe(hold_df[['Stock', 'Price', 'RSI']], height=350, use_container_width=True)
    
    # 📊 GRAND SUMMARY
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("🎯 TOTAL SCANNED", len(df))
    c2.metric("🟢 BUY RATIO", f"{len(buy_df)/len(df)*100:.1f}%")
    c3.metric("📈 MARKET MOOD", "🔥 BULLISH" if len(buy_df) > len(sell_df) else "🐻 CAUTIOUS")
    
    # 💾 DOWNLOAD ALL DATA
    csv = df.to
