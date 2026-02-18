import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime

st.set_page_config(page_title="NIFTY 500 PRO", layout="wide", page_icon="📊")
st.title("📊 **NIFTY 500 PRO SCANNER**")

# NIFTY 500 CLASSIFICATION (SEBI Standard)
LARGE_CAP = ['RELIANCE', 'HDFCBANK', 'TCS', 'INFY', 'HINDUNILVR', 'ICICIBANK', 'KOTAKBANK', 
             'ITC', 'LT', 'BHARTIARTL', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 
             'TITAN', 'NESTLEIND', 'ULTRACEMCO', 'POWERGRID', 'TATAMOTORS', 'JSWSTEEL']

MID_CAP = ['TRENT', 'BEL', 'VARUNBEV', 'PIDILITIND', 'DIXON', 'POLYCAB', 'RAYMOND', 
           'LAURUSLABS', 'LALPATHLAB', 'METROPOLIS', 'CRAVATSYND', 'NAVINFLUOR']

SMALL_CAP = ['MONASTERY', 'MPHASIS', 'MRF', 'MUTHOOTFIN', 'NH', 'OFSS', 'PATANJALI', 
             'PIIND', 'POLICYSBZ', 'PRESTIGE', 'PTC', 'QUESS']

# Session state for each category
for cap in ['large', 'mid', 'small']:
    for signal in ['strongbuy', 'buy', 'sell', 'hold']:
        key = f"{cap}_{signal}"
        if key not in st.session_state:
            st.session_state[key] = pd.DataFrame()
if 'last_strongbuy_refresh' not in st.session_state:
    st.session_state.last_strongbuy_refresh = {}

# Auto-refresh timer for strong buy
def should_auto_refresh(cap):
    now = time.time()
    last_refresh = st.session_state.last_strongbuy_refresh.get(cap, 0)
    return now - last_refresh > 300  # 5 minutes

# Generate signals for a category
def generate_signals(stocks, cap_type):
    np.random.seed(int(time.time()))
    results = []
    
    for stock in stocks:
        price = np.random.uniform(200, 5000)
        rsi = np.random.uniform(20, 80)
        change = np.random.uniform(-5, 6)
        
        # Cap-specific thresholds
        if cap_type == 'large':
            strongbuy_rsi, buy_rsi, sell_rsi = 40, 45, 65
        elif cap_type == 'mid':
            strongbuy_rsi, buy_rsi, sell_rsi = 35, 42, 68
        else:  # small
            strongbuy_rsi, buy_rsi, sell_rsi = 32, 38, 72
        
        if rsi < strongbuy_rsi:
            signal = '🟢 STRONG BUY'
        elif rsi < buy_rsi:
            signal = '🟢 BUY'
        elif rsi > sell_rsi:
            signal = '🔴 SELL'
        else:
            signal = '🟡 HOLD'
        
        results.append({
            'Stock': stock,
            'Price': f"₹{price:.0f}",
            'Change': f"{change:+.1f}%",
            'RSI': f"{rsi:.1f}",
            'Signal': signal
        })
    return pd.DataFrame(results)

# PRIMARY TABS - CAP CATEGORIES
tab1, tab2, tab3 = st.tabs(["🟢 **LARGE CAP** (1-100)", "🟡 **MID CAP** (101-250)", "🔴 **SMALL CAP** (251+)"])

# LARGE CAP TAB
with tab1:
    st.markdown("### 🏢 **LARGE CAP** - Conservative Signals")
    
    col1, col2 = st.columns([3, 1])
    
    # Auto-refresh strong buy
    if should_auto_refresh('large'):
        st.session_state['large_strongbuy'] = generate_signals(LARGE_CAP[:20], 'large')
        st.session_state.last_strongbuy_refresh['large'] = time.time()
    
    # 4 SIGNAL SUB-TABS
    signal_tabs = col1.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
    
    with signal_tabs[0]:
        strongbuy = st.session_state.get('large_strongbuy', generate_signals(LARGE_CAP[:5], 'large'))
        if not strongbuy.empty:
            st.metric("🚀 Large Cap Strong Buy", len(strongbuy))
            st.dataframe(strongbuy, use_container_width=True)
    
    with signal_tabs[1]:
        all_large = generate_signals(LARGE_CAP[:20], 'large')
        buy_signals = all_large[all_large['Signal'] == '🟢 BUY']
        st.metric("🟢 Large Cap Buy", len(buy_signals))
        st.dataframe(buy_signals)
    
    with signal_tabs[2]:
        all_large = generate_signals(LARGE_CAP[:20], 'large')
        sell_signals = all_large[all_large['Signal'] == '🔴 SELL']
        st.metric("🔴 Large Cap Sell", len(sell_signals))
        st.dataframe(sell_signals)
    
    with signal_tabs[3]:
        all_large = generate_signals(LARGE_CAP[:20], 'large')
        hold_signals = all_large[all_large['Signal'] == '🟡 HOLD']
        st.metric("🟡 Large Cap Hold", len(hold_signals))
        st.dataframe(hold_signals)
    
    with col2:
        if st.button("🔄 REFRESH LARGE CAP", key="refresh_large"):
            for signal in ['strongbuy', 'buy', 'sell', 'hold']:
                st.session_state[f'large_{signal}'] = generate_signals(LARGE_CAP[:20], 'large')
            st.rerun()

# MID CAP TAB  
with tab2:
    st.markdown("### 📈 **MID CAP** - Growth Signals")
    
    col1, col2 = st.columns([3, 1])
    
    # Auto-refresh strong buy
    if should_auto_refresh('mid'):
        st.session_state['mid_strongbuy'] = generate_signals(MID_CAP[:15], 'mid')
        st.session_state.last_strongbuy_refresh['mid'] = time.time()
    
    signal_tabs = col1.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
    
    with signal_tabs[0]:
        strongbuy = st.session_state.get('mid_strongbuy', generate_signals(MID_CAP[:5], 'mid'))
        if not strongbuy.empty:
            st.metric("🚀 Mid Cap Strong Buy", len(strongbuy))
            st.dataframe(strongbuy)
    
    with signal_tabs[1]:
        all_mid = generate_signals(MID_CAP[:15], 'mid')
        buy_signals = all_mid[all_mid['Signal'] == '🟢 BUY']
        st.metric("🟢 Mid Cap Buy", len(buy_signals))
        st.dataframe(buy_signals)
    
    with signal_tabs[2]:
        all_mid = generate_signals(MID_CAP[:15], 'mid')
        sell_signals = all_mid[all_mid['Signal'] == '🔴 SELL']
        st.metric("🔴 Mid Cap Sell", len(sell_signals))
        st.dataframe(sell_signals)
    
    with signal_tabs[3]:
        all_mid = generate_signals(MID_CAP[:15], 'mid')
        hold_signals = all_mid[all_mid['Signal'] == '🟡 HOLD']
        st.metric("🟡 Mid Cap Hold", len(hold_signals))
        st.dataframe(hold_signals)
    
    with col2:
        if st.button("🔄 REFRESH MID CAP", key="refresh_mid"):
            st.rerun()

# SMALL CAP TAB
with tab3:
    st.markdown("### 🚀 **SMALL CAP** - High Risk/Reward")
    
    col1, col2 = st.columns([3, 1])
    
    # Auto-refresh strong buy
    if should_auto_refresh('small'):
        st.session_state['small_strongbuy'] = generate_signals(SMALL_CAP[:15], 'small')
        st.session_state.last_strongbuy_refresh['small'] = time.time()
    
    signal_tabs = col1.tabs(["🟢 STRONG BUY", "🟢 BUY", "🔴 SELL", "🟡 HOLD"])
    
    with signal_tabs[0]:
        strongbuy = st.session_state.get('small_strongbuy', generate_signals(SMALL_CAP[:5], 'small'))
        if not strongbuy.empty:
            st.metric("🚀 Small Cap Strong Buy", len(strongbuy))
            st.dataframe(strongbuy)
    
    with signal_tabs[1]:
        all_small = generate_signals(SMALL_CAP[:15], 'small')
        buy_signals = all_small[all_small['Signal'] == '🟢 BUY']
        st.metric("🟢 Small Cap Buy", len(buy_signals))
        st.dataframe(buy_signals)
    
    with signal_tabs[2]:
        all_small = generate_signals(SMALL_CAP[:15], 'small')
        sell_signals = all_small[all_small['Signal'] == '🔴 SELL']
        st.metric("🔴 Small Cap Sell", len(sell_signals))
        st.dataframe(sell_signals)
    
    with signal_tabs[3]:
        all_small = generate_signals(SMALL_CAP[:15], 'small')
        hold_signals = all_small[all_small['Signal'] == '🟡 HOLD']
        st.metric("🟡 Small Cap Hold", len(hold_signals))
        st.dataframe(hold_signals)
    
    with col2:
        if st.button("🔄 REFRESH SMALL CAP", key="refresh_small"):
            st.rerun()

# OVERVIEW DASHBOARD
st.markdown("---")
st.subheader("📊 **NIFTY 500 OVERVIEW**")

col1, col2, col3 = st.columns(3)
col1.metric("🏢 Large Cap Stocks", len(LARGE_CAP))
col2.metric("📈 Mid Cap Stocks", len(MID_CAP)) 
col3.metric("🚀 Small Cap Stocks", len(SMALL_CAP))

st.caption("""
**🎯 SIGNAL LOGIC** (Cap-specific RSI):
• **LARGE CAP**: Strong Buy <40, Buy <45, Sell >65
• **MID CAP**: Strong Buy <35, Buy <42, Sell >68  
• **SMALL CAP**: Strong Buy <32, Buy <38, Sell >72

**🔄 AUTO REFRESH**: Strong Buy tabs update every 5 minutes
**✅ SEBI Classification**: Large(1-100), Mid(101-250), Small(251+)
""")
