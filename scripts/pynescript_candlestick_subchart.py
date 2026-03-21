# @name: pynescript_candlestick_subchart
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator


indicator("Pyne Candlestick Sub", overlay=False, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["visual_x"] = pd.to_numeric(frame.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    frame["visual_open"] = pd.to_numeric(frame.get("open", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    frame["visual_high"] = pd.to_numeric(frame.get("high", pd.Series(dtype=float)), errors="coerce").fillna(frame["visual_open"])
    frame["visual_low"] = pd.to_numeric(frame.get("low", pd.Series(dtype=float)), errors="coerce").fillna(frame["visual_open"])
    frame["visual_close"] = pd.to_numeric(frame.get("close", pd.Series(dtype=float)), errors="coerce").fillna(frame["visual_open"])
    frame["visual_color"] = ["#089981" if float(open_) <= float(close_) else "#f23645" for open_, close_ in zip(frame["visual_open"], frame["visual_close"])]
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    return ctx.atk.candlestick(
        key="candles_sub",
        x=frame.get("visual_x", pd.Series(dtype=float)).tolist(),
        open=frame.get("visual_open", pd.Series(dtype=float)).tolist(),
        high=frame.get("visual_high", pd.Series(dtype=float)).tolist(),
        low=frame.get("visual_low", pd.Series(dtype=float)).tolist(),
        close=frame.get("visual_close", pd.Series(dtype=float)).tolist(),
        colors=frame.get("visual_color", pd.Series(dtype=object)).astype(str).tolist(),
    )
