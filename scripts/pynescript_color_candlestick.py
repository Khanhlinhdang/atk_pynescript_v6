# @name: pynescript_color_candlestick
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator


indicator("Pyne Color Candlestick", overlay=False, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    return df.copy().reset_index(drop=True)


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    colors = []
    for index, _row in frame.reset_index(drop=True).iterrows():
        if index % 10 == 0:
            colors.append("#FF0000")
        elif index % 7 == 0:
            colors.append("#D6138B")
        elif index % 5 == 0:
            colors.append("#0000FF")
        else:
            colors.append("#62E265")
    return ctx.atk.color_candlestick(
        key="custom_color_candles",
        x=frame["index"].tolist(),
        open=frame["open"].tolist(),
        high=frame["high"].tolist(),
        low=frame["low"].tolist(),
        close=frame["close"].tolist(),
        colors=colors,
    )
