# @name: pynescript_native_table_indicator
# Docs: function-cookbook.html#table-recipes
# Docs: examples-copybook.html#native-table
import pandas as pd

from source import indicator, ta, table


indicator("Pyne Native Table Indicator", overlay=True, max_bars_back=180)

# Static dashboard structure can be declared once at module load.
dashboard = table.new("top_right", 2, 3, key="dashboard", title="Summary", border_color="#2962ff")
table.cell(dashboard, 0, 0, "Metric", bgcolor="#0f172a", text_color="#ffffff", text_bold=True)
table.cell(dashboard, 1, 0, "Value", bgcolor="#0f172a", text_color="#ffffff", text_bold=True)
table.cell(dashboard, 0, 1, "Trend")
table.cell(dashboard, 0, 2, "Spread")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["ema_fast"] = ta.ema(frame["close"], 8)
    frame["ema_slow"] = ta.ema(frame["close"], 21)
    frame["spread"] = (frame["ema_fast"] - frame["ema_slow"]).fillna(0.0)
    frame["trend_label"] = frame["spread"].ge(0.0).map({True: "Bullish", False: "Bearish"})
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    if frame is None or frame.empty or ctx is None:
        return None

    last = frame.iloc[-1]
    runtime_table = ctx.table.new("bottom_left", 2, 2, key="runtime_dashboard", title="Runtime")
    ctx.table.cell(runtime_table, 0, 0, "Bars", bgcolor="#111827", text_color="#ffffff")
    ctx.table.cell(runtime_table, 1, 0, str(len(frame)), text_color="#ffd600")
    ctx.table.cell(runtime_table, 0, 1, "Last Close", bgcolor="#111827", text_color="#ffffff")
    ctx.table.cell(runtime_table, 1, 1, f"{float(last['close']):.2f}", text_color="#00c853")

    # Static top-right cells and dynamic runtime cells can coexist.
    table.cell(dashboard, 1, 1, str(last["trend_label"]))
    table.cell(dashboard, 1, 2, f"{float(last['spread']):.3f}")
    return runtime_table