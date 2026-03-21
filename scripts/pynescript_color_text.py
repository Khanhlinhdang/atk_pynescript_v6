# @name: pynescript_color_text
import numpy as np
import pandas as pd

from source import Weight
from source.gui.scripts_editor.pynescript_runtime import indicator, input


indicator("Pyne Color Text", overlay=True, max_bars_back=320)
signal_spacing = input.int(3, title="Signal Spacing", key="signal_spacing")
text_size = input.int(8, title="Text Size", key="text_size")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "signal_spacing": int(signal_spacing),
        "text_size": int(text_size),
    } | dict(params or {})
    step = max(int(merged.get("signal_spacing", 3) or 3), 1)
    size = max(int(merged.get("text_size", 8) or 8), 1)
    open_values = pd.to_numeric(frame.get("open", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    high_values = pd.to_numeric(frame.get("high", pd.Series(dtype=float)), errors="coerce").fillna(open_values)
    low_values = pd.to_numeric(frame.get("low", pd.Series(dtype=float)), errors="coerce").fillna(open_values)
    close_values = pd.to_numeric(frame.get("close", pd.Series(dtype=float)), errors="coerce").fillna(open_values)
    price_range = (high_values - low_values).clip(lower=0.0)
    body_ratio = (close_values - open_values).abs().where(price_range > 0, 0.0) / price_range.where(price_range > 0, 1.0)
    bullish = close_values >= open_values
    visible = pd.Series([(index % step) == 0 for index in range(len(frame))], index=frame.index)
    frame["visual_show"] = visible
    frame["visual_x"] = pd.to_numeric(frame.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    frame["visual_y"] = np.where(bullish, low_values, high_values)
    frame["visual_text"] = np.where(
        bullish,
        np.where(body_ratio > 0.7, "ST.BUY", "BUY"),
        np.where(body_ratio > 0.7, "ST.SELL", "SELL"),
    )
    frame["visual_color"] = np.where(bullish, "#17EC89", "#9E1010")
    frame["visual_size"] = float(size)
    frame["visual_font"] = "Arial"
    frame["visual_weight"] = Weight.Normal
    frame["visual_position"] = np.where(bullish, "above", "below")
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    visible_frame = frame[frame.get("visual_show", pd.Series(False, index=frame.index)).astype(bool)].reset_index(drop=True)

    return ctx.atk.color_text(
        key="candle_bias_text",
        x=visible_frame.get("visual_x", pd.Series(dtype=float)).tolist(),
        y=pd.to_numeric(visible_frame.get("visual_y", pd.Series(dtype=float)), errors="coerce").fillna(0.0).tolist(),
        texts=visible_frame.get("visual_text", pd.Series(dtype=object)).astype(str).tolist(),
        colors=visible_frame.get("visual_color", pd.Series(dtype=object)).astype(str).tolist(),
        sizes=pd.to_numeric(visible_frame.get("visual_size", pd.Series(dtype=float)), errors="coerce").fillna(8.0).tolist(),
        fonts=visible_frame.get("visual_font", pd.Series(dtype=object)).astype(str).tolist(),
        weights=visible_frame.get("visual_weight", pd.Series(dtype=object)).tolist(),
        positions=visible_frame.get("visual_position", pd.Series(dtype=object)).astype(str).tolist(),
    )
