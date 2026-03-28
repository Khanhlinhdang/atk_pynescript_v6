# @name: pynescript_rsi_indicator
import pandas as pd

from source import indicator, input, hline, plot, ta


indicator("Pyne RSI", overlay=False, max_bars_back=320)
period = input.int(14, title="Period", key="period")
source_type = input.string("close", title="Source", key="source_type")
mamode = input.string("rma", title="MA Mode", key="mamode")
overbought = input.int(70, title="Overbought", key="overbought")
oversold = input.int(30, title="Oversold", key="oversold")
plot("data", key="rsi_line", title="RSI", color="#ffff00", width=1)
hline(70, key="rsi_overbought", title="Overbought", color="#ff6b6b")
hline(30, key="rsi_oversold", title="Oversold", color="#51cf66")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "period": int(period),
        "source_type": str(source_type),
        "mamode": str(mamode),
    } | dict(params or {})
    source_name = str(merged.get("source_type", "close") or "close").strip().lower()
    if source_name not in frame.columns:
        source_name = "close"
    frame["data"] = pd.to_numeric(ta.rsi(frame[source_name], max(int(merged.get("period", 14) or 14), 1)), errors="coerce")
    return frame
