# @name: pynescript_reduce_only_exit_strategy
# Docs: strategy-authoring-handbook.html#reduce-tif-fields
# Docs: examples-copybook.html#strategy-order-types
import numpy as np
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne Reduce Only Exit Strategy", overlay=True, process_orders_on_close=True, max_bars_back=120)
fast_period = input.int(9, title="Fast EMA", key="fast_period")
slow_period = input.int(21, title="Slow EMA", key="slow_period")
reduce_qty = input.float(1.0, title="Reduce Qty", key="reduce_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "reduce_qty": float(reduce_qty),
    } | dict(params or {})

    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow

    # This example teaches exit-management intent rather than fresh entries.
    reduce_long_signal = ta.crossunder(ema_fast, ema_slow).fillna(False)
    reduce_short_signal = ta.crossover(ema_fast, ema_slow).fillna(False)

    frame["mapped_entry_side"] = np.where(reduce_long_signal, "SELL", np.where(reduce_short_signal, "BUY", ""))
    frame["mapped_entry_order_type"] = "MARKET"
    frame["mapped_entry_price"] = frame["open"]
    frame["mapped_quantity"] = float(p["reduce_qty"])
    frame["mapped_size_pct"] = 0.0
    frame["mapped_reduce_only"] = frame["mapped_entry_side"] != ""
    frame["mapped_time_in_force"] = "IOC"
    frame["mapped_tag"] = np.where(frame["mapped_entry_side"] != "", "REDUCE_ONLY_EXIT", "")
    frame["mapped_comment"] = np.where(
        frame["mapped_entry_side"] != "",
        "Reduce-only exit management example; assumes an open position already exists.",
        "",
    )
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)