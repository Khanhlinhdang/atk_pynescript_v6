# @name: pynescript_bbands_fill_indicator
import pandas as pd

from source import indicator, input, linefill, plot, ta


indicator("Pyne BBands Fill", overlay=True, max_bars_back=240)
length = input.int(20, title="Length", key="length")
multiplier = input.float(2.0, title="StdDev Mult", key="multiplier")
mamode = input.string("sma", title="MA Mode", key="mamode")
source_type = input.string("close", title="Source", key="source_type")

plot("lb", key="bb_lower", title="Lower", color="#ff0000", width=1)
plot("cb", key="bb_basis", title="Basis", color="#ffa500", width=1)
plot("ub", key="bb_upper", title="Upper", color="#00aa00", width=1)
linefill.new("bb_lower", "bb_upper", key="bb_band_fill", color="rgba(63,57,100,0.44)")


def _nan_series(length_hint: int) -> pd.Series:
    return pd.Series([float("nan")] * max(int(length_hint or 0), 0), dtype="float64")


def _resolve_source_series(frame: pd.DataFrame, source_name: str) -> pd.Series:
    if frame is None or not isinstance(frame, pd.DataFrame) or frame.empty:
        return _nan_series(0)

    requested = str(source_name or "close").strip().lower()
    columns = list(frame.columns)
    lower_map = {str(column).strip().lower(): column for column in columns}

    for candidate in (requested, "close", "c"):
        original = lower_map.get(candidate)
        if original is not None:
            return pd.to_numeric(frame[original], errors="coerce").reset_index(drop=True)

    numeric_columns = [column for column in columns if pd.api.types.is_numeric_dtype(frame[column])]
    if numeric_columns:
        return pd.to_numeric(frame[numeric_columns[0]], errors="coerce").reset_index(drop=True)
    return _nan_series(len(frame))


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "length": int(length),
        "multiplier": float(multiplier),
        "mamode": str(mamode),
        "source_type": str(source_type),
    } | dict(params or {})

    source_name = str(merged.get("source_type", "close") or "close").strip().lower()
    source_series = _resolve_source_series(frame, source_name)

    lower = _nan_series(len(frame))
    basis = _nan_series(len(frame))
    upper = _nan_series(len(frame))
    period = max(int(merged.get("length", 20) or 20), 2)
    dev = float(merged.get("multiplier", 2.0) or 2.0)
    try:
        upper, basis, lower = ta.bbands(
            source_series,
            length=period,
            std=dev,
            mamode=str(merged.get("mamode", "sma") or "sma").lower(),
        )
    except Exception:
        basis = source_series.rolling(window=period, min_periods=period).mean()
        deviation = source_series.rolling(window=period, min_periods=period).std(ddof=0)
        upper = basis + dev * deviation
        lower = basis - dev * deviation

    frame["lb"] = lower.reset_index(drop=True)
    frame["cb"] = basis.reset_index(drop=True)
    frame["ub"] = upper.reset_index(drop=True)
    return frame
