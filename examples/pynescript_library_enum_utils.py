# @name: pynescript_library_enum_utils
# Docs: function-cookbook.html#library-recipes
# Docs: examples-copybook.html#library-enum-import
from enum import Enum

from source import library


library("Pyne Enum Utils", overlay=False, version=1)


class TrendMode(Enum):
    FAST = "fast"
    SLOW = "slow"
    AUTO = "auto"


def resolve_length(mode: TrendMode | str) -> int:
    normalized = str(getattr(mode, "value", mode) or "slow").lower()
    mapping = {
        "fast": 8,
        "slow": 21,
        "auto": 34,
    }
    return int(mapping.get(normalized, 21))


def bias_label(spread_value: float) -> str:
    return "bullish" if float(spread_value or 0.0) >= 0.0 else "bearish"