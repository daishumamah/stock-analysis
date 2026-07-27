import os, sys, numpy as np, pandas as pd
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)
from data.fetcher import get_info

PIOTROSKI={"positive_net_income":("netIncome",lambda v:v>0),"positive_operating_cf":("operatingCashFlow",lambda v:v>0),"roa_increasing":("returnOnAssets",lambda v:v>0)}

def get_fundamentals(ticker):
    info=get_info(ticker)
    if not info or not info.get("pe_ratio"):
        return {"pe_ratio":None,"forward_pe":None,"eps":None,"pb_ratio":None,"debt_equity":None,"dividend_yield":None,"market_cap":None,"sector":"N/A","industry":"N/A","fscore":0}
    fscore=0
    t=__import__("yfinance").Ticker(ticker)
    try:
        fs=t.financials
        if fs is not None and not fs.empty:
            for key,(field,test) in PIOTROSKI.items():
                if field in fs.index:
                    val=fs.loc[field].iloc[0]
                    if not pd.isna(val) and (not hasattr(np,"isnan") or not np.isnan(val)):
                        if test(val): fscore+=1
    except: pass
    info["fscore"]=fscore
    return info
