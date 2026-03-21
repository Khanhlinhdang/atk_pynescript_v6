# @name: pynescript_plot_shape_below
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator


indicator("Pyne Plot Shape Below", overlay=True, max_bars_back=240)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    idx = range(len(frame))
    frame["shape_trigger"] = [(i % 5) == 0 for i in idx]
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    return ctx.plotshape(
        key="shape_below_signals",
        when=frame["shape_trigger"].tolist(),
        x=frame["index"].tolist(),
        y=frame["low"].tolist(),
        style="labelup",
        text="BUY",
        color="#00AA00",
        text_color="#ffffff",
        location="belowbar",
    )
