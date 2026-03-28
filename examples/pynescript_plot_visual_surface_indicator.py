# @name: pynescript_plot_visual_surface_indicator
# Docs: function-cookbook.html#plot-family-recipes
# Docs: examples-copybook.html#plot-visual-surfaces
import pandas as pd

from source import barcolor, bgcolor, indicator, plotarrow, plotbar, plotchar, ta


indicator("Pyne Plot Visual Surface Indicator", overlay=True, max_bars_back=120)

# This file focuses on the plot-family APIs that users often look for when
# migrating TradingView-style marker and bar decoration code.
plotbar("open", "high", "low", "close", key="ohlc_surface", title="OHLC Surface", color="#2962ff")
plotchar("breakout_signal", key="breakout_chars", title="Breakout", char="B", location="abovebar", color="#00c853")
plotarrow("trend_strength", key="trend_arrows", title="Trend Arrows", colorup="#00c853", colordown="#f23645")
barcolor("bar_tint", key="bar_tint")
bgcolor("session_bg_signal", key="session_bg", color="rgba(41,98,255,0.10)")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.ema(frame["close"], 8)
    frame["breakout_signal"] = frame["close"] >= frame["basis"]
    frame["trend_strength"] = ((frame["close"] - frame["basis"]).fillna(0.0) * 10.0).clip(-3.0, 3.0)
    frame["bar_tint"] = frame["breakout_signal"].map({True: "#2962ff", False: "#ff6d00"})
    frame["session_bg_signal"] = (frame.index % 6) < 3
    return frame