# @name: pynescript_stochrsi
import pandas as pd

from source import indicator, input, hline, plot, ta


indicator("Pyne STOCHRSI", overlay=False, max_bars_back=320)
period = input.int(14, title="Period", key="period")
rsi_period = input.int(14, title="RSI Period", key="rsi_period")
k_period = input.int(3, title="K Period", key="k_period")
d_period = input.int(3, title="D Period", key="d_period")
mamode = input.string("sma", title="MA Mode", key="mamode")
source_type = input.string("close", title="Source", key="source_type")
plot("stochrsi", key="stochrsi_line", title="STOCHRSI", color="#ff0000", width=1)
plot("signal", key="stochrsi_signal_line", title="Signal", color="#ffa500", width=1)
hline(80, key="stochrsi_overbought", title="Overbought", color="#ff6b6b")
hline(20, key="stochrsi_oversold", title="Oversold", color="#51cf66")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "period": int(period),
        "rsi_period": int(rsi_period),
        "k_period": int(k_period),
        "d_period": int(d_period),
        "mamode": str(mamode),
        "source_type": str(source_type),
    } | dict(params or {})
    source_name = str(merged.get("source_type", "close") or "close").strip().lower()
    if source_name not in frame.columns:
        source_name = "close"
    stochrsi_value, signal_value = ta.stochrsi(
        frame[source_name],
        period=max(int(merged.get("period", 14) or 14), 1),
        rsi_period=max(int(merged.get("rsi_period", 14) or 14), 1),
        k_period=max(int(merged.get("k_period", 3) or 3), 1),
        d_period=max(int(merged.get("d_period", 3) or 3), 1),
        mamode=str(merged.get("mamode", "sma") or "sma"),
    )
    frame["stochrsi"] = pd.to_numeric(stochrsi_value, errors="coerce")
    frame["signal"] = pd.to_numeric(signal_value, errors="coerce")
    return frame
