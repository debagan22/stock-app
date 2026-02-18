import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import requests
import numpy as np

# Session state
if 'data_full' not in st.session_state: st.session_state.data_full = pd.DataFrame()
if 'data_strongbuy' not in st.session_state: st.session_state.data_strongbuy = pd.DataFrame()
if 'last_scan' not in st.session_state: st.session_state.last_scan = 0
if 'scan_count' not in st.session_state: st.session_state.scan_count = 0
if 'auto_active' not in st.session_state: st.session_state.auto_active = False
if 'batch_progress' not in st.session_state: st.session_state.batch_progress = 0

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="🚀")
st.title("🔥 NIFTY 500 SCANNER v2.0")

# 🔥 DYNAMIC OFFICIAL NIFTY 500 LIST
@st.cache_data(ttl=86400)
def get_true_nifty500():
    """Fetch OFFICIAL NSE Nifty 500 symbols dynamically"""
    try:
        url = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
        df = pd.read_csv(url)
        symbols = [sym + '.NS' for sym in df['Symbol'].tolist() if pd.notna(sym) and sym != '—']
        st.success(f"✅ **OFFICIAL NIFTY 500** | **{len(symbols)} stocks** loaded from NSE")
        return symbols[:500]  # Top 500
    except:
        st.warning("❌ NSE CSV failed, using cached backup")
        return [
            "RELIANCE.NS","HDFCBANK.NS","TCS.NS","INFY.NS","HINDUNILVR.NS","ICICIBANK.NS","KOTAKBANK.NS","ITC.NS","LT.NS","BHARTIARTL.NS",
            "AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","NESTLEIND.NS","ULTRACEMCO.NS","POWERGRID.NS","TATAMOTORS.NS",
            "JSWSTEEL.NS","ONGC.NS","COALINDIA.NS","M&M.NS","NTPC.NS","TECHM.NS","WIPRO.NS","LTIM.NS","TATASTEEL.NS","CIPLA.NS","DRREDDY.NS"
        ]  # Top 30 fallback

nifty500 = get_true_nifty500()

def scan_stock(symbol):
    """Scan single stock with enhanced signals"""
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="30d")
        if len(data) < 20: 
            return None
            
        # Technical indicators
        data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
        data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
        data['MA50'] = ta.trend.SMAIndicator(data['Close'], window=50).sma_indicator()
        data['Volume_SMA'] = ta.volume.VolumeSMAIndicator(data['Volume'], window=20).volume_sma()
        
        # Latest values
        rsi = data['RSI'].iloc[-1]
        ma20 = data['MA20'].iloc[-1]
        ma50 = data['MA50'].iloc[-1]
        price = data['Close'].iloc[-1]
        volume_ratio = data['Volume'].iloc[-1] / data['Volume_SMA'].iloc[-1]
        
        # Enhanced signal logic
        if rsi < 35 and price > ma20 and volume_ratio > 1.2:
            signal = '🟢 STRONG BUY'
            strength = '🔥🔥🔥'
        elif rsi < 30 and price > ma20:
            signal = '🟢 BUY'
            strength = '🔥🔥'
        elif rsi > 70 and price < ma20:
            signal = '🔴 STRONG SELL'
            strength = '⚡⚡⚡'
        elif rsi > 65:
            signal = '🔴 SELL'
            strength = '⚡⚡'
        else:
            signal = '🟡 HOLD'
            strength = '➖➖'
        
        return {
            'Stock': symbol.replace('.NS', ''),
            'Price': f"₹{price:.1f}",
            'Change%': f"{((price/data['Close'].iloc[-2]-1)*100):+.1f}%",
            'MA20': f"₹{ma20:.1f}",
            'MA50': f"₹{ma50:.1f}",
            'RSI': f"{rsi:.1f}",
            'VolRatio': f"{volume_ratio:.1f}x",
            'Signal': signal,
            'Strength': strength
        }
    except:
        return None

def scan_stocks_batch(symbols, batch_num):
    """Scan batch with progress"""
    results = []
    progress_text = st.empty()
    
    for i, symbol in enumerate(symbols):
        result = scan_stock(symbol)
        if result:
            results.append(result)
        
        # Update progress
        pct = (i+1)/len(symbols)
        progress_text.text(f"Batch {batch_num}: {i+1}/{len(symbols)} stocks | Found: {len(results)} signals")
        time.sleep(0.2)  # Rate limit
    
    progress_text.empty()
    return pd.DataFrame(results)

def scan_true_500_batched():
    """Scan all 500 stocks in 5 batches"""
    all_results = []
    batches = [nifty500[i:i+100] for i in range(0, len(nifty500), 100)]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, batch in enumerate(batches):
        with st.container():
            status_text.text(f"🔥 Scanning **BATCH {i+1}/5** ({len(batch)} stocks)...")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Batch Progress", f"{i+1}/{len(batches)}")
            with col2:
                st.metric("Signals Found", len(all_results))
            
            batch_results = scan_stocks_batch(batch, i+1)
            all_results.append(batch_results)
            time.sleep(2)  # Short pause between batches
        
        progress_bar.progress((i+1)/len(batches))
    
    progress_bar.empty()
    status_text.empty()
    full_df = pd.concat(all_results, ignore_index=True)
    
    # Auto-filter STRONG BUY
    strongbuy_df = full_df[full_df['Signal'] == '🟢 STRONG BUY'].sort_values('RSI')
    st.session_state.data_strongbuy = strongbuy_df
    
    return full_df

# 🔥 AUTO SCAN CHECK
if st.session_state.auto_active and st.session_state.last_scan > 0:
    time_since = time.time() - st.session_state.last_scan
    if time_since > 1800:  # 30 min
        st.info("🤖 **AUTO SCAN TRIGGERED** - Refreshing data...")
        with st.spinner("Auto-scanning..."):
            st.session_state.data_full = scan_true_500_batched()
            st.session_state.scan_count += 1
            st.session_state.last_scan = time.time()
        st.rerun()

# 🔥 CONTROLS
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_active = col1.toggle("🤖 AUTO SCAN (every 30min)", value=st.session_state.auto_active)

if col2.button("🚀 SCAN NIFTY 500 NOW (8-10min)", type="primary", use_container_width=True, disabled=not nifty500):
    with st.spinner("🔥 Starting full Nifty 500 scan..."):
        st.session_state.data_full = scan_true_500_batched()
        st.session_state.data_strongbuy = st.session_state.data_full[
            st.session_state.data_full['Signal'] == '🟢 STRONG BUY'
        ].sort_values('RSI')
        st.session_state.scan_count += 1
        st.session_state.last_scan = time.time()
    st.rerun()

if col3.button("🗑️ CLEAR DATA", use_container_width=True):
    for key in ['data_full', 'data_strongbuy', 'scan_count', 'last_scan']:
        st.session_state[key] = 0 if key in ['scan_count', 'last_scan'] else pd.DataFrame()
    st.rerun()

# 🔥 ENHANCED TABS
tab1, tab2, tab3, tab4 = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])

with tab1:
    st.markdown("### 🚀 STRONG BUY (RSI<35 + Price>MA20 + High Volume)")
    if not st.session_state.data_strongbuy.empty:
        df = st.session_state.data_strongbuy
        col1, col2 = st.columns(2)
        col1.metric("🚀 Top Signals", len(df))
        col2.metric("Best RSI", df['RSI'].min())
        st.dataframe(df, height=600, use_container_width=True, hide_index=True)
        st.download_button("💾 DOWNLOAD CSV", df.to_csv(index=False), "nifty500-strongbuy.csv", "📥")
    elif st.session_state.auto_active:
        st.info("🤖 **AUTO SCANNING** - Top picks loading...")
    else:
        st.warning("🔥 **Click SCAN or enable AUTO**")

with tab2:
    st.markdown("### 🟢 BUY (RSI<30 + Price>MA20)")
    if not st.session_state.data_full.empty:
        buy_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟢 BUY'].sort_values('RSI')
        st.metric("Count", len(buy_df))
        if len(buy_df) > 0:
            st.dataframe(buy_df.head(50), height=500, use_container_width=True)
            st.download_button("💾 DOWNLOAD", buy_df.to_csv(index=False), "nifty500-buy.csv")
    else:
        st.info("📈 **Scan first**")

with tab3:
    st.markdown("### 🔴 SELL (RSI>65/70)")
    if not st.session_state.data_full.empty:
        sell_df = st.session_state.data_full[st.session_state.data_full['Signal'].str.contains('SELL')].sort_values('RSI', ascending=False)
        st.metric("Count", len(sell_df))
        if len(sell_df) > 0:
            st.dataframe(sell_df.head(50), height=500, use_container_width=True)
            st.download_button("💾 DOWNLOAD", sell_df.to_csv(index=False), "nifty500-sell.csv")
    else:
        st.info("📉 **Scan first**")

with tab4:
    st.markdown("### 🟡 HOLD (Neutral)")
    if not st.session_state.data_full.empty:
        hold_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟡 HOLD'].head(50)
        st.metric("Showing", "Top 50")
        st.dataframe(hold_df, height=500, use_container_width=True)
    else:
        st.info("⚖️ **Scan first**")

# 🔥 LIVE DASHBOARD
st.markdown("---")
cols = st.columns(6)
signals = {
    '🟢 STRONG BUY': len(st.session_state.data_strongbuy),
    '🟢 BUY': len(st.session_state.data_full[st.session_state.data_full['Signal']=='🟢 BUY']),
    '🔴 SELL': len(st.session_state.data_full[st.session_state.data_full['Signal'].str.contains('SELL')]),
    '🟡 HOLD': len(st.session_state.data_full[st.session_state.data_full['Signal']=='🟡 HOLD'])
}

for i, (label, count) in enumerate(signals.items()):
    cols[i].metric(label, count)

col_last = st.columns(1)[0]
col_last.metric("📈 Total Scanned", len(st.session_state.data_full))
col_last.metric("🔄 Scans Done", st.session_state.scan_count)

# Time since last scan
if st.session_state.last_scan > 0:
    mins_since = int((time.time() - st.session_state.last_scan) / 60)
    col_last.metric("⏱️ Last Scan", f"{mins_since} mins ago")

st.info("""
**🚀 v2.0 Updates**:
- ✅ **OFFICIAL NSE 500 list** (dynamic CSV fetch)
- 🔧 **Fixed STRONG BUY filter**
- 📊 **Enhanced metrics** (MA50, VolRatio, Change%)
- 🤖 **AUTO SCAN** every 30min
- ⚡ **Better progress + batch metrics**
- 💾 **Individual CSV downloads**
**⏱️ Scan time**: 8-10min | **Rate limited** for yfinance
""")
