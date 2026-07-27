import os, sys, numpy as np, pandas as pd
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)
from config import CONFIG

def detect_regime(df):
    if "ADX" not in df.columns or df["ADX"].dropna().empty:
        from analysis.indicators import compute_adx; df=compute_adx(df)
    adx=df["ADX"].dropna()
    return "trending" if not adx.empty and adx.iloc[-1]>=CONFIG.indicator.regime_adx_threshold else "ranging"

def _latest(df, col):
    if col not in df.columns: return 0.0
    v=df[col].dropna(); return float(v.iloc[-1]) if not v.empty else 0.0

def _ivote(v,bl=-np.inf,bh=np.inf,al=-np.inf,ah=np.inf):
    if np.isnan(v) or v==0: return 0.0
    if bl<=v<=bh: return 1.0
    if al<=v<=ah: return -1.0
    return 0.0

def _avg(vs):
    vs=[v for v in vs if v is not None and not np.isnan(v)]
    return np.mean(vs) if vs else 0.0

def compute_trend_score(df):
    c=df["Close"].dropna()
    if len(c)<2: return 0.0
    cur=c.iloc[-1]; votes=[]
    for p in CONFIG.indicator.sma_periods:
        s=_latest(df,f"SMA_{p}")
        if s>0: votes.append(1.0 if cur>s else -1.0)
    for p in CONFIG.indicator.ema_periods:
        s=_latest(df,f"EMA_{p}")
        if s>0: votes.append(1.0 if cur>s else -1.0)
    a=_latest(df,"ADX"); dp=_latest(df,"DI_plus"); dm=_latest(df,"DI_minus")
    if a>20: votes.append(1.0 if dp>dm else -1.0)
    return _avg(votes)

def compute_momentum_score(df):
    votes=[]
    r=_latest(df,"RSI")
    if r>0: votes.append(_ivote(r,bl=0,bh=30,al=70,ah=100))
    m=_latest(df,"MACD"); ms=_latest(df,"MACD_Signal")
    if m!=0 and ms!=0: votes.append(1.0 if m>ms else -1.0)
    sk=_latest(df,"Stoch_K")
    if sk>0: votes.append(_ivote(sk,bl=0,bh=20,al=80,ah=100))
    wr=_latest(df,"Williams_%R")
    if wr<0: votes.append(_ivote(abs(wr),bl=80,bh=100,al=0,ah=20))
    cci=_latest(df,"CCI")
    if abs(cci)<400: votes.append(_ivote(cci,bl=-np.inf,bh=-100,al=100,ah=np.inf))
    return _avg(votes)

def compute_volume_score(df):
    votes=[]
    if "OBV" in df.columns:
        obv=df["OBV"].dropna(); c=df["Close"].dropna()
        if len(obv)>1 and len(c)>1:
            ot=1.0 if obv.iloc[-1]>obv.iloc[-5] else -1.0
            pt=1.0 if c.iloc[-1]>c.iloc[-5] else -1.0
            votes.append(ot if ot==pt else -0.5*abs(ot))
    mfi=_latest(df,"MFI")
    if mfi>0: votes.append(_ivote(mfi,bl=0,bh=20,al=80,ah=100))
    return _avg(votes)

def compute_volatility_score(df):
    bb=_latest(df,"BB_%B")
    if 0<=bb<=2: return _ivote(bb,bl=0,bh=0.2,al=0.8,ah=1.0)
    return 0.0

def compute_fundamental_score(fd):
    votes=[]
    pe=fd.get("pe_ratio")
    if pe and pe>0:
        if pe<15: votes.append(1.0)
        elif pe>30: votes.append(-1.0)
        else: votes.append(0.0)
    de=fd.get("debt_equity")
    if de and de>0: votes.append(1.0 if de<1.0 else -1.0)
    else: votes.append(0.0)
    return np.mean(votes) if votes else 0.0

def generate_signals(df, fundamentals=None):
    regime=detect_regime(df); sc=CONFIG.signal
    wt=sc.trend_weight_trending if regime=="trending" else sc.trend_weight_ranging
    wm=sc.momentum_weight_trending if regime=="trending" else sc.momentum_weight_ranging
    wv=sc.volume_weight_trending if regime=="trending" else sc.volume_weight_ranging
    wvl=sc.volatility_weight_trending if regime=="trending" else sc.volatility_weight_ranging
    wf=sc.fundamental_weight_trending if regime=="trending" else sc.fundamental_weight_ranging
    ts=compute_trend_score(df); ms=compute_momentum_score(df); vs=compute_volume_score(df); vls=compute_volatility_score(df)
    fs=compute_fundamental_score(fundamentals or {})
    composite=np.clip((wt*ts+wm*ms+wv*vs+wvl*vls+wf*fs)*50+50,0,100)
    if composite>=80: cv="Strong Buy"
    elif composite>=60: cv="Buy"
    elif composite>=40: cv="Neutral"
    elif composite>=20: cv="Sell"
    else: cv="Strong Sell"
    return {"composite_score":round(float(composite),1),"conviction":cv,"regime":regime,
            "breakdown":{"trend":round(float(ts),3),"momentum":round(float(ms),3),"volume":round(float(vs),3),
                         "volatility":round(float(vls),3),"fundamental":round(float(fs),3)}}
