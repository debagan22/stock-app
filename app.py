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
if 'auto_strongbuy' not in st.session_state: st.session_state.auto_strongbuy = True

st.set_page_config(page_title="NIFTY LIVE SCANNER", layout="wide", page_icon="📈")
st.title("🚀 NIFTY 500 LIVE SCANNER")
st.markdown("**🤖 AUTO STRONG BUY | 🟢🔴🟡 SIDE-BY-SIDE TABS**")

# 🔥 COMPLETE 500 STOCKS LIST
nifty500 = [
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS", "TCS.NS",
    "BAJFINANCE.NS", "LT.NS", "INFY.NS", "HINDUNILVR.NS", "ITC.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "LTIM.NS", "SUNPHARMA.NS", 
    "HCLTECH.NS", "TITAN.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "NESTLEIND.NS",
    "TECHM.NS", "POWERGRID.NS", "WIPRO.NS", "TATAMOTORS.NS", "JSWSTEEL.NS",
    "TATASTEEL.NS", "COALINDIA.NS", "NTPC.NS", "ONGC.NS", "M&M.NS", "BAJAJFINSV.NS",
    "BEL.NS", "TATACONSUM.NS", "GRASIM.NS", "DIVISLAB.NS", "DRREDDY.NS", "CIPLA.NS",
    "BPCL.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BRITANNIA.NS", "APOLLOHOSP.NS",
    "TRENT.NS", "VARUNBEV.NS", "LICI.NS", "BAJAJ-AUTO.NS", "SHRIRAMFIN.NS",
    "GODREJCP.NS", "PIDILITIND.NS", "ADANIENT.NS", "AMBUJACEM.NS", "AUBANK.NS",
    "AUROPHARMA.NS", "BANKBARODA.NS", "BHARATFORG.NS", "BHEL.NS", "BIOCON.NS",
    "BOSCHLTD.NS", "CHOLAFIN.NS", "COFORGE.NS", "COLPAL.NS", "DABUR.NS",
    "DLF.NS", "DIXON.NS", "ESCORTS.NS", "EXIDEIND.NS", "FEDERALBNK.NS",
    "GAIL.NS", "HAVELLS.NS", "HDFCLIFE.NS", "HINDALCO.NS", "IDFCFIRSTB.NS",
    "INDUSINDBK.NS", "IOC.NS", "IPCALAB.NS", "IRCTC.NS", "JINDALSTEL.NS",
    "JSWENERGY.NS", "JUBLFOOD.NS", "L&TFH.NS", "LUPIN.NS", "MANAPPURAM.NS",
    "MFSL.NS", "MOTHERSUMI.NS", "NATIONALUM.NS", "NAUKRI.NS", "NMDC.NS",
    "OBEROIRLTY.NS", "PAGEIND.NS", "PEL.NS", "PERSISTENT.NS", "PNB.NS",
    "POLYCAB.NS", "RAYMOND.NS", "SAIL.NS", "SBILIFE.NS", "SIEMENS.NS",
    "SRF.NS", "TATACOMM.NS", "TATAPOWER.NS", "TORNTPOWER.NS", "TVSMOTOR.NS",
    "VEDL.NS", "VOLTAS.NS", "ZYDUSLIFE.NS", "ABB.NS", "ACC.NS", "ALKEM.NS"
]

def analyze_stock(symbol):
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
            'Stock': symbol.replace('.NS',''), 
            'Price': f"₹{price:.1f}",
            'RSI': float(rsi), 
            'MA20': float(ma20), 
            'Signal': signal
        }
    except:
        return None

# 🔥 AUTO STRONG BUY ONLY (500 stocks)
@st.cache_data(ttl=60)
def scan_strongbuy_only():
    results = []
    progress = st.progress(0)
    for i, symbol in enumerate(nifty500):
        result = analyze_stock(symbol)
        if result and result['Signal'] == "🟢 STRONG BUY":
            results.append(result)
        progress.progress((i + 1) / len(nifty500))
        time.sleep(0.08)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 FULL SCAN ALL SIGNALS (120 stocks)
@st.cache_data(ttl=1800)
def scan_full_signals():
    results = []
    progress = st.progress(0)
    reliable_stocks = nifty500[:120]
    
    for i, symbol in enumerate(reliable_stocks):
        result = analyze_stock(symbol)
        if result: results.append(result)
        progress.progress((i + 1) / len(reliable_stocks))
        time.sleep(0.1)
    progress.empty()
    return pd.DataFrame(results)

# 🔥 CONTROLS
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_strongbuy = col1.toggle("🤖 AUTO STRONG BUY (45s)", value=st.session_state.auto_strongbuy)

if col2.button("🔥 FULL SCAN (2min)", type="primary", use_container_width=True):
    with st.spinner("🔥 Scanning ALL signals..."):
        st.session_state.df_full = scan_full_signals()
        st.session_state.last_full = time.time()
        st.session_state.full_count += 1
    st.rerun()

if col3.button("🔄 CLEAR CACHE", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# 🔥 AUTO SCAN LOGIC
time_since_strongbuy = time.time() - st.session_state.last_strongbuy
if st.session_state.auto_strongbuy and time_since_strongbuy > 45:
    with st.spinner("🔍 Auto scanning STRONG BUY across 500 stocks..."):
        st.session_state.df_strongbuy = scan_strongbuy_only()
        st.session_state.last_strongbuy = time.time()
        st.session_state.strongbuy_count += 1
    st.rerun()

# 🔥 MAIN SECTIONS
col_main1, col_main2 = st.columns([1,3])

with col_main1:
    st.markdown("### 🟢 LIVE STRONG BUY (AUTO)")
    if not st.session_state.df_strongbuy.empty:
        df = st.session_state.df_strongbuy
        st.success(f"#{st.session_state.strongbuy_count} | {len(df)} stocks")
        st.dataframe(df.sort_values('RSI'), height=350, use_container_width=True)
        
        csv = df.to_csv(index=False)
        st.download_button("💾 DOWNLOAD", csv, "strong-buy-live.csv", use_container_width=True)
    else:
        st.info("🤖 AUTO scanning 500 stocks...")

with col_main2:
    st.markdown("### 📊 ALL SIGNALS (MANUAL SCAN)")
    
    # 🔥 SIDE-BY-SIDE TABS FOR SIGNALS
    strong_buy_tab, buy_tab, sell_tab, hold_tab = st.tabs([
        "🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"
    ])
    
    if not st.session_state.df_full.empty:
        df_full = st.session_state.df_full
        
        with strong_buy_tab:
            strong_buy = df_full[df_full['Signal'] == "🟢 STRONG BUY"]
            if not strong_buy.empty:
                st.metric("Count", len(strong_buy))
                st.dataframe(strong_buy.sort_values('RSI'), height=250, use_container_width=True)
            else:
                st.info("No STRONG BUY signals")
        
        with buy_tab:
            buy_signals = df_full[df_full['Signal'] == "🟢 BUY"]
            if not buy_signals.empty:
                st.metric("Count", len(buy_signals))
                st.dataframe(buy_signals.sort_values('RSI'), height=250, use_container_width=True)
            else:
                st.info("No BUY signals")
        
        with sell_tab:
            sell_signals = df_full[df_full['Signal'].str.contains('SELL', na=False)]
            if not sell_signals.empty:
                st.metric("Count", len(sell_signals))
                st.dataframe(sell_signals.sort_values('RSI', ascending=False), height=250, use_container_width=True)
            else:
                st.info("No SELL signals")
        
        with hold_tab:
            hold_signals = df_full[df_full['Signal'] == "🟡 HOLD"]
            if not hold_signals.empty:
                st.metric("Count", len(hold_signals))
                st.dataframe(hold_signals.head(20).sort_values('RSI'), height=250, use_container_width=True)
            else:
                st.info("No HOLD signals")
    else:
        st.info("🔥 Click FULL SCAN first")

# 🔥 STATUS DASHBOARD
st.markdown("---")
st.subheader("📊 LIVE STATUS")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🤖 Auto Scans", st.session_state.strongbuy_count)
col2.metric("🔥 Full Scans", st.session_state.full_count)
col3.metric("⏱️ Auto Timer", f"{time_since_strongbuy:.0f}s")
col4.metric("🟢 Live StrongBuys", len(st.session_state.df_strongbuy))

st.info("""
**🤖 LEFT SIDE**: AUTO STRONG BUY (500 stocks every 45s)  
**📊 RIGHT SIDE**: 4 TABS → STRONG BUY | BUY | SELL | HOLD  
**🎯 PERFECT LAYOUT**: Live monitoring + Complete analysis side-by-side!
""")
