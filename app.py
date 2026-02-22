import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np
from datetime import datetime, time as dt_time
import pytz

st.set_page_config(layout="wide", page_icon="📈")

# ✅ FULL NIFTY 100 STOCKS (100 stocks)
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

# SESSION STATE
if 'expanded_signals' not in st.session_state:
    st.session_state.expanded_signals = {}
if 'all_data' not in st.session_state:
    st.session_state.all_data = []
if 'scan_complete' not in st.session_state:
    st.session_state.scan_complete = False

# TIME FUNCTIONS
IST = pytz.timezone('Asia/Kolkata')
def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5: 
        return False
    return dt_time(9, 15) <= now.time() <= dt_time(15, 30)

@st.cache_data(ttl=60)
def get_nifty_data(symbol):
    try:
        ticker = yf.Ticker(symbol + '.NS')
        hist = ticker.history(period="3mo")
        if len(hist) >= 30:
            price = hist['Close'].iloc[-1]
            rsi = ta.momentum.RSIIndicator(hist['Close'], 14).rsi().iloc[-1]
            macd = ta.trend.MACD(hist['Close'])
            macd_line = macd.macd().iloc[-1]
            signal_line = macd.macd_signal().iloc[-1]
            ma20 = hist['Close'].rolling(20).mean().iloc[-1]
            change = ((price / hist['Close'].iloc[-2] - 1) * 100) if len(hist) > 1 else 0
            atr = ta.volatility.AverageTrueRange(hist['High'], hist['Low'], hist['Close'], 14).average_true_range().iloc[-1]
            
            category = '🟦 NIFTY 50' if symbol in NIFTY_50 else '🟨 NIFTY NEXT 50'
            status = '🔴 LIVE' if is_market_open() else '📊 EOD'
            
            # SIGNAL LOGIC + PRICE TARGETS
            rsi_super = rsi < 35
            rsi_buy = rsi < 45
            rsi_sell = rsi > 65
            macd_bull = macd_line > signal_line
            ma_bull = price > ma20
            confirmations = sum([rsi_super, macd_bull, ma_bull])
            
            # Initialize price targets
            buy_entry = sell_entry = sell_target1 = sell_target2 = buy_target1 = np.nan
            risk_reward = 1.0
            
            if confirmations == 3:  # SUPER BUY
                signal = '🚀 SUPER BUY'
                signal_class = 'super-buy'
                buy_entry = min(price * 0.98, ma20 * 1.01)
                sell_target1 = price * 1.05
                sell_target2 = price + (atr * 1.5)
                risk_reward = 3.0
            elif confirmations >= 2:  # STRONG BUY
                signal = '🟢 STRONG BUY'
                signal_class = 'strong-buy'
                buy_entry = price * 0.985
                sell_target1 = price * 1.04
                sell_target2 = price + atr
                risk_reward = 2.5
            elif rsi_buy or macd_bull:  # BUY
                signal = '🟢 BUY'
                signal_class = 'buy'
                buy_entry = price * 0.99
                sell_target1 = price * 1.03
                sell_target2 = price + (atr * 0.8)
                risk_reward = 1.8
            elif rsi_sell or not macd_bull:  # SELL
                signal = '🔴 SELL'
                signal_class = 'sell'
                sell_entry = max(price * 1.02, ma20 * 0.99)
                buy_target1 = price * 0.95
                risk_reward = 2.0
            else:  # HOLD
                signal = '🟡 HOLD'
                signal_class = 'hold'
            
            return {
                'Stock': symbol,
                'Price': f"₹{price:.0f}",
                'Change': f"{change:.1f}%",
                'RSI': f"{rsi:.1f}",
                'MACD': f"{macd_line:.2f}",
                'Signal_Line': f"{signal_line:.2f}",
                'MA20': f"₹{ma20:.0f}",
                'Price/MA20': '📈' if ma_bull else '📉',
                'Signal': signal,
                'Category': category,
                'Status': status,
                'RSI_Value': rsi,
                'Signal_Class': signal_class,
                # 🎯 PRICE TARGETS
                'Buy_Entry': f"₹{buy_entry:.0f}" if not np.isnan(buy_entry) else '-',
                'Sell_T1': f"₹{sell_target1:.0f}" if not np.isnan(sell_target1) else '-',
                'Sell_T2': f"₹{sell_target2:.0f}" if not np.isnan(sell_target2) else '-',
                'RR_Ratio': f"{risk_reward:.1f}:1",
                'Sell_Entry': f"₹{sell_entry:.0f}" if not np.isnan(sell_entry) else '-',
                'Buy_T1': f"₹{buy_target1:.0f}" if not np.isnan(buy_target1) else '-',
                'ATR': f"₹{atr:.0f}"
            }
    except:
        return None

def signal_category(category_data, signal_type):
    return [stock for stock in category_data if stock['Signal'] == signal_type]

def display_category_section(category_name, all_data):
    category_data = [d for d in all_data if d['Category'] == category_name]
    
    if not category_data:
        return
    
    st.markdown(f"## {category_name} | **{len(category_data)} Stocks**")
    
    signals = {
        '🚀 SUPER BUY': signal_category(category_data, '🚀 SUPER BUY'),
        '🟢 STRONG BUY': signal_category(category_data, '🟢 STRONG BUY'),
        '🟢 BUY': signal_category(category_data, '🟢 BUY'),
        '🔴 SELL': signal_category(category_data, '🔴 SELL'),
        '🟡 HOLD': signal_category(category_data, '🟡 HOLD')
    }
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    for i, (signal_name, signal_stocks) in enumerate(signals.items()):
        col = [col1, col2, col3, col4, col5][i]
        with col:
            signal_key = f"{category_name}_{signal_name.replace(' ', '_').replace('/', '')}"
            
            if st.button(f"**{signal_name}**\n{len(signal_stocks)}", 
                        key=f"{signal_key}_btn", use_container_width=True):
                st.session_state.expanded_signals[signal_key] = not st.session_state.expanded_signals.get(signal_key, False)
                st.rerun()
            
            if st.session_state.expanded_signals.get(signal_key, False):
                with st.expander(f"📋 **{len(signal_stocks)} Stocks**", expanded=True):
                    if signal_stocks:
                        df = pd.DataFrame(signal_stocks)
                        st.dataframe(df[['Stock', 'Price', 'RSI', 'Buy_Entry', 'Sell_T1', 'RR_Ratio', 'ATR']], 
                                   use_container_width=True, hide_index=True)
                    else:
                        st.info("No stocks")

# 🔥 HEADER
st.markdown("# 🚀 **NIFTY 100 LIVE SCANNER** | RSI + MACD + MA20 + PRICE TARGETS")
status = "🔴 **LIVE MARKET**" if is_market_open() else "📊 **MARKET CLOSED**"
st.success(status)

# MAIN CONTROLS
col1, col2 = st.columns([3,1])
with col1:
    if st.button("🚀 **SCAN ALL 100 NIFTY STOCKS** 🚀", type="primary", use_container_width=True):
        st.session_state.scan_complete = True
        st.session_state.all_data = []
        st.cache_data.clear()
        st.rerun()
with col2:
    if st.button("🔄 REFRESH", use_container_width=True):
        st.cache_data.clear()
        st.session_state.all_data = []
        st.rerun()

# SCAN EXECUTION
if st.session_state.scan_complete:
    if not st.session_state.all_data:
        st.info("🔄 **SCANNING ALL 100 NIFTY STOCKS** (~2-3 mins)")
        progress = st.progress(0)
        
        for i, symbol in enumerate(NIFTY100_COMPLETE):
            data = get_nifty_data(symbol)
            if data:
                st.session_state.all_data.append(data)
            progress.progress((i + 1) / 100)
            time.sleep(0.1)
        
        st.success(f"✅ **SCAN COMPLETE** - {len(st.session_state.all_data)}/100 stocks")
        st.rerun()
    
    all_data = [d for d in st.session_state.all_data if d]
    
    # OVERVIEW
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("📊 Scanned", f"{len(all_data)}/100")
    with col2: st.metric("🚀 Super Buys", len([d for d in all_data if d['Signal']=='🚀 SUPER BUY']))
    with col3: st.metric("🟦 Nifty 50", len([d for d in all_data if d['Category']=='🟦 NIFTY 50']))
    with col4: st.metric("⏱️", datetime.now(IST).strftime("%H:%M IST"))
    
    # CATEGORIES
    display_category_section('🟦 NIFTY 50', all_data)
    st.markdown("---")
    display_category_section('🟨 NIFTY NEXT 50', all_data)
    
    # FULL TABLE
    st.markdown("---")
    st.subheader("📋 **COMPLETE RESULTS** (RSI Sorted)")
    df = pd.DataFrame(all_data).sort_values('RSI_Value')
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    st.download_button("💾 DOWNLOAD CSV", df.to_csv(index=False), "nifty100-complete.csv")

st.markdown("---")
st.info("👆 **CLICK SIGNAL CARDS** to see stocks with BUY/SELL prices | **ALL 100 NIFTY STOCKS**")
