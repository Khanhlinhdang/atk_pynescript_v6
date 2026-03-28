# @name: pynescript_candlestick
import pandas as pd

from source import indicator, plotcandle


indicator("Pyne Candlestick", overlay=True, max_bars_back=320)
plotcandle("open", "high", "low", "close", key="candles", title="Candles")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    return df.copy().reset_index(drop=True)
