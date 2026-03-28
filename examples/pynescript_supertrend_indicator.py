# @name: pynescript_supertrend_indicator
import pandas as pd

from source import indicator, input, plot, ta


indicator("Pyne SuperTrend", overlay=True, max_bars_back=320)
length = input.int(14, title="Length", key="length")
atr_length = input.int(14, title="ATR Length", key="atr_length")
multiplier = input.float(3.0, title="Multiplier", key="multiplier")
atr_mamode = input.string("rma", title="ATR MA Mode", key="atr_mamode")
plot("SUPERTt", key="supertrend_line", title="SuperTrend", color="#00c853", width=2)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "length": int(length),
        "atr_length": int(atr_length),
        "multiplier": float(multiplier),
        "atr_mamode": str(atr_mamode),
    } | dict(params or {})
    trend_line, trend_dir = ta.supertrend(
        frame,
        length=max(int(merged.get("length", 14) or 14), 1),
        atr_length=max(int(merged.get("atr_length", 14) or 14), 1),
        multiplier=float(merged.get("multiplier", 3.0) or 3.0),
        atr_mamode=str(merged.get("atr_mamode", "rma") or "rma"),
    )
    frame["SUPERTt"] = pd.to_numeric(trend_line, errors="coerce")
    frame["SUPERTd"] = pd.to_numeric(trend_dir, errors="coerce")
    return frame
