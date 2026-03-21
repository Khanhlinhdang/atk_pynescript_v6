# @name: pynescript_plot_shape_above
# Docs: pynescript_v6_api_documants/function-cookbook.html#plot-family-recipes
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator


indicator("Pyne Plot Shape Above", overlay=True, max_bars_back=240)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    # plotshape consumes a prepared boolean series rather than computing the condition itself.
    idx = range(len(frame))
    frame["shape_trigger"] = [(i % 5) == 0 for i in idx]
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    # The shape marker is rendered from the prepared trigger column and row-aligned x/y coordinates.
    return ctx.plotshape(
        key="shape_above_signals",
        when=frame["shape_trigger"].tolist(),
        x=frame["index"].tolist(),
        y=frame["high"].tolist(),
        style="labeldown",
        text="SELL",
        color="#AA0000",
        text_color="#ffffff",
        location="abovebar",
    )
