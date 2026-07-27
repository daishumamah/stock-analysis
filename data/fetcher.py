import os, sys
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)

import sqlite3, hashlib, pickle as pkl
import pandas as pd
import yfinance as yf
from datetime import datetime
from config import CONFIG

def _cache_key(ticker, period, interval):
    raw = f"{ticker.upper()}:{period}:{interval}"
    return hashlib.sha256(raw.encode()).hexdigest()

def _get_cache_conn():
    os.makedirs(CONFIG.cache_dir, exist_ok=True)
    db = os.path.join(CONFIG.cache_dir, "cache.db")
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE IF NOT EXISTS c (k TEXT PRIMARY KEY, d BLOB, t TEXT)")
    conn.commit()
    return conn

def get_historical_data(ticker, period="", interval=""):
    period = period or CONFIG.default_period
    interval = interval or CONFIG.default_interval
    key = _cache_key(ticker, period, interval)
    conn = _get_cache_conn()
    row = conn.execute("SELECT d, t FROM c WHERE k = ?", (key,)).fetchone()
    if row:
        try:
            ft = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - ft).total_seconds() < CONFIG.cache_expiry_hours * 3600:
                df = pd.read_pickle(row[0])
                conn.close(); return df
        except: pass
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval)
    if df.empty:
        conn.close(); return pd.DataFrame()
    cm = {}
    for c in df.columns:
        lc = c.lower()
        if lc in ("open","high","low","close","volume"): cm[c] = lc.capitalize()
    df = df.rename(columns=cm)
    for c in ("Open","High","Low","Close","Volume"):
        if c not in df.columns: df[c] = 0.0
    df = df[["Open","High","Low","Close","Volume"]]
    blob = pkl.dumps(df)
    conn.execute("INSERT OR REPLACE INTO c (k, d, t) VALUES (?, ?, ?)",
                 (key, sqlite3.Binary(blob), datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit(); conn.close()
    df.attrs["ticker"] = ticker
    return df

def get_info(ticker):
    try:
        t = yf.Ticker(ticker); i = t.info
        return {"pe_ratio": i.get("trailingPE"), "forward_pe": i.get("forwardPE"),
                "eps": i.get("trailingEps"), "pb_ratio": i.get("priceToBook"),
                "debt_equity": i.get("debtToEquity"), "dividend_yield": i.get("dividendYield"),
                "market_cap": i.get("marketCap"), "sector": i.get("sector"),
                "industry": i.get("industry"), "beta": i.get("beta")}
    except: return {}

def validate_ticker(ticker):
    try:
        t = yf.Ticker(ticker)
        return not t.history(period="5d").empty
    except: return False
