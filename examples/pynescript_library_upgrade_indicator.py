# @name: pynescript_library_upgrade_indicator
import pandas as pd

from source import import_library, indicator, input, ta

indicator("Pyne Library Upgrade Indicator", overlay=False)
fast_length = input.int(9, title="Fast EMA", key="fast_length")
slow_length = input.int(21, title="Slow EMA", key="slow_length")


def _series_like(values) -> pd.Series:
    if isinstance(values, pd.Series):
        return pd.to_numeric(values, errors="coerce").reset_index(drop=True)
    return pd.Series(values, dtype="float64")


def _local_ema_basis(close_values, length: int = 21) -> pd.Series:
    close_series = _series_like(close_values)
    return ta.ema(close_series, max(int(length or 21), 1)).reset_index(drop=True)


def _local_signal_score(close_values, basis_values) -> pd.Series:
    close_series = _series_like(close_values)
    basis_series = _series_like(basis_values)
    return close_series.sub(basis_series).fillna(0.0).round(4).reset_index(drop=True)


try:
    legacy_utils = import_library(
        "Pyne Upgrade Utils@1::ema_basis,trend_side,version_tag as legacy_utils"
    )
except Exception:
    legacy_utils = None

try:
    upgraded_utils = import_library(
        "Pyne Upgrade Utils@2::ema_basis,signal_score,trend_side,version_tag as upgraded_utils"
    )
except Exception:
    upgraded_utils = None


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_length": int(fast_length),
        "slow_length": int(slow_length),
    } | dict(params or {})

    fast_period = max(int(merged.get("fast_length", 9) or 9), 1)
    slow_period = max(int(merged.get("slow_length", 21) or 21), 1)
    close_series = pd.to_numeric(frame.get("close"), errors="coerce").reset_index(drop=True)

    available_versions: list[int] = []
    upgrade_tags = {"legacy": "local-v1", "upgraded": "local-v2"}
    mode = "local-fallback"

    if legacy_utils is not None:
        legacy_basis = legacy_utils.ema_basis(close_series, fast_period)
        available_versions.append(1)
        upgrade_tags["legacy"] = str(legacy_utils.version_tag())
    else:
        legacy_basis = _local_ema_basis(close_series, fast_period)

    if upgraded_utils is not None:
        upgraded_basis = upgraded_utils.ema_basis(close_series, slow_period)
        upgrade_score = upgraded_utils.signal_score(close_series, upgraded_basis)
        available_versions.append(2)
        upgrade_tags["upgraded"] = str(upgraded_utils.version_tag())
    else:
        upgraded_basis = _local_ema_basis(close_series, slow_period)
        upgrade_score = _local_signal_score(close_series, upgraded_basis)

    if available_versions == [1, 2]:
        mode = "published-upgrade"
    elif available_versions == [1]:
        mode = "legacy-only"
    elif available_versions == [2]:
        mode = "upgraded-only"

    frame["legacy_basis"] = legacy_basis
    frame["upgraded_basis"] = upgraded_basis
    frame["upgrade_delta"] = (legacy_basis - upgraded_basis).fillna(0.0).round(4)
    frame["upgrade_score"] = upgrade_score
    frame.attrs["library_upgrade_mode"] = mode
    frame.attrs["library_upgrade_versions"] = available_versions
    frame.attrs["library_upgrade_tags"] = upgrade_tags
    return frame