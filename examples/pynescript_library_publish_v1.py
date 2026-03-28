# @name: pynescript_library_publish_v1
import pandas as pd

from source import library, ta

library("Pyne Upgrade Utils", overlay=False, version=1)


def _series_like(values) -> pd.Series:
    if isinstance(values, pd.Series):
        return pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    return pd.Series(values, dtype="float64")


def ema_basis(close_values, length: int = 21) -> pd.Series:
    close_series = _series_like(close_values)
    return ta.ema(close_series, max(int(length or 21), 1)).reset_index(drop=True)


def trend_side(close_values, basis_values) -> pd.Series:
    close_series = _series_like(close_values)
    basis_series = _series_like(basis_values)
    return close_series.ge(basis_series).map(lambda is_up: "up" if bool(is_up) else "down")


def version_tag() -> str:
    return "v1"