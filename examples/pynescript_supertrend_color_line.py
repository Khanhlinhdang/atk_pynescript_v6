# @name: pynescript_supertrend_color_line
import pandas as pd

from source import indicator, input, ta


indicator("Pyne SuperTrend Color Line", overlay=True, max_bars_back=320)
length = input.int(14, title="Length", key="length")
atr_length = input.int(14, title="ATR Length", key="atr_length")
multiplier = input.float(3.0, title="Multiplier", key="multiplier")
atr_mamode = input.string("rma", title="ATR MA Mode", key="atr_mamode")


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


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    points = []
    colors = []
    trend = frame["SUPERTd"].fillna(0.0).to_numpy()
    values = frame["SUPERTt"].ffill().to_numpy()
    indices = frame["index"].to_numpy()
    for idx in range(len(frame)):
        points.append((float(indices[idx]), float(values[idx])))
        trend_value = trend[idx - 1] if idx > 0 else trend[idx]
        colors.append("#00aa00" if trend_value == 1 else "#ff0000")
    return ctx.atk.color_line(
        key="supertrend_color_line",
        points=points,
        colors=colors,
    )
