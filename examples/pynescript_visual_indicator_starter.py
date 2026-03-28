# @name: pynescript_visual_indicator_starter
import pandas as pd

from source import indicator, input, ta, plot, plotshape, hline


indicator("Pyne Visual Indicator Starter", overlay=True)
length = input.int(20, title="Length", key="length")

plot("ema_fast", key="ema_fast", title="EMA Fast", color="#00c853", width=2)
plot("ema_slow", key="ema_slow", title="EMA Slow", color="#ff6d00", width=2)
hline(100, key="price_ref", title="Reference", color="#9e9e9e")
plotshape("buy_signal", key="buy_markers", location="belowbar", style="arrow_up", color="#00c853", text="BUY")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {"length": int(length)} | dict(params or {})
    fast_length = int(p.get("length", 20))
    slow_length = max(fast_length + 5, 2)
    frame["ema_fast"] = ta.ema(frame["close"], fast_length)
    frame["ema_slow"] = ta.ema(frame["close"], slow_length)
    frame["buy_signal"] = ta.crossover(frame["ema_fast"], frame["ema_slow"]).fillna(False)
    if not frame.empty:
        last = frame.iloc[-1]
        anchor = frame.iloc[max(len(frame) - 10, 0)]
        frame.attrs["visual_indicator_payload"] = {
            "box": {
                "left": int(anchor["index"]),
                "top": float(last["high"] + 0.5),
                "right": int(last["index"]),
                "bottom": float(last["low"] - 0.5),
                "text": "ACTIVE RANGE",
                "bgcolor": "rgba(41,98,255,0.12)",
                "border_color": "#2962ff",
            },
            "label": {
                "x": int(last["index"]),
                "y": float(last["close"]),
                "text": "LAST",
                "color": "#2962ff",
                "style": "label_down",
            },
            "line": {
                "x1": int(anchor["index"]),
                "y1": float(anchor["close"]),
                "x2": int(last["index"]),
                "y2": float(last["close"]),
                "color": "#ffd600",
                "text": "TREND",
            },
        }
    else:
        frame.attrs["visual_indicator_payload"] = {}
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    if frame is None or frame.empty or ctx is None:
        return None
    payload = dict(frame.attrs.get("visual_indicator_payload") or {})
    if not payload:
        return None

    ctx.box.new(
        key="last_range_box",
        **dict(payload.get("box") or {}),
    )
    ctx.label.new(
        key="last_close_label",
        **dict(payload.get("label") or {}),
    )
    return ctx.line.new(
        key="trend_hint",
        **dict(payload.get("line") or {}),
    )
