# @name: pynescript_macd_sub_indicator
import pandas as pd

from source import indicator, input, hline, plot, ta


indicator("Pyne MACD", overlay=False, max_bars_back=320)
fast_period = input.int(12, title="Fast", key="fast_period")
slow_period = input.int(26, title="Slow", key="slow_period")
signal_period = input.int(9, title="Signal", key="signal_period")
source_type = input.string("close", title="Source", key="source_type")
mamode = input.string("ema", title="MA Mode", key="mamode")
hline(0, key="macd_zero", title="Zero", color="#666666")
plot("macd", key="macd_line", title="MACD", color="#2196F3", width=1)
plot("signal", key="signal_line", title="Signal", color="#FF5722", width=1)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "signal_period": int(signal_period),
        "source_type": str(source_type),
        "mamode": str(mamode),
    } | dict(params or {})
    source_name = str(merged.get("source_type", "close") or "close").strip().lower()
    if source_name not in frame.columns:
        source_name = "close"
    macd_line, signal_line, histogram = ta.macd(
        frame[source_name],
        fast_period=max(int(merged.get("fast_period", 12) or 12), 1),
        slow_period=max(int(merged.get("slow_period", 26) or 26), 1),
        signal_period=max(int(merged.get("signal_period", 9) or 9), 1),
        mamode=str(merged.get("mamode", "ema") or "ema"),
    )
    frame["macd"] = pd.to_numeric(macd_line, errors="coerce")
    frame["histogram"] = pd.to_numeric(histogram, errors="coerce")
    frame["signal"] = pd.to_numeric(signal_line, errors="coerce")
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    colors = ["#4CAF50" if float(value) >= 0 else "#F44336" for value in frame["histogram"].fillna(0.0).tolist()]
    return ctx.atk.histogram(
        key="macd_histogram",
        x=frame["index"].tolist(),
        y=frame["histogram"].fillna(0.0).tolist(),
        colors=colors,
    )
