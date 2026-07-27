import streamlit as st
import plotly.graph_objects as go

def build_dashboard(df, signals, risk_metrics, fundamentals, ticker):
    st.markdown(f"## {ticker.upper()} — {signals["conviction"]}")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        price = df["Close"].iloc[-1] if not df.empty else 0
        change = df["Close"].iloc[-1] - df["Close"].iloc[-2] if len(df) > 1 else 0
        pct = change / df["Close"].iloc[-2] * 100 if len(df) > 1 and df["Close"].iloc[-2] != 0 else 0
        st.metric("Price", f"${price:.2f}", f"{change:.2f} ({pct:.2f}%)")
    with col2:
        st.metric("Signal", f"{signals["composite_score"]:.0f}/100", signals["regime"])
    with col3:
        vol = risk_metrics["volatility"]["annualized"] * 100 if risk_metrics else 0
        st.metric("Volatility", f"{vol:.1f}%")
    with col4:
        dd = risk_metrics["max_drawdown"]["max_drawdown_pct"] if risk_metrics else 0
        st.metric("Max Drawdown", f"{dd:.1f}%")

    tab1, tab2, tab3 = st.tabs(["Technical", "Fundamental", "Risk"])
    with tab1:
        from .charts import render_candlestick, render_signal_gauge
        c1, c2 = st.columns([3, 1])
        with c1:
            fig = render_candlestick(df)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.plotly_chart(render_signal_gauge(signals["composite_score"]), use_container_width=True)
            st.markdown("### Signal Breakdown")
            for k, v in signals["breakdown"].items():
                st.markdown(f"- **{k}**: {v}")
    with tab2:
        if fundamentals:
            st.json(fundamentals)
        else:
            st.info("No fundamental data available")
    with tab3:
        from .charts import render_risk_radar
        st.plotly_chart(render_risk_radar(risk_metrics), use_container_width=True)
        st.json(risk_metrics["value_at_risk"])
        if risk_metrics["volatility"]["annualized"] > 0:
            sr = risk_metrics["sharpe_ratio"]
            st.metric("Sharpe Ratio", sr)
            st.metric("Annualized Vol", f"{risk_metrics["volatility"]["annualized"]*100:.1f}%")
            st.metric("Max Drawdown", f"{risk_metrics["max_drawdown"]["max_drawdown_pct"]:.1f}%")
