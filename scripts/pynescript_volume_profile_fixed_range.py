# @name: pynescript_volume_profile_fixed_range
import pandas as pd

from source.controls.tradingview.volume_profile_fixed_range import calculate_volume_profile
from source.gui.scripts_editor.pynescript_runtime import indicator, input


indicator("Pyne Volume Profile Fixed Range", overlay=True, max_bars_back=900)
look_back_bar = input.int(500, title="Look Back Bars", key="look_back_bar")
row_size = input.int(24, title="Row Size", key="row_size")
value_area_volume_percent = input.int(70, title="Value Area %", key="value_area_volume_percent")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "look_back_bar": int(look_back_bar),
        "row_size": int(row_size),
        "value_area_volume_percent": int(value_area_volume_percent),
    } | dict(params or {})
    try:
        payload = calculate_volume_profile(
            frame.copy().reset_index(drop=True),
            max(int(merged.get("look_back_bar", 500) or 500), 20),
            max(int(merged.get("row_size", 24) or 24), 2),
            max(int(merged.get("value_area_volume_percent", 70) or 70), 1),
        )
    except Exception:
        payload = {}
    frame.attrs["volume_profile_payload"] = dict(payload or {})
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    payload = dict(frame.attrs.get("volume_profile_payload") or {})
    return ctx.atk.volume_profile(
        payload,
        key="dual_volume_profile",
        orient="right",
        up_color="#0126A0",
        down_color="#ffa32b",
        value_area_title="VA",
        poc_title="POC",
    )
