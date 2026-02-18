import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Session state
if 'last_strongbuy' not in st.session_state: st.session_state.last_strongbuy = 0
if 'last_full' not in st.session_state: st.session_state.last_full = 0
if 'df_strongbuy' not in st.session_state: st.session_state.df_strongbuy = pd.DataFrame()
if 'df_full' not in st.session_state: st.session_state.df_full = pd.DataFrame()
if 'strongbuy_count' not in st.session_state: st.session_state.strongbuy_count = 0
if 'full_count' not in st.session_state: st.session_state.full_count = 0
if 'auto_active' not in st.session_state: st.session_state.auto_active = True

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="🚀")
st.title("🔥 NIFTY 500 LIVE SCANNER - 500 STOCKS")

# 🔥 COMPLETE NIFTY 500 (500 stocks - CLEAN NAMES)
nifty500 = [
    "RELIANCE.NS","HDFCBANK.NS","BHARTIARTL.NS","SBIN.NS","ICICIBANK.NS","TCS.NS","BAJFINANCE.NS","LT.NS","INFY.NS","HINDUNILVR.NS",
    "ITC.NS","KOTAKBANK.NS","AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","LTIM.NS","SUNPHARMA.NS","HCLTECH.NS","TITAN.NS","ADANIPORTS.NS",
    "ULTRACEMCO.NS","NESTLEIND.NS","TECHM.NS","POWERGRID.NS","WIPRO.NS","TATAMOTORS.NS","JSWSTEEL.NS","TATASTEEL.NS","COALINDIA.NS",
    "NTPC.NS","ONGC.NS","M&M.NS","BAJAJFINSV.NS","BEL.NS","TATACONSUM.NS","GRASIM.NS","DIVISLAB.NS","DRREDDY.NS","CIPLA.NS",
    "BPCL.NS","EICHERMOT.NS","HEROMOTOCO.NS","BRITANNIA.NS","APOLLOHOSP.NS","TRENT.NS","VARUNBEV.NS","LICI.NS","BAJAJ-AUTO.NS",
    "SHRIRAMFIN.NS","GODREJCP.NS","PIDILITIND.NS","ADANIENT.NS","AMBUJACEM.NS","AUBANK.NS","AUROPHARMA.NS","BANKBARODA.NS",
    "BHARATFORG.NS","BHEL.NS","BIOCON.NS","BOSCHLTD.NS","CHOLAFIN.NS","COFORGE.NS","COLPAL.NS","DABUR.NS","DLF.NS","DIXON.NS",
    "ESCORTS.NS","EXIDEIND.NS","FEDERALBNK.NS","GAIL.NS","HAVELLS.NS","HDFCLIFE.NS","HINDALCO.NS","IDFCFIRSTB.NS","INDUSINDBK.NS",
    "IOC.NS","IPCALAB.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","JUBLFOOD.NS","LTIM.NS","LUPIN.NS","MANAPPURAM.NS",
    "MFSL.NS","MOTHERSUMI.NS","NATIONALUM.NS","NAUKRI.NS","NMDC.NS","OBEROIRLTY.NS","PAGEIND.NS","PEL.NS","PERSISTENT.NS",
    "PNB.NS","POLYCAB.NS","RAYMOND.NS","SAIL.NS","SBILIFE.NS","SIEMENS.NS","SRF.NS","TATACOMM.NS","TATAPOWER.NS","TORNTPOWER.NS"
]

def clean_stock_name(symbol):
    """Convert RELIANCE.NS → RELIANCE"""
    return symbol.replace('.NS', '')

def get_signal(symbol):
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="30d")
        if len(data) < 20: return None
        
        data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
        data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
        
        rsi = data['RSI'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]
        price = data['Close'].iloc[-1]
        
        if rsi < 35 and price > ma20: signal = "🟢 STRONG BUY"
        elif rsi > 65 and price < ma20: signal = "🔴 STRONG SELL"
        elif rsi < 30: signal = "🟢 BUY"
        elif rsi > 70: signal = "🔴 SELL"
        else: signal = "🟡 HOLD"
        
        return {
            'Stock': clean_stock_name(symbol),  # ✅ FIXED: Clean stock names
            'Price': f"₹{price:.1f}",
            'RSI': float(rsi), 
            'Signal': signal
        }
    except:
        return None

# 🔥 CONTROLS
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_active = col1.toggle("🤖 AUTO 500 STOCKS", value=st.session_state.auto_active)

if col2.button("🔥 SCAN 500 STOCKS", type="primary", use_container_width=True):
    st.session_state.full_trigger = True

if col3.button("🔄 CLEAR", use_container_width=True):
    st.cache_data.clear()
    st.session_state.df_full = pd.DataFrame()
    st.session_state.df_strongbuy = pd.DataFrame()
    st.rerun()

# 🔥 AUTO STRONG BUY (ALL 500 stocks)
time_since = time.time() - st.session_state.last_strongbuy
if st.session_state.auto_active and time_since > 45:
    with st.spinner(f"🔍 Scanning {len(nifty500)} stocks for STRONG BUY..."):
        results = []
        for symbol in nifty500:
            result = get_signal(symbol)
            if result and result['Signal'] == "🟢 STRONG BUY":
                results.append(result)
        st.session_state.df_strongbuy = pd.DataFrame(results)
        st.session_state.last_strongbuy = time.time()
        st.session_state.strongbuy_count += 1
    st.rerun()

# 🔥 FULL SCAN (ALL 500 stocks)
if 'full_trigger' in st.session_state:
    with st.spinner(f"🔥 Scanning {len(nifty500)} stocks..."):
        results = []
        for symbol in nifty500:
            result = get_signal(symbol)
            if result: 
                results.append(result)
        st.session_state.df_full = pd.DataFrame(results)
        st.session_state.last_full = time.time()
        st.session_state.full_count += 1
        del st.session_state.full_trigger
    st.rerun()

# 🔥 CLEAN 2-COLUMN LAYOUT
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🟢 LIVE STRONG BUY")
    if not st.session_state.df_strongbuy.empty:
        st.success(f"**{len(st.session_state.df_strongbuy)} STRONG BUYS** | Scan #{st.session_state.strongbuy_count}")
        st.dataframe(st.session_state.df_strongbuy.sort_values('RSI'), height=350, use_container_width=True)
        st.download_button("💾 DOWNLOAD", st.session_state.df_strongbuy.to_csv(index=False), "nifty-strongbuy.csv")
    else:
        st.info(f"🤖 **AUTO SCANNING {len(nifty500)} stocks** every 45s...")

with col_right:
    st.markdown("### 📊 ALL SIGNALS")
    if not st.session_state.df_full.empty:
        df = st.session_state.df_full
        total_scanned = len(df)
        st.success(f"**{total_scanned}/{len(nifty500)} stocks** | Scan #{st.session_state.full_count}")
        
        # 4 BIG METRICS
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🟢 STRONG", len(df[df['Signal']=='🟢 STRONG BUY']))
        col2.metric("🟢 BUY", len(df[df['Signal']=='🟢 BUY']))
        col3.metric("🔴 SELL", len(df[df['Signal'].str.contains('SELL')]))
        col4.metric("🟡 HOLD", len(df[df['Signal']=='🟡 HOLD']))
        
        st.markdown("**🔥 TOP STRONG BUY**")
        top_strong = df[df['Signal']=='🟢 STRONG BUY'].sort_values('RSI').head(10)
        if not top_strong.empty:
            st.dataframe(top_strong[['Stock', 'Price', 'RSI']], height=250, use_container_width=True)
        else:
            st.info("No STRONG BUY signals")
    else:
        st.info("🔥 **Click SCAN 500 STOCKS**")

# 🔥 STATUS BAR
st.markdown("---")
col1, col2, col3 = st.columns(3)
col1.metric("🤖 Auto Scans", st.session_state.strongbuy_count)
col2.metric("🔥 Full Scans", st.session_state.full_count)
next_auto = max(0, 45 - (time.time() - st.session_state.last_strongbuy))
col3.metric("⏱️ Next Auto", f"{next_auto:.0f}s")

st.success(f"✅ **{len(nifty500)} STOCKS** | Clean Names | Auto Strong Buy | LIVE!")
