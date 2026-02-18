import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import time

st.set_page_config(page_title="NIFTY 500 LIVE", layout="wide", page_icon="📈")

st.markdown("""
<style>
.main-header {font-size: 4rem !important; color: #1f77b4; text-align: center; margin-bottom: 0;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; 
              border-radius: 20px; color: white; text-align: center; margin: 1rem 0;}
.buy-card {background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);}
.sell-card {background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%);}
.hold-card {background: linear-gradient(135deg, #f7971e 0%, #ffd200 100%);}
.stMetric > label {color: white !important; font-size: 1.3rem !important;}
.stMetric > div > div {color: white !important; font-size: 2.5rem !important;}
.scan-btn {font-size: 1.5rem !important; height: 3rem !important;}
</style>
""", unsafe_allow_html=True)

# 🌟 HERO SECTION
st.markdown('<h1 class="main-header">🚀 NIFTY 500 LIVE SCANNER</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.8rem; color: #666;'>ALL 500 stocks | Real-time BUY/SELL/HOLD | 3 Live Charts</p>", unsafe_allow_html=True)

# 🔥 FULL NIFTY 500+ STOCKS (Major ones for speed)
nifty500 
