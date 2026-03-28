# @name: pynescript_library_import_indicator
import pandas as pd

from source import hline, import_library, indicator, input, ta

indicator("Pyne Library Import Indicator", overlay=False)
fast_length = input.int(9, title="Fast EMA", key="fast_length")
slow_length = input.int(21, title="Slow EMA", key="slow_length")
hline(0, title="Spread Zero", color="#7f8c8d")

try:
    signal_utils = import_library(
        "Pyne Signal Utils@1::ema_pair,spread,bullish_cross,bearish_cross as signal_utils"
    )
    LIBRARY_MODE = "published-library"
except Exception:
    signal_utils = None
    LIBRARY_MODE = "local-fallback"


def _fallback_ema_pair(close_values, fast_period: int, slow_period: int) -> tuple[pd.Series, pd.Series]:
    close_series = pd.to_numeric(close_values, errors="coerce").reset_index(drop=True)
    return (
        ta.ema(close_series, max(int(fast_period or 9), 1)).reset_index(drop=True),
        ta.ema(close_series, max(int(slow_period or 21), 1)).reset_index(drop=True),
    )


def _fallback_spread(close_values, basis_values) -> pd.Series:
    close_series = pd.to_numeric(close_values, errors="coerce").reset_index(drop=True)
    basis_series = pd.to_numeric(basis_values, errors="coerce").reset_index(drop=True)
    return (close_series - basis_series).reset_index(drop=True)


def _fallback_bullish_cross(fast_values, slow_values) -> pd.Series:
    return ta.crossover(fast_values, slow_values).fillna(False).reset_index(drop=True)


def _fallback_bearish_cross(fast_values, slow_values) -> pd.Series:
    return ta.crossunder(fast_values, slow_values).fillna(False).reset_index(drop=True)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_length": int(fast_length),
        "slow_length": int(slow_length),
    } | dict(params or {})

    fast_period = max(int(merged.get("fast_length", 9) or 9), 1)
    slow_period = max(int(merged.get("slow_length", 21) or 21), 1)
    close_series = pd.to_numeric(frame.get("close"), errors="coerce").reset_index(drop=True)

    if signal_utils is not None:
        ema_fast, ema_slow = signal_utils.ema_pair(close_series, fast_period, slow_period)
        spread_series = signal_utils.spread(close_series, ema_slow)
        cross_up = signal_utils.bullish_cross(ema_fast, ema_slow)
        cross_down = signal_utils.bearish_cross(ema_fast, ema_slow)
    else:
        ema_fast, ema_slow = _fallback_ema_pair(close_series, fast_period, slow_period)
        spread_series = _fallback_spread(close_series, ema_slow)
        cross_up = _fallback_bullish_cross(ema_fast, ema_slow)
        cross_down = _fallback_bearish_cross(ema_fast, ema_slow)

    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["spread_value"] = spread_series
    frame["library_cross_up"] = cross_up.fillna(False)
    frame["library_cross_down"] = cross_down.fillna(False)
    frame.attrs["library_import_mode"] = LIBRARY_MODE
    return frame