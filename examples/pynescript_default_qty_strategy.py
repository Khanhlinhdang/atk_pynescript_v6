# @name: pynescript_default_qty_strategy
# Docs: strategy-authoring-handbook.html#trade-frame-fields
# Docs: function-cookbook.html#trade-frame-recipes
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta


strategy(
    "Default Qty Strategy",
    overlay=True,
    default_qty_type="percent_of_equity",
    default_qty_value=25,
    process_orders_on_close=True,
)
fast_period = input.int(5, title="Fast", key="fast_period")
slow_period = input.int(12, title="Slow", key="slow_period")
trade_pct = input.float(25.0, title="Trade %", key="trade_pct")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "trade_pct": float(trade_pct),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False)

    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"] = 0.0
    frame["size_pct"] = np.where(frame["buy_signal"] | frame["sell_signal"], float(p.get("trade_pct", 0.0) or 0.0) / 100.0, 0.0)
    frame["tag"] = np.where(frame["buy_signal"], "long", np.where(frame["sell_signal"], "short", ""))
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)