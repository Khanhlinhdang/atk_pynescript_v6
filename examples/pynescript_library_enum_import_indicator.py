# @name: pynescript_library_enum_import_indicator
# Docs: function-cookbook.html#library-recipes
# Docs: examples-copybook.html#library-enum-import
import pandas as pd
from enum import Enum

from source import hline, import_library, indicator, input, plot, ta


indicator("Pyne Library Enum Import Indicator", overlay=False)
mode = input.enum("slow", title="Mode", key="mode", options=["fast", "slow", "auto"])
hline(0, title="Zero", color="#7f8c8d")

try:
    enum_utils = import_library("Pyne Enum Utils@1::TrendMode,resolve_length,bias_label as enum_utils")
    LIBRARY_IMPORT_MODE = "published-library"
except Exception:
    enum_utils = None
    LIBRARY_IMPORT_MODE = "local-fallback"

    class _TrendMode(Enum):
        FAST = "fast"
        SLOW = "slow"
        AUTO = "auto"

    class _EnumUtilsFallback:
        TrendMode = _TrendMode

        @staticmethod
        def resolve_length(selected_mode: _TrendMode | str) -> int:
            normalized = str(getattr(selected_mode, "value", selected_mode) or "slow").lower()
            mapping = {"fast": 8, "slow": 21, "auto": 34}
            return int(mapping.get(normalized, 21))

        @staticmethod
        def bias_label(spread_value: float) -> str:
            return "bullish" if float(spread_value or 0.0) >= 0.0 else "bearish"

    enum_utils = _EnumUtilsFallback()

plot("ema_fast", key="ema_fast_line", title="EMA Fast", color="#00c853", width=2)
plot("ema_slow", key="ema_slow_line", title="EMA Slow", color="#ff6d00", width=2)
plot("spread_value", key="spread_value_line", title="Spread", color="#2962ff")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {"mode": str(mode)} | dict(params or {})
    selected_mode = enum_utils.TrendMode(str(merged.get("mode", mode) or mode))
    length = enum_utils.resolve_length(selected_mode)
    slow_length = max(length + 13, 2)

    frame["ema_fast"] = ta.ema(frame["close"], length)
    frame["ema_slow"] = ta.ema(frame["close"], slow_length)
    frame["spread_value"] = (frame["ema_fast"] - frame["ema_slow"]).fillna(0.0)
    frame.attrs["library_import_mode"] = LIBRARY_IMPORT_MODE
    frame.attrs["trend_bias"] = enum_utils.bias_label(float(frame["spread_value"].iloc[-1] or 0.0)) if not frame.empty else "neutral"
    return frame