# @name: pynescript_volume_profile_fixed_range_with_rectangle
import pandas as pd

from source.controls.tradingview.volume_profile import calculate_volume_profile
from source import indicator, input


indicator("Pyne Volume Profile With Rectangle", overlay=True, max_bars_back=900)
look_back_bar = input.int(500, title="Look Back Bars", key="look_back_bar")
num_bars = input.int(100, title="Profile Rows", key="num_bars")
bar_len_mult = input.int(20, title="Bar Length Mult", key="bar_len_mult")
va_percent = input.int(68, title="Value Area %", key="va_percent")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "look_back_bar": int(look_back_bar),
        "num_bars": int(num_bars),
        "bar_len_mult": int(bar_len_mult),
        "va_percent": int(va_percent),
    } | dict(params or {})
    try:
        payload = calculate_volume_profile(
            df=frame.copy().reset_index(drop=True),
            lookback_depth=max(int(merged.get("look_back_bar", 500) or 500), 20),
            num_bars=max(int(merged.get("num_bars", 100) or 100), 8),
            bar_len_mult=max(int(merged.get("bar_len_mult", 20) or 20), 1),
            volume_type="Both",
            va_percent=max(int(merged.get("va_percent", 68) or 68), 1),
        )
    except Exception:
        payload = {}
    frame.attrs["volume_profile_payload"] = dict(payload or {})
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    payload = dict(frame.attrs.get("volume_profile_payload") or {})
    return ctx.atk.volume_profile(
        payload,
        key="single_volume_profile",
        orient="left",
        value_area_title="VA",
        poc_title="POC",
    )
