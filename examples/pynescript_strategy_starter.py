# @name: pynescript_strategy_starter
import numpy as np
import pandas as pd

from source import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne Strategy Starter", overlay=True, process_orders_on_close=True)
fast_period = input.int(10, title="Fast", key="fast_period")
slow_period = input.int(21, title="Slow", key="slow_period")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")
size_pct = input.float(0.0, title="Size %", key="size_pct")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "trade_qty": float(trade_qty),
        "size_pct": float(size_pct),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False)
    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"] = float(p.get("trade_qty", 0.0) or 0.0)
    frame["size_pct"] = float(p.get("size_pct", 0.0) or 0.0)
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
