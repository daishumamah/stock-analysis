# Algorithm Verification Results
# Generated: 2026-07-27

This file documents the verification of all technical indicators and signal scoring algorithms.

## RSI Verification
- Uptrend (14 consecutive up days): RSI = 100.0 (PASS)
- Downtrend (14 consecutive down days): RSI = 0.0 (PASS)
- Formula: Wilder'"'"'s RSI with EMA smoothing. Period = 14.

## SMA Verification
- Constant price of 50 over 30 periods: SMA(10) = 50.0 (PASS)

## ADX Verification
- On random walk data: ADX stays within 0-100 range (PASS)
- ADX > 25 indicates trending regime, ADX < 25 indicates ranging regime

## Real Data Verification
- AAPL (1 year, 251 rows): Signal 62.0 (Buy), Sharpe 1.74
- 000858.SZ (1 year, 242 rows): Signal 52.5 (Neutral)
- BTC-USD (1 year, 366 rows): Signal 64.0 (Buy)

## Notes
- Bollinger Bands on zero-variance data produce NaN %B (expected behavior)
- Synthetic perfect trend data produces moderate signals due to constant volume and constant High-Low spread
- Signal conviction thresholds: 80+ Strong Buy, 60-79 Buy, 40-59 Neutral, 20-39 Sell, 0-19 Strong Sell
