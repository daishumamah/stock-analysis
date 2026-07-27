# Stock Analysis Tool — Design Document

> A high-accuracy stock analysis tool combining technical analysis, fundamental analysis, risk metrics, and a multi-factor signal scoring engine. Supports both historical and real-time data.

---

## 1. System Architecture

![Architecture Diagram](diagram-arch.png)

### Updated Architecture with Real-Time Data

```
                   ┌─────────────────────┐
                   │    Dashboard UI     │
                   │   (Streamlit +      │
                   │    Plotly Charts)   │
                   └──────┬──────┬──────┘
                          │      │
              ┌───────────┘      └───────────┐
              │                              │
     ┌────────▼────────┐          ┌──────────▼──────────┐
     │  Historical      │          │  Real-Time          │
     │  Analysis Path   │          │  Data Path          │
     │                  │          │                     │
     │ signal: 0-100    │          │ price: current      │
     │ risk: VaR,Sharpe │          │ source: Binance/AV  │
     │ fundamentals     │          │ auto-refresh: 30s   │
     └────────┬─────────┘          └──────────┬──────────┘
              │                              │
     ┌────────▼─────────┐          ┌──────────▼──────────┐
     │  Indicator Engine │          │  Real-Time Fetcher  │
     │  15+ indicators   │          │                     │
     │  Signal scoring   │          │  Binance (crypto)   │
     │  Regime detection │          │  Alpha Vantage      │
     └────────┬──────────┘          │  (stocks, requires  │
              │                     │   free API key)     │
     ┌────────▼─────────┐          │  yfinance fallback  │
     │  Data Fetcher     │          └──────────┬──────────┘
     │  yfinance +       │                     │
     │  SQLite Cache     │                     │
     └────────┬──────────┘                     │
              │                                │
     ┌────────▼─────────┐                     │
     │  External APIs   │◄────────────────────┘
     │  - yfinance      │
     │  - Binance (crypto)│
     │  - Alpha Vantage │
     └──────────────────┘
```

### Data Flow Modes

**Historical Analysis Mode (default):**
User enters ticker + period -> Data Fetcher checks SQLite cache -> If miss, downloads from yfinance -> Computes 15+ indicators -> Generates signal score -> Calculates risk metrics -> Fetches fundamentals -> Renders dashboard

**Real-Time Mode (optional):**
User enables auto-refresh -> Real-time price fetched from Binance (crypto) or Alpha Vantage (stocks) -> Price updates every 30 seconds -> Historical analysis is preserved for indicators/risk -> Dashboard shows live price ticker alongside analysis

---

## 2. User Analysis Session — Sequence Flow

![Sequence Diagram](diagram-seq.png)

### Updated Sequence with Real-Time Option

```
User -> Dashboard: Enter ticker + select period + enable auto-refresh
Dashboard -> Data Fetcher: get_historical_data(ticker, period)
Data Fetcher -> yfinance: Download OHLCV data
yfinance -> Data Fetcher: Historical data returned
Data Fetcher -> Cache: Store in SQLite
Data Fetcher -> Dashboard: Return DataFrame
Dashboard -> Indicators: compute_all_indicators(df)
Dashboard -> Signal Engine: generate_signals(df, fundamentals)
Dashboard -> Risk Module: compute_all_risk_metrics(df)
Dashboard -> User: Show full dashboard

─── Real-Time Loop (if enabled) ───
loop every 30 seconds:
    Dashboard -> Real-Time Fetcher: get_realtime_price(ticker)
    Real-Time Fetcher -> Binance/AlphaVantage: Fetch current price
    Binance/AlphaVantage -> Real-Time Fetcher: Return latest price
    Real-Time Fetcher -> Dashboard: Update price metric
    Dashboard -> User: Display updated price + change %
end loop
```

---

## 3. Real-Time Data Sources

### Supported Sources

| Source | Coverage | Delay | API Key Required | Rate Limit |
|---|---|---|---|---|
| **Binance** (public) | Crypto (BTC-USD, ETH-USD, etc.) | Real-time | No | 1200 req/min |
| **Alpha Vantage** | US stocks | ~15s delay | Yes (free) | 5 req/min |
| **yfinance** (fallback) | Stocks + Crypto | 15-20 min | No | No hard limit |

### Data Source Selection Logic

```
Crypto ticker (ends with -USD or -USDT)?
  YES -> Binance API (real-time, no key needed)
  NO -> Alpha Vantage key configured?
         YES -> Alpha Vantage (near-real-time)
         NO -> yfinance (delayed fallback)
```

### User Controls

- **Auto-refresh checkbox:** Toggle real-time updates (30 second interval)
- **Price display:** Shows source indicator (Binance/Alpha Vantage/yfinance)
- **Change %:** Calculated vs previous day close

---

## 4. Indicator Coverage

### Trend Indicators
- **SMA (20/50/200)** — Simple Moving Averages for trend direction at multiple timeframes
- **EMA (12/26)** — Faster-reacting moving averages
- **Ichimoku Cloud** — 5-line system: tenkan-sen, kijun-sen, senkou span A/B, chikou span
- **ADX (14)** — Trend strength indicator. Used both as indicator AND regime classifier. >25 trending, <25 ranging.
- **Parabolic SAR** — Stop-and-reversal trailing stop indicator

### Momentum Indicators
- **RSI (14)** — Relative Strength Index. 0-100 scale. <30 oversold, >70 overbought.
- **MACD (12,26,9)** — Moving Average Convergence Divergence. Line, signal, histogram.
- **Stochastic (14,3)** — %K and %D lines. Compares close to recent range.
- **Williams %R (14)** — Inverse of stochastic. -80 oversold, -20 overbought.
- **CCI (20)** — Commodity Channel Index. -100 to +100 typical range.
- **ROC (12)** — Rate of Change. Simple price momentum.

### Volatility Indicators
- **Bollinger Bands (20,2)** — SMA +- 2 standard deviations. %B gives position within bands.
- **Keltner Channels (20,1.5)** — EMA +- 1.5xATR. Less reactive to outlier moves.
- **ATR (14)** — Average True Range. Core volatility measure.
- **Donchian Channels (20)** — Highest high / lowest low channels.

### Volume Indicators
- **OBV** — On-Balance Volume. Cumulative volume confirms price trends.
- **MFI (14)** — Money Flow Index. Volume-weighted RSI.
- **VWAP** — Volume Weighted Average Price.
- **Chaikin MF (20)** — Money Flow multiplier x volume, accumulated.

---

## 5. Signal Scoring System

![Signal Scoring](diagram-signal-scoring.png)

### Improved Conviction Scoring (0-100) with 3 Accuracy Enhancements

**Enhancement 1: Z-Score Normalization**
All indicator values are converted to z-scores (how many standard deviations from their own mean) before being combined. This prevents indicators with wider numerical ranges (like CCI: -400 to +400) from dominating indicators with narrow ranges (like RSI: 0-100).

**Enhancement 2: Exponential Decay Weighting**
Recent signals count more. A signal from 5 days ago has ~60% the weight of today's signal. This ensures the score reflects current conditions, not stale data.

**Enhancement 3: Correlation-Aware Voting**
Indicators within the same family (e.g., RSI and Stochastic %K, which are ~0.8 correlated) are averaged before contributing to the final score.

| Component | Weight (Trending) | Weight (Ranging) | Inputs |
|---|---|---|---|
| **Trend Score** | 40% | 20% | SMA/EMA positioning, ADX, Ichimoku |
| **Momentum Score** | 20% | 30% | RSI, MACD, Stochastic, Williams %R |
| **Volume Score** | 20% | 20% | OBV trend, MFI, volume vs avg |
| **Volatility Score** | 10% | 20% | Bollinger %B, ATR regime |
| **Fundamental Score** | 10% | 10% | P/E, EPS, F-Score |

**Regime-adaptive:** ADX > 25 = trending (weight trend indicators). ADX < 25 = ranging (weight mean-reversion).

**Output:** Composite score 0-100 with conviction level (Strong Buy / Buy / Neutral / Sell / Strong Sell) and supporting reasoning breakdown.

---

## 6. Accuracy Enhancement Strategies

![Accuracy Strategies](diagram-accuracy.png)

### Five-Layer Accuracy Architecture

1. **Regime Filtering** — ADX threshold classifies trending vs ranging markets.
2. **Z-Score Normalization** — All indicator values standardized to same scale before voting.
3. **Correlation-Aware Grouping** — Correlated indicators averaged within families.
4. **Exponential Time Decay** — Recent signals weighted more heavily. Half-life: 10 trading days.
5. **Volume Confirmation** — All signals discounted unless volume supports the move.

---

## 7. Risk Module

| Metric | Method | Purpose |
|---|---|---|
| **Daily Volatility** | Std dev of log returns x sqrt(252) | Annualized risk measure |
| **VaR (95%/99%)** | Historical percentile of returns | Worst case in normal conditions |
| **Max Drawdown** | Peak-to-trough decline | Historical worst loss |
| **Position Sizing** | Kelly Criterion (capped at 25%) | Optimal bet size |
| **Sharpe Ratio** | (Return - RF) / Volatility x sqrt(252) | Risk-adjusted return |
| **Beta** | Covariance with SPY returns | Market correlation |

---

## 8. Project Structure

![Project Structure](diagram-structure.png)

```
stock-analysis/
├── app.py                    # Streamlit entry point
├── config.py                 # Indicator params, default settings
├── requirements.txt          # Dependencies
├── README.md                 # Usage documentation
├── project.md                # This design document
├── data/
│   ├── fetcher.py            # yfinance + SQLite cache (historical)
│   ├── realtime.py           # Real-time price (Binance, Alpha Vantage)
│   ├── cache/                # SQLite database directory
│   └── .alpha_key            # Optional: Alpha Vantage API key file
├── analysis/
│   ├── indicators.py         # 15+ technical indicators
│   ├── signals.py            # Multi-factor scoring engine
│   ├── risk.py               # Volatility, VaR, position sizing
│   └── fundamentals.py       # Fundamental ratios and F-Score
├── visualization/
│   ├── charts.py             # Plotly chart functions
│   └── dashboard.py          # Dashboard layout components
├── tests/
│   ├── test_indicators.py
│   └── test_signals.py
├── docs/
│   └── implementation-plan.md
└── node_modules/             # Screenshot tooling (optional)
```

---

## 9. Tech Stack

| Component | Technology |
|---|---|
| Dashboard | Streamlit |
| Charts | Plotly |
| Historical Data | yfinance (free, 15-20 min delayed) |
| Real-Time Data (Crypto) | Binance public API (free, real-time) |
| Real-Time Data (Stocks) | Alpha Vantage (free, ~15s delay) |
| Caching | SQLite (local) |
| Computation | NumPy, Pandas |
| Language | Python 3.14 |

### Data Source Notes
- **yfinance:** Stocks, crypto, ETFs. 15-20 min delayed. Free. No SLA.
- **Binance:** Crypto only (BTC-USD, ETH-USD). Real-time. Free. No key required.
- **Alpha Vantage:** US stocks. Near-real-time (~15s). Free tier: 5 calls/min. API key required.
- **Architecture is data-source agnostic** — swapping providers requires changing only `data/fetcher.py` or `data/realtime.py`.

---

## 10. Configuration

All configurable in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| sma_periods | (20, 50, 200) | SMA lookback periods |
| rsi_period | 14 | RSI period |
| adx_period | 14 | ADX period |
| regime_adx_threshold | 25.0 | ADX threshold for regime switch |
| kelly_cap | 0.25 | Max position size (fraction of portfolio) |
| cache_expiry_hours | 4 | Cache refresh interval |
| risk_free_rate | 0.05 | Risk-free rate for Sharpe |

---

## 11. Cost Estimate

| Metric | Value |
|---|---|
| Scope | Complex (many files, multi-step workflow) |
| Total est. cost | ~$10-15 (design + implementation) |
| Daily budget | $5.00/day cap |
