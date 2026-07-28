import os, sys, time
PROJ = os.path.dirname(os.path.abspath(__file__))
if PROJ not in sys.path: sys.path.insert(0, PROJ)

import streamlit as st
from pwa_pack import PWA_SCRIPT
st.set_page_config(page_title="股票分析工具 _ Stock Analysis Tool", layout="wide")

st.markdown(PWA_SCRIPT, unsafe_allow_html=True)

from data.fetcher import get_historical_data, validate_ticker
from data.realtime import get_realtime_price
from analysis.indicators import compute_all_indicators
from analysis.signals import generate_signals
from analysis.risk import compute_all_risk_metrics
from analysis.fundamentals import get_fundamentals

# ---- Language State ----
if "lang" not in st.session_state:
    st.session_state.lang = "中文"

col1, col2 = st.columns([3, 1])
with col1:
    st.title("股票分析工具 _ Stock Analysis Tool")
with col2:
    lang = st.selectbox("语言 _ Language", ["中文", "English"], key="lang")

is_cn = st.session_state.lang == "中文"

# ---- Translations ----
T = {}
if is_cn:
    T = {
        "title": "股票分析工具",
        "ticker": "股票代码",
        "period": "周期",
        "data_mode": "数据模式",
        "historical": "历史分析",
        "realtime": "实时行情",
        "auto_refresh": "自动刷新（30秒）",
        "analyze": "分析",
        "invalid_ticker": "无效的股票代码",
        "no_data": "暂无数据",
        "price_src": "数据来源",
        "price": "价格",
        "signal": "信号",
        "conviction_Strong Buy": "强力买入",
        "conviction_Buy": "买入",
        "conviction_Neutral": "中性",
        "conviction_Sell": "卖出",
        "conviction_Strong Sell": "强力卖出",
        "volatility": "波动率",
        "max_dd": "最大回撤",
        "tab_tech": "技术分析",
        "tab_fund": "基本面",
        "tab_risk": "风险分析",
        "breakdown": "信号分解",
        "trend": "趋势",
        "momentum": "动量",
        "volume": "成交量",
        "volatility_score": "波动",
        "fundamental": "基本面",
        "no_fund": "暂无基本面数据",
        "sharpe": "夏普比率",
        "risk_metrics": "风险指标",
        "features": "功能特色",
        "f1": "15+ 技术指标（SMA, EMA, RSI, MACD, 布林带, ADX, Ichimoku, OBV, MFI, VWAP等）",
        "f2": "市场状态自适应信号评分（0-100分）含置信度等级",
        "f3": "风险指标（VaR, 夏普比率, 回撤, 波动率）",
        "f4": "基本面分析（市盈率, 每股收益, F-Score）",
        "f5": "实时行情：加密货币通过币安API",
        "f6": "实时行情：美股通过Alpha Vantage（已配置密钥）",
        "f7": "实时行情：中国A股实时数据",
        "f8": "历史分析：多年详细技术分析",
        "f9": "交互式Plotly图表含指标叠加",
        "f10": "自动刷新模式用于实时监控",
        "enter_ticker": "输入股票代码并点击分析",
        "live": "（实时）",
        "trending": "趋势",
        "ranging": "震荡",
    }
else:
    T = {
        "title": "Stock Analysis Tool",
        "ticker": "Ticker Symbol",
        "period": "Period",
        "data_mode": "Data Mode",
        "historical": "Historical Analysis",
        "realtime": "Real-Time View",
        "auto_refresh": "Auto-refresh (30s)",
        "analyze": "Analyze",
        "invalid_ticker": "Invalid ticker",
        "no_data": "No data available",
        "price_src": "Price source",
        "price": "Price",
        "signal": "Signal",
        "conviction_Strong Buy": "Strong Buy",
        "conviction_Buy": "Buy",
        "conviction_Neutral": "Neutral",
        "conviction_Sell": "Sell",
        "conviction_Strong Sell": "Strong Sell",
        "volatility": "Volatility",
        "max_dd": "Max Drawdown",
        "tab_tech": "Technical",
        "tab_fund": "Fundamental",
        "tab_risk": "Risk",
        "breakdown": "Breakdown",
        "trend": "Trend",
        "momentum": "Momentum",
        "volume": "Volume",
        "volatility_score": "Volatility",
        "fundamental": "Fundamental",
        "no_fund": "No fundamental data available",
        "sharpe": "Sharpe Ratio",
        "risk_metrics": "Risk Metrics",
        "features": "Features",
        "f1": "15+ technical indicators (SMA, EMA, RSI, MACD, Bollinger, ADX, Ichimoku, OBV, MFI, VWAP, and more)",
        "f2": "Regime-aware signal scoring (0-100) with conviction levels",
        "f3": "Risk metrics (VaR, Sharpe, drawdown, volatility)",
        "f4": "Fundamental analysis (P/E, EPS, F-Score)",
        "f5": "Real-Time: Crypto via Binance API",
        "f6": "Real-Time: US stocks via Alpha Vantage (key configured)",
        "f7": "Real-Time: China A-shares live data",
        "f8": "Historical Analysis: Multi-year technical analysis",
        "f9": "Interactive Plotly charts with indicator overlays",
        "f10": "Auto-refresh mode for real-time monitoring",
        "enter_ticker": "Enter a ticker and click Analyze",
        "live": " (Live)",
        "trending": "Trending",
        "ranging": "Ranging",
    }

# ---- Sidebar ----
with st.sidebar:
    ticker = st.text_input(T["ticker"], value="AAPL").strip().upper()
    period = st.selectbox(T["period"], ["1mo","3mo","6mo","1y","2y","5y"], index=3)
    data_mode = st.radio(T["data_mode"], [T["historical"], T["realtime"]], index=0)
    auto_refresh = st.checkbox(T["auto_refresh"], value=False)
    analyze = st.button(T["analyze"], type="primary")

if auto_refresh and "last" in st.session_state:
    time.sleep(30)
    st.rerun()

if analyze or ("last" in st.session_state and st.session_state.last == ticker):
    if "last" not in st.session_state:
        st.session_state.last = ticker
    with st.spinner("..."):
        if not validate_ticker(ticker):
            st.error(T["invalid_ticker"]); st.stop()
        
        df = get_historical_data(ticker, period=period)
        if df.empty:
            st.error(T["no_data"]); st.stop()
        
        if data_mode == T["realtime"]:
            rt = get_realtime_price(ticker)
            if rt and rt.get("price"):
                latest_price = rt["price"]
                rt_source = rt["source"]
                rt_change = rt.get("change_pct")
            else:
                latest_price = float(df["Close"].iloc[-1])
                rt_source = "yfinance (delayed)"
                rt_change = None
        else:
            latest_price = float(df["Close"].iloc[-1])
            rt_source = "yfinance (historical)"
            rt_change = None
        
        df_ind = compute_all_indicators(df)
        fund = get_fundamentals(ticker)
        sigs = generate_signals(df_ind, fund)
        risk = compute_all_risk_metrics(df_ind)

        prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else latest_price
        chg = latest_price - prev_close
        pct = rt_change if rt_change is not None else (chg / prev_close * 100 if prev_close != 0 else 0)
        
        # Translate conviction and regime
        cv_key = "conviction_" + sigs["conviction"]
        cn_conviction = T.get(cv_key, sigs["conviction"])
        rg_key = sigs["regime"]  # "trending" or "ranging"
        cn_regime = T.get(rg_key, rg_key)
        
        mode_tag = T["live"] if data_mode == T["realtime"] else ""
        st.markdown("## " + ticker.upper() + mode_tag + " - " + cn_conviction)
        st.caption(T["price_src"] + ": " + rt_source)
        
        c1,c2,c3,c4 = st.columns(4)
        c1.metric(T["price"], "${:.2f}".format(latest_price), "{:.2f} ({:.2f}%)".format(chg, pct))
        c2.metric(T["signal"], "{:.0f}/100".format(sigs["composite_score"]), cn_regime)
        c3.metric(T["volatility"], "{:.1f}%".format(risk["volatility"]["annualized"]*100))
        c4.metric(T["max_dd"], "{:.1f}%".format(risk["max_drawdown"]["max_drawdown_pct"]))

        tab1, tab2, tab3 = st.tabs([T["tab_tech"], T["tab_fund"], T["tab_risk"]])
        with tab1:
            from visualization.charts import render_candlestick, render_signal_gauge
            col_a, col_b = st.columns([3,1])
            with col_a:
                st.plotly_chart(render_candlestick(df), use_container_width=True)
            with col_b:
                st.plotly_chart(render_signal_gauge(sigs["composite_score"]), use_container_width=True)
                st.markdown("### " + T["breakdown"])
                labels = {"trend": T["trend"], "momentum": T["momentum"], "volume": T["volume"],
                          "volatility": T["volatility_score"], "fundamental": T["fundamental"]}
                for k,v in sigs["breakdown"].items():
                    lb = labels.get(k, k)
                    st.markdown("- **" + lb + "**: " + str(v))
        with tab2:
            if fund:
                st.json(fund)
            else:
                st.info(T["no_fund"])
        with tab3:
            st.metric(T["sharpe"], str(risk["sharpe_ratio"]))
            st.write("### " + T["risk_metrics"])
            st.json(risk)
else:
    st.info(T["enter_ticker"])
    st.markdown("### " + T["features"])
    for i in range(1, 11):
        key = "f" + str(i)
        st.markdown("- " + T[key])
