# @name: pynescript_commission_strategy
# Docs: strategy-authoring-handbook.html#trade-frame-fields
# Docs: function-cookbook.html#trade-frame-recipes
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta


strategy(
    "Commission Strategy",
    overlay=True,
    commission_type="cash_per_order",
    commission_value=5,
    process_orders_on_close=True,
)
fast_period = input.int(5, title="Fast", key="fast_period")
slow_period = input.int(13, title="Slow", key="slow_period")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "trade_qty": float(trade_qty),
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
    frame["size_pct"] = 0.0
    frame["tag"] = np.where(frame["buy_signal"], "fee_long", np.where(frame["sell_signal"], "fee_short", ""))
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)