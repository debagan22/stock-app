import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time
import numpy as np
from datetime import datetime, time as dt_time
import pytz

st.set_page_config(layout="wide", page_icon="📈")

# ✅ FULL NIFTY 100 STOCKS
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

# STYLING
st.markdown("""
<style>
.main-header {font-size:4rem !important;font-weight:900 !important;background:linear-gradient(90deg,#667eea 0%,#764ba2 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-align:center;}
.metric-card {background:linear-gradient(145deg,#1e3a8a,#3b82f6);padding:1.5rem;border-radius:15px;box-shadow:0 10px 30px rgba(59,130,246,0.3);cursor:pointer;}
.super-buy {background:linear-gradient(145deg
