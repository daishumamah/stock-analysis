import os, sys
PROJ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJ not in sys.path: sys.path.insert(0, PROJ)
import plotly.graph_objects as go

def render_candlestick(df, signals=None):
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        row_heights=[0.6, 0.15, 0.25])
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"],
                                 low=df["Low"], close=df["Close"], name="Price"), row=1, col=1)
    for p in (20,50,200):
        c=f"SMA_{p}"
        if c in df.columns:
            fig.add_trace(go.Scatter(x=df.index, y=df[c], mode="lines", name=f"SMA({p})"), row=1, col=1)
    if "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Upper"], mode="lines", name="BB Upper", line=dict(dash="dash")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_Lower"], mode="lines", name="BB Lower", line=dict(dash="dash")), row=1, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["Volume"], name="Volume"), row=2, col=1)
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], mode="lines", name="RSI"), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    fig.update_layout(height=700, template="plotly_dark", margin=dict(l=40,r=20,t=40,b=20))
    fig.update_xaxes(rangeslider_visible=False)
    return fig

def render_signal_gauge(score):
    c="red" if score<40 else "orange" if score<60 else "green"
    return go.Figure(go.Indicator(mode="gauge+number", value=score,
        gauge={"axis":{"range":[0,100]},"bar":{"color":c},
               "steps":[{"range":[0,40],"color":"#ffcccc"},{"range":[40,60],"color":"#ffffcc"},{"range":[60,100],"color":"#ccffcc"}]},
        title={"text":"Signal Score"})).update_layout(height=250, template="plotly_dark", margin=dict(l=40,r=40,t=40,b=20))

from plotly.subplots import make_subplots
