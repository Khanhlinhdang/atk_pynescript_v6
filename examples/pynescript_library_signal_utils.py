# @name: pynescript_library_signal_utils
import pandas as pd

from source import library, ta

library("Pyne Signal Utils", overlay=False, version=1)


def _series_like(values) -> pd.Series:
    if isinstance(values, pd.Series):
        return pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    return pd.Series(values, dtype="float64")


def ema_pair(close_values, fast_length: int = 9, slow_length: int = 21) -> tuple[pd.Series, pd.Series]:
    close_series = _series_like(close_values)
    fast = ta.ema(close_series, max(int(fast_length or 9), 1))
    slow = ta.ema(close_series, max(int(slow_length or 21), 1))
    return fast.reset_index(drop=True), slow.reset_index(drop=True)


def spread(close_values, basis_values) -> pd.Series:
    close_series = _series_like(close_values)
    basis_series = _series_like(basis_values)
    return (close_series - basis_series).reset_index(drop=True)


def bullish_cross(fast_values, slow_values) -> pd.Series:
    fast_series = _series_like(fast_values)
    slow_series = _series_like(slow_values)
    return ta.crossover(fast_series, slow_series).fillna(False).reset_index(drop=True)


def bearish_cross(fast_values, slow_values) -> pd.Series:
    fast_series = _series_like(fast_values)
    slow_series = _series_like(slow_values)
    return ta.crossunder(fast_series, slow_series).fillna(False).reset_index(drop=True)


def format_alert_message(side: str, price: float, symbol: str = "") -> str:
    resolved_side = str(side or "").strip().upper() or "SIGNAL"
    resolved_symbol = str(symbol or "").strip()
    symbol_prefix = f"{resolved_symbol} " if resolved_symbol else ""
    return f"{symbol_prefix}{resolved_side} @ {float(price):.2f}"