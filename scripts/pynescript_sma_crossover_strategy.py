# @name: pynescript_sma_crossover_strategy
# Docs: strategy-authoring-handbook.html#entry-fields
# Docs: function-cookbook.html#mapped-strategy-recipes
import numpy as np
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne SMA Crossover", overlay=True, process_orders_on_close=True)
fast_period = input.int(9, title="Fast SMA", key="fast_period")
slow_period = input.int(20, title="Slow SMA", key="slow_period")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {"fast_period": int(fast_period), "slow_period": int(slow_period)} | dict(params or {})
    sma_fast = ta.sma(frame["close"], int(p["fast_period"]))
    sma_slow = ta.sma(frame["close"], int(p["slow_period"]))
    frame["sma_fast"] = sma_fast
    frame["sma_slow"] = sma_slow
    frame["buy_signal"] = ta.crossover(sma_fast, sma_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(sma_fast, sma_slow).fillna(False)
    # This example teaches the minimal mapped entry field set.
    frame["mapped_entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["mapped_entry_price"] = frame["open"]
    frame["mapped_quantity"] = float(trade_qty)
    frame["mapped_size_pct"] = 0.0
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
