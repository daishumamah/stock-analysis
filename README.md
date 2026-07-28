# Stock Analysis Tool

A stock and crypto analysis tool with 15+ technical indicators, regime-aware signal scoring, risk metrics, fundamentals, and real-time data. Bilingual (Chinese/English). Available as a mobile app via PWA.

---

## Quick Start (Local)

```bash
cd stock-analysis
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501**

---

## Live Deployment

The app is deployed on **Streamlit Community Cloud**:

**https://stock-analysis-fahfsh6d7rwaivwhr7qyaf.streamlit.app**

Any push to `main` auto-deploys (takes ~1-2 min).

---

## Mobile App (iOS & Android)

Install as a **Progressive Web App (PWA)** on your phone:

### Via GitHub Pages (recommended)
1. Open **https://daishumamah.github.io/stock-analysis/** on your phone
2. **iOS**: Share ? Add to Home Screen
3. **Android**: Menu ? Add to Home Screen

### Via Local Network (development)
```bash
# Terminal 1: Start the main app
streamlit run app.py

# Terminal 2: Start the PWA server
python -m http.server 8080 --directory pwa
```
Open `http://YOUR_IP:8080` on your phone (same WiFi).

---

## Data Sources & Real-Time Coverage

| Market | Source | Live? |
|---|---|---|
| **A-Shares** (.SS/.SZ) | Sina Finance | Yes |
| **Crypto** (BTC-USD) | Binance | Yes |
| **US Stocks** | Alpha Vantage | Yes |
| **Hong Kong** (.HK) | yfinance | Delayed |

### Language
Select **?? / English** from the dropdown in the app header.

---

## Features

- 15+ technical indicators (SMA, EMA, RSI, MACD, Bollinger, ADX, Ichimoku, OBV, MFI, VWAP)
- Regime-aware signal scoring (0-100) with conviction levels (Strong Buy to Strong Sell)
- Risk metrics (VaR, Sharpe, drawdown, volatility)
- Fundamental analysis (P/E, EPS, F-Score)
- Historical Analysis & Real-Time View modes
- Auto-refresh for live monitoring
- Interactive Plotly charts

---

## Project Structure

```
stock-analysis/
+-- app.py                 # Main app (bilingual EN/CN)
+-- config.py              # Configuration
+-- data/
¦   +-- fetcher.py         # Historical data (yfinance + SQLite)
¦   +-- realtime.py        # Real-time data (multiple sources)
¦   +-- .alpha_key         # Alpha Vantage API key
+-- analysis/
¦   +-- indicators.py      # 15+ technical indicators
¦   +-- signals.py         # Multi-factor signal engine
¦   +-- risk.py            # Risk metrics
¦   +-- fundamentals.py    # Fundamental analysis
+-- visualization/
¦   +-- charts.py          # Plotly charts
¦   +-- dashboard.py       # Dashboard layout
+-- pwa/                   # Mobile app files
¦   +-- index.html         # PWA wrapper
¦   +-- manifest.json      # App manifest
¦   +-- sw.js              # Service worker
¦   +-- icons/             # App icons
+-- tests/                 # Verification tests
+-- data/cache/            # Auto-created SQLite cache
```

---

## Verification

```bash
cd stock-analysis
python tests/test_verify_algo.py
```

---

## Disclaimer

Educational purposes only. Not financial advice. Use at your own risk.
