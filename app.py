import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np
from datetime import datetime, time as dt_time
import pytz

st.set_page_config(layout="wide", page_icon="📈", initial_sidebar_state="expanded")

# ✅ OFFICIAL NIFTY 100 STOCKS (100 stocks) [web:72]
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

# 🔥 STYLING
st.markdown("""
<style>
.main-header {font-size:4rem !important;font-weight:900 !important;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;margin-bottom:0 !important;}
.metric-card {background:linear-gradient(145deg,#1e3a8a,#3b82f6);padding:1.5rem;border-radius:15px;box-shadow:0 10px 30px rgba(59,130,246,0.3);border:2px solid rgba(255,255,255,0.1);cursor:pointer;transition:all 0.3s;}
.super-buy {background:linear-gradient(145deg,#10b981,#059669) !important;box-shadow:0 0 30px #10b981 !important;}
.strong-buy {background:linear-gradient(145deg,#3b82f6,#1d4ed8) !important;box-shadow:0 0 25px #3b82f6 !important;}
.buy {background:linear-gradient(145deg,#06b6d4,#0891b2) !important;box-shadow:0 0 20px #06b6d4 !important;}
.sell {background:linear-gradient(145deg,#ef4444,#dc2626) !important;box-shadow:0 0 25px #ef4444 !important;}
.hold {background:linear-gradient(145deg,#eab308,#ca8a04) !important;box-shadow:0 0 20px #eab308 !important;}
.metric-card:hover {transform:translateY(-5px) scale(1.02)!important;box-shadow:0 20px 40px rgba(0,0,0,0.3)!important;}
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if 'expanded_signals' not in st.session_state: st.session_state.expanded_signals = {}
if 'all_data' not in st.session_state: st.session_state.all_data = []
if 'scan_complete' not in st.session_state: st.session_state.scan_complete = False

# TIME FUNCTIONS
IST = pytz.timezone('Asia/Kolkata')
def is_market_open():
    now = datetime.now(IST)
    if now.weekday() >= 5: return False
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
            
            # SIGNAL LOGIC
            rsi_super = rsi < 35
            rsi_buy = rsi < 45
            rsi_sell = rsi > 65
            macd_bull = macd_line > signal_line
            ma_bull = price > ma20
            confirmations = sum([rsi_super, macd_bull, ma_bull])
            
            # 🎯 PRICE TARGETS + SIGNALS
            if confirmations
