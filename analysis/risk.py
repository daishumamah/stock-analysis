import os, sys
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)

import numpy as np, pandas as pd
from config import CONFIG

def compute_returns(df): return df["Close"].pct_change().dropna()

def compute_volatility(df, w=21):
    r=compute_returns(df)
    if len(r)<2: return {"daily":0,"weekly":0,"monthly":0,"annualized":0}
    dv=float(r.std(ddof=1))
    return {"daily":round(dv,4),"weekly":round(dv*np.sqrt(5),4),"monthly":round(dv*np.sqrt(21),4),"annualized":round(dv*np.sqrt(252),4)}

def compute_var(df, conf=None):
    conf=conf or CONFIG.risk.var_confidence; r=compute_returns(df)
    if len(r)<20: return {"VaR_95":0,"VaR_99":0}
    return {"VaR_95":round(float(np.percentile(r,(1-conf)*100)),4),"VaR_99":round(float(np.percentile(r,1)),4)}

def compute_max_drawdown(df):
    c=df["Close"]
    if len(c)<2: return {"max_drawdown_pct":0,"max_drawdown_duration_days":0}
    dd=(c-c.cummax())/c.cummax()*100
    return {"max_drawdown_pct":round(float(dd.min()),2),"max_drawdown_duration_days":0}

def compute_sharpe_ratio(df, rf=None):
    rf=rf or CONFIG.risk.risk_free_rate; r=compute_returns(df)
    if len(r)<2 or r.std(ddof=1)==0: return 0.0
    return round(float((r.mean()*252-rf)/(r.std(ddof=1)*np.sqrt(252))),2)

def compute_position_size(pv, rpt, atr, ep):
    if atr<=0 or ep<=0: return {"shares":0,"capital":0}
    sd=2*atr; rc=pv*rpt; mc=pv*CONFIG.risk.kelly_cap
    c=min(rc*(ep/sd),mc); s=int(c/ep)
    return {"shares":s,"capital":round(s*ep,2),"atr_stop":round(ep-sd,2)}

def compute_all_risk_metrics(df):
    return {"volatility":compute_volatility(df),"value_at_risk":compute_var(df),"max_drawdown":compute_max_drawdown(df),"sharpe_ratio":compute_sharpe_ratio(df)}

def compute_beta(df, mdf=None):
    if mdf is None:
        from data.fetcher import get_historical_data; mdf=get_historical_data("SPY",period="1y")
    sr=compute_returns(df); mr=compute_returns(mdf)
    a=pd.concat([sr,mr],axis=1).dropna()
    if len(a)<2: return 1.0
    cv=np.cov(a.iloc[:,0],a.iloc[:,1]); return round(float(cv[0,1]/cv[1,1]),2)
