# @name: pynescript_chart_point_showcase
import pandas as pd

from source import box, chart, indicator, label, line, polyline, ta


indicator("Pyne Chart Point Showcase", overlay=True, max_lines_count=3, max_boxes_count=2)

trend = line.new(
    chart.point.from_index(2, 101),
    chart.point.from_time(1700000000, 108),
    key="cp_trend",
    color="#2962ff",
)
line.set_xy1(trend, chart.point.from_index(4, 103))
line.set_xy2(trend, chart.point.from_time(1700000600, 109))

marker = label.new(
    chart.point.from_index(6, 106),
    key="cp_label",
    text="POINT",
    style="label_up",
    color="#00c853",
)

path = polyline.new(
    points=[
        chart.point.from_index(1, 100),
        chart.point.from_index(5, 104),
        chart.point.from_time(1700000000, 107),
    ],
    key="cp_path",
    color="#ffd600",
)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.ema(frame["close"], 5)
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    zone = ctx.box.new(
        chart.point.from_index(3, 111),
        chart.point.from_index(9, 97),
        key="cp_zone",
        text="ZONE",
        bgcolor="rgba(41,98,255,0.08)",
        border_color="#2962ff",
    )
    ctx.box.set_lefttop(zone, chart.point.from_index(4, 112))
    return None