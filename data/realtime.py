import os, sys, json, time, urllib.request, urllib.error
from typing import Optional

PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)
from config import CONFIG

# Alpha Vantage key: check env var -> file -> Streamlit secrets
ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_KEY", "")
if not ALPHA_VANTAGE_KEY:
    key_file = os.path.join(PROJ, "data", ".alpha_key")
    if os.path.exists(key_file):
        with open(key_file) as f:
            ALPHA_VANTAGE_KEY = f.read().strip()
if not ALPHA_VANTAGE_KEY:
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "ALPHA_VANTAGE_KEY" in st.secrets:
            ALPHA_VANTAGE_KEY = st.secrets["ALPHA_VANTAGE_KEY"]
    except:
        pass

_price_cache = {}

def _is_crypto(t):
    return t.upper().endswith("-USD") or t.upper().endswith("-USDT")

def _is_chinese(t):
    return t.upper().endswith(".SS") or t.upper().endswith(".SZ")

def _chinese_sina_symbol(ticker):
    t = ticker.upper().replace(".SS", "").replace(".SZ", "")
    prefix = "sh" if ticker.upper().endswith(".SS") else "sz"
    return prefix + t

def get_chinese_price(ticker):
    symbol = _chinese_sina_symbol(ticker)
    url = "https://hq.sinajs.cn/list=" + symbol
    try:
        req = urllib.request.Request(url, headers={"Referer": "https://finance.sina.com.cn"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            text = raw.decode("gbk")
        for line in text.strip().split(";"):
            if line and "=" in line:
                vals = line.split("=")[1].strip("\u201c").split(",")
                if len(vals) >= 4 and vals[3]:
                    return float(vals[3])
    except:
        pass
    return None

def _binance_symbol(ticker):
    base = ticker.upper().replace("-USD", "").replace("-USDT", "")
    return base + "USDT"

def get_crypto_price(ticker):
    symbol = _binance_symbol(ticker)
    url = "https://api.binance.com/api/v3/ticker/price?symbol=" + symbol
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return float(data["price"])
    except:
        return None

def get_stock_price_alphavantage(ticker):
    if not ALPHA_VANTAGE_KEY:
        return None
    url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + ticker + "&apikey=" + ALPHA_VANTAGE_KEY
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if "Global Quote" in data and "05. price" in data["Global Quote"]:
                return float(data["Global Quote"]["05. price"])
    except:
        pass
    return None

def get_stock_price_yfinance(ticker):
    try:
        import yfinance as yf
        t = yf.Ticker(ticker)
        hist = t.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist["Close"].iloc[-1])
    except:
        pass
    return None

def get_realtime_price(ticker, force_refresh=False):
    now = time.time()
    ticker = ticker.upper()
    if not force_refresh and ticker in _price_cache:
        cp, ct = _price_cache[ticker]
        if now - ct < 30:
            return cp
    result = {"price": None, "source": "", "timestamp": now, "change_pct": None}
    if _is_crypto(ticker):
        price = get_crypto_price(ticker)
        if price:
            result["price"] = price
            result["source"] = "Binance (crypto)"
    if result["price"] is None and _is_chinese(ticker):
        price = get_chinese_price(ticker)
        if price:
            result["price"] = price
            result["source"] = "China"
    if result["price"] is None:
        price = get_stock_price_alphavantage(ticker)
        if price:
            result["price"] = price
            result["source"] = "Alpha Vantage"
    if result["price"] is None:
        price = get_stock_price_yfinance(ticker)
        if price:
            result["price"] = price
            result["source"] = "yfinance (delayed)"
    if result["price"]:
        try:
            from data.fetcher import get_historical_data
            df = get_historical_data(ticker, period="5d")
            if not df.empty and len(df) >= 2:
                pc = float(df["Close"].iloc[-2])
                if pc > 0:
                    result["change_pct"] = round((result["price"] - pc) / pc * 100, 2)
        except:
            pass
        _price_cache[ticker] = (result, now)
    return result

def validate_alpha_key(key):
    if not key: return False
    try:
        url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=" + key
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return "Time Series (1min)" in data
    except:
        return False
