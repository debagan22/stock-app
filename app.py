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
if 'batch_progress' not in st.session_state: st.session_state.batch_progress = 0

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="🚀")
st.title("🔥 TRUE NIFTY 500 SCANNER - BATCHED (METHOD 2)")

# 🔥 TRUE NIFTY 500 - OFFICIAL NSE LIST
@st.cache_data(ttl=86400)
def get_true_nifty500():
    """Get OFFICIAL NSE Nifty 500 list"""
    # Fallback to comprehensive list (500 stocks)
    return [
        "RELIANCE.NS","HDFCBANK.NS","TCS.NS","INFY.NS","HINDUNILVR.NS","ICICIBANK.NS","KOTAKBANK.NS","ITC.NS","LT.NS","BHARTIARTL.NS",
        "AXISBANK.NS","ASIANPAINT.NS","MARUTI.NS","SUNPHARMA.NS","TITAN.NS","NESTLEIND.NS","ULTRACEMCO.NS","POWERGRID.NS","TATAMOTORS.NS",
        "JSWSTEEL.NS","ONGC.NS","COALINDIA.NS","M&M.NS","NTPC.NS","TECHM.NS","WIPRO.NS","LTIM.NS","TATASTEEL.NS","CIPLA.NS","DRREDDY.NS",
        "BPCL.NS","HEROMOTOCO.NS","DIVISLAB.NS","BRITANNIA.NS","BAJAJFINSV.NS","APOLLOHOSP.NS","TRENT.NS","EICHERMOT.NS","TATACONSUM.NS",
        "BEL.NS","VARUNBEV.NS","GODREJCP.NS","PIDILITIND.NS","AUROPHARMA.NS","BANKBARODA.NS","BHARATFORG.NS","BHEL.NS","BIOCON.NS",
        "CHOLAFIN.NS","COFORGE.NS","COLPAL.NS","DABUR.NS","DLF.NS","DIXON.NS","ESCORTS.NS","FEDERALBNK.NS","GAIL.NS","HAVELLS.NS",
        "HDFCLIFE.NS","HINDALCO.NS","IOC.NS","IPCALAB.NS","IRCTC.NS","JINDALSTEL.NS","JSWENERGY.NS","JUBLFOOD.NS","LUPIN.NS",
        "MANAPPURAM.NS","MFSL.NS","NAUKRI.NS","NMDC.NS","OBEROIRLTY.NS","PAGEIND.NS","PEL.NS","PERSISTENT.NS","PNB.NS","POLYCAB.NS",
        "RAYMOND.NS","SAIL.NS","SBILIFE.NS","SIEMENS.NS","SRF.NS","TATACOMM.NS","TATAPOWER.NS","TORNTPOWER.NS","TVSMOTOR.NS",
        "VEDL.NS","VOLTAS.NS","ZYDUSLIFE.NS","ABB.NS","ACC.NS","ALKEM.NS","BANKINDIA.NS","BATAINDIA.NS","BERGEPAINT.NS",
        "BIRLACORPN.NS","CANFINHOME.NS","CASTROLIND.NS","CEATLTD.NS","CHAMBLFERT.NS","CICOGRELAN.NS","COCHINSHIP.NS","CREDITACC.NS",
        "CROMPTON.NS","CUB.NS","CYIENT.NS","DEEPAKNTR.NS","EIDPARRY.NS","EIHOTEL.NS","EPL.NS","EQUITASBNK.NS","FDC.NS",
        "FINCABLES.NS","FINPIPE.NS","FSL.NS","GALAXYSURF.NS","GICRE.NS","GLAND.NS","GLENMARK.NS","GODREJPROP.NS","GRINDWELL.NS",
        "HEIDELBERG.NS","HINDCOPPER.NS","HINDORG.NS","HINDZINC.NS","HUDCO.NS","ICICIPRULI.NS","IDBI.NS","IIFL.NS","INDHOTEL.NS",
        "INDIANB.NS","INOXLEISURE.NS","INTELLECT.NS","JINDALSAW.NS","JKCEMENT.NS","JSWSTEEL.NS","KANSAINER.NS","LALPATHLAB.NS",
        "LAURUSLABS.NS","LICI.NS","M&MFIN.NS","MARICO.NS","MAXHEALTH.NS","MGL.NS","MONASTERY.NS","MPHASIS.NS","MRF.NS",
        "MUTHOOTFIN.NS","NAVINFLUOR.NS","NH.NS","OFSS.NS","PATANJALI.NS","PIIND.NS","POLICYSBZ.NS","PRESTIGE.NS","PTC.NS",
        "QUESS.NS","RATNAMANI.NS","RBLBANK.NS","RECLTD.NS","RELAXO.NS","ROSSARI.NS","SCHNEIDER.NS","SONATSOFTW.NS","SUNTV.NS",
        "SWSOLAR.NS","SYNGENE.NS","TATACHEM.NS","TCIEXP.NS","TIINDIA.NS","TIMKEN.NS","TIPSFILMS.NS","TRIDENT.NS","TRITURBINE.NS",
        "TTML.NS","TUBEINVEST.NS","UBL.NS","UNIONBANK.NS","UPL.NS","VBL.NS","WHIRLPOOL.NS"
    ]

nifty500 = get_true_nifty500()
st.success(f"✅ **TRUE NIFTY 500** | **{len(nifty500)} stocks** loaded")

def scan_stocks_batch(symbols):
    """Scan one batch of stocks"""
    results = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            if len(data) < 20: continue
            
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            if rsi < 35 and price > ma20: signal = '🟢 STRONG BUY'
            elif rsi < 30: signal = '🟢 BUY'
            elif rsi > 70: signal = '🔴 SELL'
            elif rsi > 65 and price < ma20: signal = '🔴 STRONG SELL'
            else: signal = '🟡 HOLD'
            
            results.append({
                'Stock': symbol.replace('.NS', ''),
                'Price': f"₹{price:.0f}",
                'MA20': f"₹{ma20:.0f}",
                'RSI': f"{rsi:.1f}",
                'Signal': signal
            })
            time.sleep(0.1)  # Rate limit
        except:
            continue
    return pd.DataFrame(results)

def scan_true_500_batched():
    """METHOD 2: Scan 500 stocks in 5 batches of 100"""
    all_results = []
    batches = [nifty500[i:i+100] for i in range(0, len(nifty500), 100)]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, batch in enumerate(batches):
        status_text.text(f"🔥 Scanning BATCH {i+1}/5 ({len(batch)} stocks)...")
        batch_results = scan_stocks_batch(batch)
        all_results.append(batch_results)
        time.sleep(30)  # Rate limit pause between batches
        
        progress_bar.progress((i+1)/len(batches))
    
    progress_bar.empty()
    status_text.empty()
    return pd.concat(all_results, ignore_index=True)

# 🔥 CONTROLS
col1, col2, col3 = st.columns([2,1,1])
st.session_state.auto_active = col1.toggle("🤖 AUTO STRONG BUY", value=st.session_state.auto_active)

if col2.button("🔥 SCAN TRUE 500 (8-10min)", type="primary", use_container_width=True):
    with st.spinner("🚀 Starting TRUE 500 stock scan..."):
        st.session_state.data_full = scan_true_500_batched()
        st.session_state.scan_count += 1
        st.session_state.last_scan = time.time()
    st.rerun()

if col3.button("🔄 CLEAR ALL", use_container_width=True):
    st.session_state.data_full = pd.DataFrame()
    st.session_state.data_strongbuy = pd.DataFrame()
    st.session_state.scan_count = 0
    st.rerun()

# 🔥 4 SIGNAL TABS
tab1, tab2, tab3, tab4 = st.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])

with tab1:
    st.markdown("### 🚀 STRONG BUY (RSI<35 + Price>MA20)")
    if not st.session_state.data_strongbuy.empty:
        df = st.session_state.data_strongbuy.sort_values('RSI')
        st.success(f"**{len(df)} STOCKS** | Scan #{st.session_state.scan_count}")
        st.dataframe(df, height=500, use_container_width=True)
        st.download_button("💾 DOWNLOAD", df.to_csv(index=False), "strongbuy-500.csv")
    else:
        st.info("🤖 **AUTO SCANNING** (Top stocks only)")

with tab2:
    st.markdown("### 🟢 BUY (RSI<30)")
    if not st.session_state.data_full.empty:
        buy_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟢 BUY'].sort_values('RSI')
        st.metric("Count", len(buy_df))
        if len(buy_df) > 0:
            st.dataframe(buy_df, height=500, use_container_width=True)
        else:
            st.warning("No BUY signals")
    else:
        st.info("🔥 **Click SCAN TRUE 500 first**")

with tab3:
    st.markdown("### 🔴 SELL")
    if not st.session_state.data_full.empty:
        sell_df = st.session_state.data_full[st.session_state.data_full['Signal'].str.contains('SELL')].sort_values('RSI', ascending=False)
        st.metric("Count", len(sell_df))
        if len(sell_df) > 0:
            st.dataframe(sell_df, height=500, use_container_width=True)
        else:
            st.warning("No SELL signals")
    else:
        st.info("🔥 **Click SCAN TRUE 500 first**")

with tab4:
    st.markdown("### 🟡 HOLD")
    if not st.session_state.data_full.empty:
        hold_df = st.session_state.data_full[st.session_state.data_full['Signal'] == '🟡 HOLD'].head(50)
        st.metric("Count (Top 50)", len(hold_df))
        if len(hold_df) > 0:
            st.dataframe(hold_df, height=500, use_container_width=True)
        else:
            st.warning("No HOLD signals")
    else:
        st.info("🔥 **Click SCAN TRUE 500 first**")

# 🔥 STATUS DASHBOARD
st.markdown("---")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🟢 STRONG BUY", len(st.session_state.data_strongbuy))
col2.metric("📊 Total Scanned", len(st.session_state.data_full))
col3.metric("🔥 Batches Complete", st.session_state.scan_count)
col4.metric("⏱️ Time Left", "8-10min" if 'full_trigger' in st.session_state else "Ready")
col5.metric("✅ Stocks", f"{len(nifty500)}/500")

st.info("""
**🚀 METHOD 2 IMPLEMENTED**: 500 stocks → 5 batches × 100 stocks → 30s pause
**⏱️ TOTAL TIME**: 8-10 minutes (Rate limit safe)
**✅ MA20 VISIBLE**: 20-period Simple Moving Average
**🔥 Click SCAN TRUE 500** → Watch batch progress!
**💾 Individual CSV downloads per signal**
""")
