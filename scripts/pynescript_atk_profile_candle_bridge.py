# @name: pynescript_atk_profile_candle_bridge
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator, ta


indicator("Pyne ATK Profile Candle Bridge", overlay=True, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.sma(frame["close"], 5)
    frame.attrs["visual_profile_payload"] = {
        "tail_size": 4,
        "horizontal_bar": {
            "width": [8.0, 10.0, 12.0, 14.0],
            "height": 0.6,
            "orient": "left",
            "brushes": ["#2962ff", "#2962ff", "#00c853", "#ff6d00"],
        },
        "dual_horizontal_bar_fixed": {
            "data1": [18.0, 16.0, 14.0, 12.0],
            "data2": [9.0, 8.0, 7.0, 6.0],
            "height": 0.6,
            "orient": "left",
            "brushes1": ["#2962ff95"] * 4,
            "brushes2": ["#ffa32b95"] * 4,
        },
    }
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    payload = dict(frame.attrs.get("visual_profile_payload") or {})
    tail_size = int(payload.get("tail_size") or 4)
    tail = frame.tail(tail_size).reset_index(drop=True)
    if tail.empty:
        return []
    last_index = float(tail.iloc[-1]["index"])
    y_levels = [float(value) for value in tail["close"].tolist()]
    return [
        ctx.atk.candlestick(
            key="atk_sub_candles",
            x=[float(value) for value in tail["index"].tolist()],
            open=[float(value) for value in tail["open"].tolist()],
            high=[float(value) for value in tail["high"].tolist()],
            low=[float(value) for value in tail["low"].tolist()],
            close=[float(value) for value in tail["close"].tolist()],
        ),
        ctx.atk.horizontal_bar(
            key="atk_horizontal_profile",
            x=last_index + 4.0,
            y=y_levels,
            **dict(payload.get("horizontal_bar") or {}),
        ),
        ctx.atk.dual_horizontal_bar_fixed(
            key="atk_dual_profile",
            xData=last_index + 8.0,
            yData=y_levels,
            **dict(payload.get("dual_horizontal_bar_fixed") or {}),
        ),
    ]