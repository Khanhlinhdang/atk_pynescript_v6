# @name: pynescript_visual_settings_lifecycle_demo
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import box, chart, indicator, plot, fill, line, linefill, ta


indicator(
    "Pyne Visual Settings Lifecycle Demo",
    overlay=True,
    explicit_plot_zorder=True,
    behind_chart=True,
    max_lines_count=2,
)

fast = plot("ema_fast", key="ema_fast", color="#00c853", show_last=120)
slow = plot("ema_slow", key="ema_slow", color="#ff6d00", show_last=120)
fill(fast, slow, key="ema_band", color="rgba(255,214,0,0.2)")

trend = line.new(0, 100, 1, 101, key="trend_line", color="#2962ff")
line.set_xy1(trend, chart.point.from_index(4, 103))
line.set_xy2(trend, chart.point.from_time(1700000000, 109))
line.set_color(trend, "#ffd600")
line.set_width(trend, 2)

# keep only latest 2 line.new objects via declaration max_lines_count
line.new(0, 98, 1, 99, key="old_line_1", color="#9e9e9e")
line.new(0, 97, 1, 98, key="old_line_2", color="#757575")

band = linefill.new("ema_fast", "ema_slow", key="linefill_band", color="rgba(41,98,255,0.12)")
linefill.set_color(band, "rgba(41,98,255,0.2)")

range_box = box.new(
    chart.point.from_index(2, 111),
    chart.point.from_index(10, 97),
    key="range_box",
    text="RANGE",
    bgcolor="rgba(255,214,0,0.08)",
    border_color="#ffd600",
)
box.set_lefttop(range_box, chart.point.from_index(4, 112))


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["ema_fast"] = ta.ema(frame["close"], 8)
    frame["ema_slow"] = ta.ema(frame["close"], 21)
    return frame
