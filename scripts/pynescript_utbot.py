# @name: pynescript_utbot
import numpy as np
import pandas as pd

from source.controls.tradingview.utbot import utbot as _utbot
from source.gui.scripts_editor.pynescript_runtime import indicator, input


indicator("Pyne UTBOT", overlay=True, max_bars_back=360)
key_value_long = input.float(1.0, title="Long Key Value", key="key_value_long")
key_value_short = input.float(1.0, title="Short Key Value", key="key_value_short")
atr_long_period = input.int(10, title="ATR Long Period", key="atr_long_period")
ema_long_period = input.int(1, title="EMA Long Period", key="ema_long_period")
atr_short_period = input.int(10, title="ATR Short Period", key="atr_short_period")
ema_short_period = input.int(1, title="EMA Short Period", key="ema_short_period")


def _build_utbot_side(
    frame: pd.DataFrame,
    *,
    key_value: float,
    atr_period: int,
    ema_period: int,
) -> pd.DataFrame:
    try:
        result = _utbot(
            frame,
            key_value=float(key_value),
            atr_period=max(int(atr_period), 1),
            ema_period=max(int(ema_period), 1),
        )
    except Exception:
        result = pd.DataFrame(index=frame.index, data={"long": False, "short": False})
    if not isinstance(result, pd.DataFrame):
        result = pd.DataFrame(index=frame.index, data={"long": False, "short": False})
    return result.reset_index(drop=True)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "key_value_long": float(key_value_long),
        "key_value_short": float(key_value_short),
        "atr_long_period": int(atr_long_period),
        "ema_long_period": int(ema_long_period),
        "atr_short_period": int(atr_short_period),
        "ema_short_period": int(ema_short_period),
    } | dict(params or {})

    long_frame = _build_utbot_side(
        frame,
        key_value=float(merged.get("key_value_long", 1.0) or 1.0),
        atr_period=int(merged.get("atr_long_period", 10) or 10),
        ema_period=int(merged.get("ema_long_period", 1) or 1),
    )
    short_frame = _build_utbot_side(
        frame,
        key_value=float(merged.get("key_value_short", 1.0) or 1.0),
        atr_period=int(merged.get("atr_short_period", 10) or 10),
        ema_period=int(merged.get("ema_short_period", 1) or 1),
    )

    length_hint = min(len(frame), len(long_frame), len(short_frame))
    if length_hint <= 0:
        return pd.DataFrame(columns=["index", "high", "low", "long", "short", "prev_long", "prev_short", "direction", "y"])

    out = frame.tail(length_hint).reset_index(drop=True).copy()
    out["long"] = long_frame["long"].tail(length_hint).fillna(False).astype(bool).reset_index(drop=True)
    out["short"] = short_frame["short"].tail(length_hint).fillna(False).astype(bool).reset_index(drop=True)
    out["prev_long"] = out["long"].shift(1, fill_value=False)
    out["prev_short"] = out["short"].shift(1, fill_value=False)
    out["direction"] = np.where(out["prev_long"], "down", np.where(out["prev_short"], "up", ""))
    out["y"] = np.where(out["prev_long"], out["low"], np.where(out["prev_short"], out["high"], np.nan))
    out["visual_show"] = out["prev_long"] | out["prev_short"]
    out["visual_x"] = pd.to_numeric(out.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    out["visual_y"] = pd.to_numeric(out.get("y", pd.Series(dtype=float)), errors="coerce").ffill().fillna(0.0)
    out["visual_direction"] = np.where(out["prev_long"], "down", np.where(out["prev_short"], "up", ""))
    out["visual_color"] = np.where(out["prev_long"], "#05922F", np.where(out["prev_short"], "#c40111", ""))
    out["visual_size"] = 15
    return out


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    signals = frame[frame.get("visual_show", pd.Series(False, index=frame.index)).astype(bool)].reset_index(drop=True)

    return ctx.atk.color_arrow(
        key="utbot_indicator_arrows",
        x=signals.get("visual_x", pd.Series(dtype=float)).tolist(),
        y=signals.get("visual_y", pd.Series(dtype=float)).tolist(),
        directions=signals.get("visual_direction", pd.Series(dtype=object)).tolist(),
        colors=signals.get("visual_color", pd.Series(dtype=object)).tolist(),
        sizes=signals.get("visual_size", pd.Series(dtype=int)).tolist(),
    )
