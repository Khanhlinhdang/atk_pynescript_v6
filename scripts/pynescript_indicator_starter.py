# @name: pynescript_indicator_starter
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator, input, ta, hline

indicator("Pyne Indicator Starter", overlay=False)
length = input.int(14, title="Length", key="length")
source_type = input.source("close", title="Source", key="source_type")
hline(70, title="Overbought", color="#ff6b6b")
hline(30, title="Oversold", color="#51cf66")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {"length": int(length), "source_type": str(source_type)} | dict(params or {})
    src_name = str(p.get("source_type", "close"))
    src = frame[src_name] if src_name in frame.columns else frame["close"]
    frame["value"] = ta.rsi(src, int(p.get("length", 14)))
    return frame
