import os, sys, numpy as np, pandas as pd
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)
from config import CONFIG
cfg = CONFIG.indicator

# === TREND ===
def compute_sma(s, p): return s.rolling(p, min_periods=min(p,len(s))).mean()
def compute_ema(s, p): return s.ewm(span=p, adjust=False).mean()

def compute_all_sma(df):
    for p in cfg.sma_periods:
        if len(df) >= p: df[f"SMA_{p}"] = compute_sma(df["Close"], p)
    return df

def compute_all_ema(df):
    for p in cfg.ema_periods:
        if len(df) >= p: df[f"EMA_{p}"] = compute_ema(df["Close"], p)
    return df

def compute_ichimoku(df):
    if len(df) < 9: return df
    h,l=df["High"],df["Low"]
    ten=(h.rolling(9).max()+l.rolling(9).min())/2
    kij=(h.rolling(26).max()+l.rolling(26).min())/2
    df["Ichimoku_Tenkan"]=ten; df["Ichimoku_Kijun"]=kij
    if len(df) >= 26: df["Ichimoku_SenkouA"]=((ten+kij)/2).shift(26)
    if len(df) >= 52: df["Ichimoku_SenkouB"]=((h.rolling(52).max()+l.rolling(52).min())/2).shift(26)
    df["Ichimoku_Chikou"]=df["Close"].shift(-26)
    return df

def compute_adx(df, p=0):
    p=p or cfg.adx_period
    if len(df) < p+1: df["ADX"]=np.nan; df["DI_plus"]=np.nan; df["DI_minus"]=np.nan; return df
    h,l,c=df["High"],df["Low"],df["Close"]
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    atr=tr.rolling(p).mean()
    up=h-h.shift(); down=l.shift()-l
    dp=np.where((up>down)&(up>0),up,0); dm=np.where((down>up)&(down>0),down,0)
    di_plus=100*pd.Series(dp).rolling(p).mean()/atr
    di_minus=100*pd.Series(dm).rolling(p).mean()/atr
    dx=100*(di_plus-di_minus).abs()/(di_plus+di_minus+1e-10)
    df["ADX"]=dx.rolling(p).mean(); df["DI_plus"]=di_plus; df["DI_minus"]=di_minus
    return df

def compute_psar(df):
    if len(df)<2: df["PSAR"]=np.nan; return df
    h,l=df["High"].values,df["Low"].values; n=len(h)
    sar,ep,af=np.empty(n),np.empty(n),np.empty(n); tr=np.empty(n,dtype=bool)
    tr[0]=True; sar[0]=l[0]; ep[0]=h[0]; af[0]=0.02
    for i in range(1,n):
        if tr[i-1]: sar[i]=sar[i-1]+af[i-1]*(ep[i-1]-sar[i-1])
        else: sar[i]=sar[i-1]-af[i-1]*(sar[i-1]-ep[i-1])
        if tr[i-1]:
            if l[i]<sar[i]: tr[i]=False; sar[i]=ep[i-1]; ep[i]=l[i]; af[i]=0.02
            else:
                tr[i]=True
                if h[i]>ep[i-1]: ep[i]=h[i]; af[i]=min(af[i-1]+0.02,0.20)
                else: ep[i]=ep[i-1]; af[i]=af[i-1]
                if sar[i]>l[i]: sar[i]=l[i]
        else:
            if h[i]>sar[i]: tr[i]=True; sar[i]=ep[i-1]; ep[i]=h[i]; af[i]=0.02
            else:
                tr[i]=False
                if l[i]<ep[i-1]: ep[i]=l[i]; af[i]=min(af[i-1]+0.02,0.20)
                else: ep[i]=ep[i-1]; af[i]=af[i-1]
                if sar[i]<h[i]: sar[i]=h[i]
    df["PSAR"]=sar; return df

# === MOMENTUM ===
def compute_rsi(s, p=0):
    p=p or cfg.rsi_period
    if len(s)<p+1: return pd.Series(np.nan,index=s.index)
    d=s.diff(); g=d.clip(lower=0); l=-d.clip(upper=0)
    return 100-100/(1+g.ewm(span=p,adjust=False).mean()/(l.ewm(span=p,adjust=False).mean()+1e-10))

def compute_macd(df):
    c=df["Close"]
    if len(df)<cfg.macd_slow+1: df["MACD"]=np.nan; df["MACD_Signal"]=np.nan; df["MACD_Hist"]=np.nan; return df
    f=c.ewm(span=cfg.macd_fast,adjust=False).mean()
    sl=c.ewm(span=cfg.macd_slow,adjust=False).mean()
    ml=f-sl; df["MACD"]=ml; df["MACD_Signal"]=ml.ewm(span=cfg.macd_signal,adjust=False).mean()
    df["MACD_Hist"]=df["MACD"]-df["MACD_Signal"]; return df

def compute_stochastic(df):
    kp,dp=cfg.stochastic_k,cfg.stochastic_d
    if len(df)<kp: df["Stoch_K"]=np.nan; df["Stoch_D"]=np.nan; return df
    lk=df["Low"].rolling(kp).min(); hk=df["High"].rolling(kp).max()
    k=100*(df["Close"]-lk)/(hk-lk+1e-10)
    df["Stoch_K"]=k; df["Stoch_D"]=k.rolling(dp).mean(); return df

def compute_williams_r(df):
    p=cfg.williams_r_period
    if len(df)<p: return pd.Series(np.nan,index=df.index)
    return -100*(df["High"].rolling(p).max()-df["Close"])/(df["High"].rolling(p).max()-df["Low"].rolling(p).min()+1e-10)

def compute_cci(df, p=0):
    p=p or cfg.cci_period
    if len(df)<p: return pd.Series(np.nan,index=df.index)
    tp=(df["High"]+df["Low"]+df["Close"])/3
    sma=tp.rolling(p).mean()
    mad=tp.rolling(p).apply(lambda x:np.abs(x-x.mean()).mean(),raw=True)
    return (tp-sma)/(0.015*mad+1e-10)

def compute_roc(s, p=0):
    p=p or cfg.roc_period
    if len(s)<p+1: return pd.Series(np.nan,index=s.index)
    return s.pct_change(p)*100

# === VOLATILITY ===
def compute_bollinger(df):
    p,s=cfg.bollinger_period,cfg.bollinger_std
    if len(df)<p: df["BB_Mid"]=np.nan; df["BB_Upper"]=np.nan; df["BB_Lower"]=np.nan; df["BB_%B"]=np.nan; df["BB_Width"]=np.nan; return df
    m=df["Close"].rolling(p).mean(); std=df["Close"].rolling(p).std(ddof=0)
    df["BB_Mid"]=m; df["BB_Upper"]=m+s*std; df["BB_Lower"]=m-s*std
    df["BB_%B"]=(df["Close"]-df["BB_Lower"])/(df["BB_Upper"]-df["BB_Lower"]+1e-10)
    df["BB_Width"]=(df["BB_Upper"]-df["BB_Lower"])/m*100; return df

def compute_keltner(df):
    p,m=cfg.keltner_period,cfg.keltner_atr_mult
    if len(df)<p: df["KC_Upper"]=np.nan; df["KC_Mid"]=np.nan; df["KC_Lower"]=np.nan; return df
    ema=df["Close"].ewm(span=p,adjust=False).mean()
    tr=pd.concat([df["High"]-df["Low"],(df["High"]-df["Close"].shift()).abs(),(df["Low"]-df["Close"].shift()).abs()],axis=1).max(axis=1)
    atr=tr.ewm(span=p,adjust=False).mean()
    df["KC_Upper"]=ema+m*atr; df["KC_Mid"]=ema; df["KC_Lower"]=ema-m*atr; return df

def compute_atr(df, p=0):
    p=p or cfg.atr_period
    if len(df)<p+1: return pd.Series(np.nan,index=df.index)
    tr=pd.concat([df["High"]-df["Low"],(df["High"]-df["Close"].shift()).abs(),(df["Low"]-df["Close"].shift()).abs()],axis=1).max(axis=1)
    return tr.rolling(p).mean()

def compute_donchian(df):
    p=cfg.donchian_period
    if len(df)<p: df["DC_Upper"]=np.nan; df["DC_Lower"]=np.nan; df["DC_Mid"]=np.nan; return df
    df["DC_Upper"]=df["High"].rolling(p).max(); df["DC_Lower"]=df["Low"].rolling(p).min()
    df["DC_Mid"]=(df["DC_Upper"]+df["DC_Lower"])/2; return df

# === VOLUME ===
def compute_obv(df):
    if len(df)<2: return pd.Series(np.nan,index=df.index)
    return (df["Volume"]*np.sign(df["Close"].diff())).fillna(0).cumsum()

def compute_mfi(df, p=0):
    p=p or cfg.mfi_period
    if len(df)<p+1: return pd.Series(np.nan,index=df.index)
    tp=(df["High"]+df["Low"]+df["Close"])/3; mf=tp*df["Volume"]
    pos=mf.where(tp>tp.shift(),0); neg=mf.where(tp<tp.shift(),0)
    return 100-100/(1+pos.rolling(p).sum()/(neg.rolling(p).sum()+1e-10))

def compute_vwap(df):
    if len(df)<1: return pd.Series(np.nan,index=df.index)
    cum=(df["Volume"]*(df["High"]+df["Low"]+df["Close"])/3).cumsum()
    return cum/(df["Volume"].cumsum()+1e-10)

def compute_chaikin_mf(df):
    p=cfg.chaikin_mf_period
    if len(df)<p+1: return pd.Series(np.nan,index=df.index)
    mf=((df["Close"]-df["Low"])-(df["High"]-df["Close"]))/(df["High"]-df["Low"]+1e-10)
    return (mf*df["Volume"]).rolling(p).sum()/df["Volume"].rolling(p).sum()

# === COMPUTE ALL ===
def compute_all_indicators(df):
    if df.empty or len(df)<5: return df
    df=df.copy()
    compute_all_sma(df); compute_all_ema(df); compute_ichimoku(df); compute_adx(df); compute_psar(df)
    df["RSI"]=compute_rsi(df["Close"]); compute_macd(df); compute_stochastic(df)
    df["Williams_%R"]=compute_williams_r(df); df["CCI"]=compute_cci(df); df["ROC"]=compute_roc(df["Close"])
    compute_bollinger(df); compute_keltner(df); df["ATR"]=compute_atr(df); compute_donchian(df)
    df["OBV"]=compute_obv(df); df["MFI"]=compute_mfi(df); df["VWAP"]=compute_vwap(df); df["Chaikin_MF"]=compute_chaikin_mf(df)
    return df
