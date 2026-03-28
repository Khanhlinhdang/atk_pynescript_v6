# @name: pynescript_atk_plot_fill_bridge
import pandas as pd

from source import indicator, ta


indicator("Pyne ATK Plot Fill Bridge", overlay=True, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["fast"] = ta.ema(frame["close"], 5)
    frame["slow"] = ta.ema(frame["close"], 10)
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    return [
        ctx.atk.plot_line(key="atk_fast_line", source="fast", color="#00c853"),
        ctx.atk.plot_line(key="atk_slow_line", source="slow", color="#f23645"),
        ctx.atk.fill_between(
            key="atk_fast_slow_fill",
            line1="atk_fast_line",
            line2="atk_slow_line",
            color="rgba(41,98,255,0.12)",
            fill_alpha=31,
        ),
    ]