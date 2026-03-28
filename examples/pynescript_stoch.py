# @name: pynescript_stoch
import pandas as pd

from source import indicator, input, hline, plot, ta

indicator("Pyne STOCH", overlay=False, max_bars_back=320)
k_period = input.int(14, title="K Period", key="k_period")
d_period = input.int(3, title="D Period", key="d_period")
smooth_k = input.int(3, title="Smooth K", key="smooth_k")
mamode = input.string("sma", title="MA Mode", key="mamode")
plot("stoch_k", key="stoch_k_line", title="%K", color="#2196F3", width=1)
plot("stoch_d", key="stoch_d_line", title="%D", color="#FF5722", width=1)
hline(80, key="stoch_overbought", title="Overbought", color="#ff6b6b")
hline(20, key="stoch_oversold", title="Oversold", color="#51cf66")

def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "k_period": int(k_period),
        "d_period": int(d_period),
        "smooth_k": int(smooth_k),
        "mamode": str(mamode),
    } | dict(params or {})
    stoch_k, stoch_d = ta.stoch(
        frame,
        k_period=max(int(merged.get("k_period", 14) or 14), 1),
        d_period=max(int(merged.get("d_period", 3) or 3), 1),
        smooth_k=max(int(merged.get("smooth_k", 3) or 3), 1),
        mamode=str(merged.get("mamode", "sma") or "sma"),
    )
    frame["stoch_k"] = pd.to_numeric(stoch_k, errors="coerce")
    frame["stoch_d"] = pd.to_numeric(stoch_d, errors="coerce")
    return frame
