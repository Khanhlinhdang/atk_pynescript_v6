# @name: pynescript_volume_with_ma
import pandas as pd

from source.controls.ma_overload import ma
from source.gui.scripts_editor.pynescript_runtime import indicator, input


indicator("Pyne Volume With MA", overlay=False, max_bars_back=320)
mamode = input.string("sma", title="MA Mode", key="mamode")
length = input.int(5, title="Length", key="length")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "mamode": str(mamode),
        "length": int(length),
    } | dict(params or {})
    frame["data"] = pd.to_numeric(
        ma(str(merged.get("mamode", "sma") or "sma"), source=frame["volume"], length=max(int(merged.get("length", 5) or 5), 1)),
        errors="coerce",
    )
    frame["visual_x"] = pd.to_numeric(frame.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    frame["visual_ma_y"] = pd.to_numeric(frame.get("data", pd.Series(dtype=float)), errors="coerce")
    frame["visual_hist_y"] = pd.to_numeric(frame.get("volume", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    frame["visual_hist_color"] = ["#089981" if float(open_) <= float(close_) else "#f23645" for open_, close_ in zip(frame["open"], frame["close"])]
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    return [
        ctx.atk.plot_line(
            key="volume_ma",
            x=frame.get("visual_x", pd.Series(dtype=float)).tolist(),
            y=[float(value) if pd.notna(value) else float("nan") for value in frame.get("visual_ma_y", pd.Series(dtype=float)).tolist()],
            color="#ffff00",
            width=1,
        ),
        ctx.atk.histogram(
            key="volume_histogram",
            x=frame.get("visual_x", pd.Series(dtype=float)).tolist(),
            y=frame.get("visual_hist_y", pd.Series(dtype=float)).tolist(),
            colors=frame.get("visual_hist_color", pd.Series(dtype=object)).astype(str).tolist(),
        ),
    ]
