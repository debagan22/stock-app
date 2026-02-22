# Add this to your existing get_nifty_data() function AFTER signal calculation:

# 🎯 BUY/SELL PRICE TARGETS
atr = ta.volatility.AverageTrueRange(hist['High'], hist['Low'], hist['Close'], 14).average_true_range().iloc[-1]

if 'SUPER BUY' in signal or 'STRONG BUY' in signal:
    # BUY ENTRY: 1-2% below current or MA20 support
    buy_entry = min(price * 0.98, ma20 * 1.01)  # 2% discount or MA20 bounce
    # SELL TARGETS: 5% up + ATR extension
    sell_target1 = price * 1.05
    sell_target2 = price + (atr * 1.5)
    risk_reward = (sell_target1 - buy_entry) / (price - ma20 * 0.98) if ma20 * 0.98 < price else 2.0
    
elif 'BUY' in signal:
    buy_entry = price * 0.99  # 1% dip
    sell_target1 = price * 1.03
    sell_target2 = price + atr
    risk_reward = 1.5

elif 'SELL' in signal:
    sell_entry = max(price * 1.02, ma20 * 0.99)  # 2% above or MA20 resistance
    buy_target1 = price * 0.95
    buy_target2 = price - (atr * 1.5)
    risk_reward = 2.0

else:  # HOLD
    buy_entry = sell_entry = buy_target1 = sell_target1 = np.nan
    risk_reward = 1.0

# ADD TO RETURN DICTIONARY:
return {
    # ... existing fields ...
    'Buy_Entry': f"₹{buy_entry:.0f}" if 'BUY' in signal else "-",
    'Sell_Target1': f"₹{sell_target1:.0f}" if 'BUY' in signal else "-",
    'Sell_Target2': f"₹{sell_target2:.0f}" if 'BUY' in signal else "-",
    'Risk_Reward': f"{risk_reward:.1f}:1",
    'Sell_Entry': f"₹{sell_entry:.0f}" if 'SELL' in signal else "-",
    'Buy_Target1': f"₹{buy_target1:.0f}" if 'SELL' in signal else "-",
    'ATR': f"₹{atr:.0f}"
}
