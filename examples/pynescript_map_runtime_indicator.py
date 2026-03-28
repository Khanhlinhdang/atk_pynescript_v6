# @name: pynescript_map_runtime_indicator
import pandas as pd

from source import indicator, input, map, ta

indicator("Pyne Map Runtime Indicator", overlay=False)
fast_length = input.int(8, title="Fast Length", key="fast_length", minval=1)
slow_length = input.int(21, title="Slow Length", key="slow_length", minval=1)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_length": int(fast_length),
        "slow_length": int(slow_length),
    } | dict(params or {})

    fast_period = max(int(merged.get("fast_length", 8) or 8), 1)
    slow_period = max(int(merged.get("slow_length", 21) or 21), 1)
    frame["ema_fast"] = ta.ema(frame["close"], fast_period)
    frame["ema_slow"] = ta.ema(frame["close"], slow_period)
    frame["spread_value"] = (frame["ema_fast"] - frame["ema_slow"]).fillna(0.0)

    settings = map.new()
    map.put(settings, "fast_length", fast_period)
    map.put(settings, "slow_length", slow_period)
    trend_bias = "bullish" if float(frame["spread_value"].iloc[-1] or 0.0) >= 0.0 else "bearish"
    map.put(settings, "trend_bias", trend_bias)

    frame.attrs["map_keys"] = map.keys(settings)
    frame.attrs["map_size"] = map.size(settings)
    frame.attrs["trend_bias"] = map.get(settings, "trend_bias", "neutral")
    return frame