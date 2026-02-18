# Replace the scan function with this ROBUST version:

@st.cache_data(ttl=300)
def scan_nifty50_robust():
    results = []
    failed = []
    
    for symbol in nifty50:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="30d")
            
            if len(data) < 20:  # Need 20+ days for MA20
                failed.append(symbol.replace('.NS',''))
                continue
            
            # RSI + MA20
            data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()
            data['MA20'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
            
            rsi = data['RSI'].iloc[-1]
            ma20 = data['MA20'].iloc[-1]
            price = data['Close'].iloc[-1]
            
            # Dual confirmation signals
            if rsi < 35 and price > ma20:
                signal = "🟢 STRONG BUY"
            elif rsi > 65 and price < ma20:
                signal = "🔴 STRONG SELL"
            elif rsi < 30:
                signal = "🟢 BUY"
            elif rsi > 70:
                signal = "🔴 SELL"
            else:
                signal = "🟡 HOLD"
            
            results.append({
                'Stock': symbol.replace('.NS',''),
                'Price': f"₹{price:.1f}",
                'RSI': f"{rsi:.1f}",
                'MA20': f"₹{ma20:.1f}",
                'Signal': signal
            })
            
        except Exception as e:
            failed.append(symbol.replace('.NS',''))
        
        time.sleep(0.6)  # Extra safe delay
    
    # Add status metrics
    st.success(f"✅ **SUCCESS**: {len(results)}/50 stocks | ❌ **FAILED**: {len(failed)} stocks")
    if failed:
        with st.expander("Failed stocks (click to see)"):
            st.write(failed)
    
    retur
