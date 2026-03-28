# @name: pynescript_murrey_math_lines_v2
import pandas as pd

from source.controls.tradingview.murrey_math_lines_v2 import Murrey_Math_Lines
from source import indicator, input, plot


indicator("Pyne Murrey Math Lines V2", overlay=True, max_bars_back=320)
frame_size = input.int(64, title="Frame", key="frame")
multiplier = input.float(1.5, title="Multiplier", key="mult")
use_wicks = input.bool(True, title="Use Wicks", key="wicks")
mintick = input.float(0.01, title="Min Tick", key="mintick")

_MURREY_LINES = [
    ("Plus38", "plus_38", "#FF00FF"),
    ("Plus28", "plus_28", "#FFA500"),
    ("Plus18", "plus_18", "#00CED1"),
    ("EightEight", "eight_eight", "#FFD700"),
    ("SevenEight", "seven_eight", "#00FF00"),
    ("SixEight", "six_eight", "#1E90FF"),
    ("FiveEight", "five_eight", "#FF4500"),
    ("FourEight", "four_eight", "#8A2BE2"),
    ("ThreeEight", "three_eight", "#00FFFF"),
    ("TwoEight", "two_eight", "#A52A2A"),
    ("OneEight", "one_eight", "#C0C0C0"),
    ("ZeroEight", "zero_eight", "#000000"),
    ("Minus18", "minus_18", "#FF0000"),
    ("Minus28", "minus_28", "#800000"),
    ("Minus38", "minus_38", "#808080"),
]

for source_name, key_name, color_value in _MURREY_LINES:
    plot(source_name, key=key_name, title=source_name, color=color_value, width=1)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "frame": int(frame_size),
        "mult": float(multiplier),
        "wicks": bool(use_wicks),
        "mintick": float(mintick),
    } | dict(params or {})
    empty_columns = {"index": frame.get("index", pd.Series(dtype="float64"))}
    for source_name, _, _ in _MURREY_LINES:
        empty_columns[source_name] = pd.Series([float("nan")] * len(frame), dtype="float64")

    try:
        calculator = Murrey_Math_Lines(
            frame=max(int(merged.get("frame", 64) or 64), 8),
            mult=float(merged.get("mult", 1.5) or 1.5),
            wicks=bool(merged.get("wicks", True)),
            mintick=max(float(merged.get("mintick", 0.01) or 0.01), 1e-9),
        )
        result = calculator.calculate(frame)
        if isinstance(result, dict) and result.get("index") is not None:
            return pd.DataFrame(result).reset_index(drop=True)
    except Exception:
        pass
    return pd.DataFrame(empty_columns).reset_index(drop=True)
