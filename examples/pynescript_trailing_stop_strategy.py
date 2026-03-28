# @name: pynescript_trailing_stop_strategy
import numpy as np
import pandas as pd

from source import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne Trailing Stop Strategy", overlay=True, process_orders_on_close=True, max_bars_back=120)
fast_period = input.int(10, title="Fast EMA", key="fast_period")
slow_period = input.int(30, title="Slow EMA", key="slow_period")
atr_length = input.int(10, title="ATR Length", key="atr_length")
trail_mult = input.float(2.0, title="Trail ATR", key="trail_mult")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "atr_length": int(atr_length),
        "trade_qty": float(trade_qty),
        "trail_mult": float(trail_mult),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    atr_value = ta.atr(frame, int(p["atr_length"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["atr"] = atr_value
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False)
    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"] = float(p.get("trade_qty", 0.0) or 0.0)
    frame["size_pct"] = 0.0
    frame["trail_offset"] = frame["atr"] * float(p["trail_mult"])
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
