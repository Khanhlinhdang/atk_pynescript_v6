# @name: pynescript_utbot_strategy
import numpy as np
import pandas as pd

from source.controls.strategy_cores.utbot_core import (
    DEFAULT_UTBOT_PARAMS as _UTBOT_DEFAULT_PARAMS,
    DEFAULT_UTBOT_STYLES as _UTBOT_DEFAULT_STYLES,
    build_utbot_signal_frame as _build_signal_frame_impl,
    build_utbot_trade_frame as _build_trade_frame_impl,
)
from source import strategy, input


strategy("Pyne UTBOT Strategy", overlay=True, process_orders_on_close=True)
key_value = input.float(1.0, title="Key Value", key="key_value")
atr_period = input.int(10, title="ATR Period", key="atr_period")
ema_period = input.int(1, title="EMA Period", key="ema_period")
size_pct = input.float(0.95, title="Size %", key="size_pct")
sl_atr_mult = input.float(1.5, title="SL ATR Mult", key="sl_atr_mult")
tp_atr_mult = input.float(3.0, title="TP ATR Mult", key="tp_atr_mult")


def _merged_params(params: dict | None = None) -> dict:
    return dict(_UTBOT_DEFAULT_PARAMS) | {
        "key_value": float(key_value),
        "atr_period": int(atr_period),
        "ema_period": int(ema_period),
        "size_pct": float(size_pct),
        "sl_atr_mult": float(sl_atr_mult),
        "tp_atr_mult": float(tp_atr_mult),
        "trade_qty": 0.0,
    } | dict(params or {})


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    signal_frame = _build_signal_frame_impl(df, _merged_params(params))
    if signal_frame.empty:
        return signal_frame
    signal_frame = signal_frame.copy().reset_index(drop=True)
    signal_frame["visual_show"] = signal_frame.get("arrow_direction", pd.Series("", index=signal_frame.index)).astype(str).ne("")
    signal_frame["visual_x"] = pd.to_numeric(signal_frame.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    signal_frame["visual_y"] = pd.to_numeric(signal_frame.get("arrow_price", pd.Series(dtype=float)), errors="coerce").ffill().fillna(0.0)
    signal_frame["visual_direction"] = signal_frame.get("arrow_direction", pd.Series(dtype=object)).astype(str)
    signal_frame["visual_color"] = signal_frame.get("arrow_color", pd.Series(dtype=object)).astype(str)
    signal_frame["visual_size"] = pd.to_numeric(signal_frame.get("arrow_size", pd.Series(dtype=float)), errors="coerce").fillna(15).astype(int)
    return signal_frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return _build_trade_frame_impl(
        signal_df,
        _merged_params(params),
        dict(_UTBOT_DEFAULT_STYLES) | dict(styles or {}),
    )


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    signals = frame[frame.get("arrow_direction", pd.Series("", index=frame.index)).astype(str).ne("")].reset_index(drop=True)
    return ctx.atk.color_arrow(
        key="utbot_strategy_arrows",
        x=pd.to_numeric(signals.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0).tolist(),
        y=pd.to_numeric(signals.get("arrow_price", pd.Series(dtype=float)), errors="coerce").ffill().fillna(0.0).tolist(),
        directions=signals.get("arrow_direction", pd.Series(dtype=object)).astype(str).tolist(),
        colors=signals.get("arrow_color", pd.Series(dtype=object)).astype(str).tolist(),
        sizes=pd.to_numeric(signals.get("arrow_size", pd.Series(dtype=float)), errors="coerce").fillna(15).astype(int).tolist(),
    )
