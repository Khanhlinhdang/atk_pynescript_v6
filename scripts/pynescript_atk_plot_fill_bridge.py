# @name: pynescript_atk_plot_fill_bridge
# Docs: pynescript_v6_api_documants/function-cookbook.html#plot-family-recipes
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator, ta


indicator("Pyne ATK Plot Fill Bridge", overlay=True, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    # The bridge still expects prepared source columns; only the render layer changes.
    frame["fast"] = ta.ema(frame["close"], 5)
    frame["slow"] = ta.ema(frame["close"], 10)
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    # Because the line visuals are created through ctx.atk.plot_line, the fill is also created
    # through ctx.atk.fill_between using those bridge line keys.
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