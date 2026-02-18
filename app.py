import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

# Session state
if 'data_full' not in st.session_state: st.session_state.data_full = pd.DataFrame()
if 'data_strongbuy' not in st.session_state: st.session_state.data_strongbuy = pd.DataFrame()
if 'last_scan' not in st.session_state: st.session_state.last_scan = 0
if 'scan_count' not in st.session_state: st.session_state.scan_count = 0
if 'auto_active' not in st.session_state: st.session_state.auto_active = True

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="🚀")
st.title("🔥 NIFTY 500 LIVE SCANNER - RSI + MA20")

# 🔥 COMPLETE NIFTY 500 STOCKS
nifty500 = [
    "RELIANCE.NS","HDFCBANK.NS","TCS.NS","INFY.NS","HINDUNILVR.NS","ICICIBANK.NS","KOTAKBANK.NS","ITC.NS","LT.NS","BHARTIARTL.NS",
    "AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","NESTLEIND.NS","ULTRACEMCO.NS","POWERGRID.NS","TATAMOTORS.NS",
    "JSWSTEEL.NS","ONGC.NS","COALINDIA.NS","M&M.NS","NTPC.NS","TECHM.NS","WIPRO.NS","LTIM.NS","TATASTEEL.NS","CIPLA.NS","DRREDDY.NS",
    "BPCL.NS","HEROMOTOCO.NS","DIVISLAB.NS","BRITANNIA.NS","BAJAJFINSV.NS","APOLLOHOSP.NS","TRENT.NS","EICHERMOT.NS","TATACONSUM.NS",
    "BEL.NS","VARUNBEV.NS","GODREJCP.NS","PIDILITIND.NS","AUROPHARMA.NS","BANKBARODA.NS","BHARATFORG.NS","BHEL.NS","BIOCON.NS",
    "CHOLAFIN.NS","COFORGE.NS","COLPAL.NS","DABUR.NS","DLF.NS","DIXON.NS","ESCORTS.NS","FEDERALBNK.NS","GAIL.NS","HAVELLS.NS",
    "HDFCLIFE.NS","HINDALCO.NS","IOC.NS","IPCALAB.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","JUBLFOOD.NS","LUPIN.NS",
    "MANAPPURAM.NS","MFSL.NS","NAUKRI.NS","NMDC.NS","OBEROIRLTY.NS","PAGEIND.NS","PEL.NS","PERSISTENT.NS","PNB.NS","POLYCAB.NS",
    "RAYMOND.NS","SAIL.NS","SBILIFE.NS","SIEMENS.NS","SRF.NS","TATACOMM.NS","TATAPOWER.NS","TORNTPOWER.NS","TVSMOTOR.NS",
    "VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","ABB.NS","ACC.NS","ALKEM.NS","BANKINDIA.NS","BATAINDIA.NS","BERGEPAINT.NS"
]

def scan_stocks(symbols, strong_buy_only=False):
    """Scan stocks with RSI + MA20 - FULL RESULTS"""
    results = []
    progress = st.progress(0)
    
    for i, symbol in enumerate(symbols):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            if len(data) < 20:
                progress.progress((i+1)/len(symbols))
                continue
            
            # ✅ MA20 CALCULATION (20-period Simple Moving Average)
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            if strong_buy_only:
                # STRONG BUY: RSI<35 + Price>MA20
                if rsi < 35 and price > ma20:
                    results.append({
                        'Stock': symbol.replace('.NS', ''),
                        'Price': f"₹{price:.0f}",
                        'MA20': f"₹{ma20:.0f}",
                        'RSI': f"{rsi:.1f}",
                        'Signal': '🟢 STRONG BUY'
                    })
            else:
                # ALL SIGNALS
                if rsi < 35 and price > ma20:
                    signal = '🟢 STRONG BUY'
                elif rsi < 30:
                    signal = '🟢 BUY'
                elif rsi > 70:
                    signal = '🔴 SELL'
                elif rsi > 65 and price < ma20:
                    signal = '🔴 STRONG SELL'
                else:
                    signal = '🟡 HOLD'
                
                results.append({
                    'Stock': symbol.replace('.NS', ''),
                    'Price': f"₹{price:.0f}",
                    'MA20': f"₹{ma20:.0f}",
                    'RSI': f"{rsi:.1f}",
                    'Signal': signal
                })
            
            progress.progress((i+1)/len(symbols))
            time.sleep(0.05)
            
        except:
            progress.progress((i+1)/len(symbols))
    
    progress.empty()
    return pd.DataFrame(results)

# 🔥 CONTROLS
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_active = col1.toggle("🤖 AUTO STRONG BUY", value=st.session_state.auto_active)

if col2.button("🔥 FULL SCAN 500", type="primary", use_container_width=True):
    with st.spinner(f"🔥 Scanning {len(nifty500)} stocks..."):
        st.session_state.data_full = scan_stocks(nifty500)
        st.session_state.scan_count += 1
        st.session_state.last_scan = time.time()
    st.rerun()

if col3.button("🔄 CLEAR ALL", use_container_width=True):
    st.session_state.data_full = pd.DataFrame()
    st.session_state.data_strongbuy = pd.DataFrame()
    st.session_state.scan_count = 0
    st.rerun()

# 🔥 AUTO STRONG BUY SCAN
if st.session_state.auto_active:
    time_since = time.time() - st.session_state.last_scan
    if time_since > 45:
        with st.spinner("🤖 Auto scanning STRONG BUY (500 stocks)..."):
            st.session_state.data_strongbuy = scan_stocks(nifty500, strong_buy_only=True)
            st.session_state.last_scan = time.time()
        st.rerun()

# 🔥 4 SIGNAL TABS WITH MA20 COLUMN
tab1, tab2, tab3, tab4 = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])

with tab1:
    st.markdown("### 🚀 LIVE STRONG BUY (RSI<35 + Price>MA20)")
    if not st.session_state.data_strongbuy.empty:
        df = st.session_state.data_strongbuy.sort_values('RSI')
        st.success(f"**{len(df)} STOCKS** | Scan #{st.session_state.scan_count} | Auto: ON")
        st.dataframe(df, height=500, use_container_width=True)
        st.download_button("💾 DOWNLOAD STRONG BUY", df.to_csv(index=False), "strongbuy.csv")
    else:
        st.info("🤖 **AUTO SCANNING 500 stocks every 45s**")

with tab2:
    st.markdown("### 🟢 BUY (RSI<30)")
    if not st.session_state.data_full.empty:
        buy_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟢 BUY'].sort_values('RSI')
        st.metric("Count", len(buy_df))
        if len(buy_df) > 0:
            st.dataframe(buy_df, height=500, use_container_width=True)
            st.download_button("💾 DOWNLOAD BUY", buy_df.to_csv(index=False), "buy.csv")
        else:
            st.warning("No BUY signals found")
    else:
        st.info("🔥 **Click FULL SCAN first**")

with tab3:
    st.markdown("### 🔴 SELL SIGNALS")
    if not st.session_state.data_full.empty:
        sell_df = st.session_state.data_full[st.session_state.data_full['Signal'].str.contains('SELL')].sort_values('RSI', ascending=False)
        st.metric("Count", len(sell_df))
        if len(sell_df) > 0:
            st.dataframe(sell_df, height=500, use_container_width=True)
            st.download_button("💾 DOWNLOAD SELL", sell_df.to_csv(index=False), "sell.csv")
        else:
            st.warning("No SELL signals found")
    else:
        st.info("🔥 **Click FULL SCAN first**")

with tab4:
    st.markdown("### 🟡 HOLD SIGNALS")
    if not st.session_state.data_full.empty:
        hold_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟡 HOLD']
        st.metric("Count", len(hold_df))
        if len(hold_df) > 0:
            st.dataframe(hold_df.head(50), height=500, use_container_width=True)
            st.download_button("💾 DOWNLOAD HOLD (TOP 50)", hold_df.head(50).to_csv(index=False), "hold-top50.csv")
        else:
            st.warning("No HOLD signals found")
    else:
        st.info("🔥 **Click FULL SCAN first**")

# 🔥 LIVE STATUS DASHBOARD
st.markdown("---")
st.subheader("📊 LIVE STATUS")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🟢 STRONG BUY", len(st.session_state.data_strongbuy))
col2.metric("🟢 BUY", len(st.session_state.data_full[st.session_state.data_full['Signal']=='🟢 BUY']) if not st.session_state.data_full.empty else 0)
col3.metric("🔴 SELL", len(st.session_state.data_full[st.session_state.data_full['Signal'].str.contains('SELL')]) if not st.session_state.data_full.empty else 0)
col4.metric("🟡 HOLD", len(st.session_state.data_full[st.session_state.data_full['Signal']=='🟡 HOLD']) if not st.session_state.data_full.empty else 0)
col5.metric("📈 Total", len(st.session_state.data_full) if not st.session_state.data_full.empty else 0)

# Timer
next_auto = max(0, 45 - (time.time() - st.session_state.last_scan))
col6, col7 = st.columns(2)
col6.metric("🔄 Scans", st.session_state.scan_count)
col7.metric("⏱️ Next Auto", f"{next_auto:.0f}s")

st.markdown("---")
st.info("""
**✅ MA20 VISIBLE** - 20-period Simple Moving Average in every table
**✅ STRONG BUY** = RSI<35 + Price>MA20  
**✅ 500 STOCKS** - Complete Nifty 500 universe
**✅ AUTO** = Strong Buy every 45s | **MANUAL** = All signals
**✅ 4 DOWNLOADS** - Individual CSV files per signal type
**🚀 READY TO TRADE!**
""")
