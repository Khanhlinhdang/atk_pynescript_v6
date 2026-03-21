# @name: pynescript_color_line_text
import pandas as pd

from source import Location, Weight
from source.gui.scripts_editor.pynescript_runtime import indicator, input


indicator("Pyne Color Line Text", overlay=True, max_bars_back=320)
signal_spacing = input.int(3, title="Signal Spacing", key="signal_spacing")
text_size = input.int(8, title="Text Size", key="text_size")


def _build_signal_payload(frame: pd.DataFrame, spacing: int, size: int):
    points = []
    texts = []
    colors = []
    sizes = []
    fonts = []
    weights = []
    locations = []
    location_cycle = [Location.Above, Location.Below, Location.Left, Location.Right]
    step = max(int(spacing or 1), 1)

    for index, row in frame.reset_index(drop=True).iterrows():
        if index % step != 0:
            continue
        open_price = float(row.get("open", 0.0) or 0.0)
        high_price = float(row.get("high", open_price) or open_price)
        low_price = float(row.get("low", open_price) or open_price)
        close_price = float(row.get("close", open_price) or open_price)
        x_value = float(row.get("index", index) or index)
        price_range = max(high_price - low_price, 0.0)
        body_ratio = abs(close_price - open_price) / price_range if price_range > 0 else 0.0

        if close_price >= open_price:
            text_value = "ST.BUY" if body_ratio > 0.7 else "BUY"
            color_value = "#17EC89"
            y_value = low_price
        else:
            text_value = "ST.SELL" if body_ratio > 0.7 else "SELL"
            color_value = "#9E1010"
            y_value = high_price

        points.append((x_value - 5.0, y_value, x_value + 5.0, y_value + 5.0))
        texts.append(text_value)
        colors.append(color_value)
        sizes.append(float(size))
        fonts.append("Arial")
        weights.append(Weight.Normal)
        locations.append(location_cycle[index % len(location_cycle)])

    return points, texts, colors, sizes, fonts, weights, locations


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "signal_spacing": int(signal_spacing),
        "text_size": int(text_size),
    } | dict(params or {})
    points, texts, colors, sizes, fonts, weights, locations = _build_signal_payload(
        frame,
        max(int(merged.get("signal_spacing", 3) or 3), 1),
        max(int(merged.get("text_size", 8) or 8), 1),
    )
    payload_len = len(points)
    frame = frame.head(payload_len).copy().reset_index(drop=True)
    frame["visual_show"] = True
    frame["visual_point"] = points
    frame["visual_text"] = texts
    frame["visual_color"] = colors
    frame["visual_size"] = sizes
    frame["visual_font"] = fonts
    frame["visual_weight"] = weights
    frame["visual_location"] = locations
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    visible_frame = frame[frame.get("visual_show", pd.Series(False, index=frame.index)).astype(bool)].reset_index(drop=True)
    return ctx.atk.color_line_text(
        key="candle_bias_signals",
        points=visible_frame.get("visual_point", pd.Series(dtype=object)).tolist(),
        texts=visible_frame.get("visual_text", pd.Series(dtype=object)).astype(str).tolist(),
        colors=visible_frame.get("visual_color", pd.Series(dtype=object)).astype(str).tolist(),
        sizes=pd.to_numeric(visible_frame.get("visual_size", pd.Series(dtype=float)), errors="coerce").fillna(8.0).tolist(),
        fonts=visible_frame.get("visual_font", pd.Series(dtype=object)).astype(str).tolist(),
        weights=visible_frame.get("visual_weight", pd.Series(dtype=object)).tolist(),
        locations=visible_frame.get("visual_location", pd.Series(dtype=object)).tolist(),
    )
