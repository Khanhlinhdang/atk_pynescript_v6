# @name: pynescript_limit_entry_strategy
# Docs: strategy-authoring-handbook.html#order-type-matrix
# Docs: examples-copybook.html#strategy-order-types
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta

strategy("Pyne Limit Entry Strategy", overlay=True, process_orders_on_close=True, max_bars_back=120)
fast_period = input.int(10, title="Fast EMA", key="fast_period")
slow_period = input.int(21, title="Slow EMA", key="slow_period")
pullback_pct = input.float(0.002, title="Pullback %", key="pullback_pct")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "pullback_pct": float(pullback_pct),
        "trade_qty": float(trade_qty),
    } | dict(params or {})

    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False)

    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_order_type"] = "LIMIT"
    frame["entry_price"] = frame["close"]
    frame["entry_limit_price"] = np.where(
        frame["entry_side"] == "BUY",
        frame["close"] * (1.0 - float(p["pullback_pct"])),
        np.where(frame["entry_side"] == "SELL", frame["close"] * (1.0 + float(p["pullback_pct"])), 0.0),
    )
    frame["quantity"] = float(p["trade_qty"])
    frame["size_pct"] = 0.0
    frame["post_only"] = frame["entry_side"] != ""
    frame["time_in_force"] = "GTC"
    frame["tag"] = np.where(frame["entry_side"] != "", "LIMIT_ENTRY", "")
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)