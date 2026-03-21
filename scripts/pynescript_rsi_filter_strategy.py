# @name: pynescript_rsi_filter_strategy
# Docs: strategy-authoring-handbook.html#entry-fields
# Docs: strategy-authoring-handbook.html#stage-split
import numpy as np
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne RSI Filter Strategy", overlay=True, process_orders_on_close=True)
fast_period = input.int(8, title="Fast EMA", key="fast_period")
slow_period = input.int(21, title="Slow EMA", key="slow_period")
rsi_length = input.int(14, title="RSI Length", key="rsi_length")
rsi_buy_level = input.int(55, title="Buy Level", key="rsi_buy_level")
rsi_sell_level = input.int(45, title="Sell Level", key="rsi_sell_level")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "rsi_length": int(rsi_length),
        "rsi_buy_level": int(rsi_buy_level),
        "rsi_sell_level": int(rsi_sell_level),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    rsi_value = ta.rsi(frame["close"], int(p["rsi_length"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["rsi"] = rsi_value
    # The RSI filter changes whether a crossover becomes a real entry, so it stays in build_signal_frame.
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False) & (rsi_value >= int(p["rsi_buy_level"]))
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False) & (rsi_value <= int(p["rsi_sell_level"]))
    frame["mapped_entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["mapped_entry_price"] = frame["open"]
    frame["mapped_quantity"] = float(trade_qty)
    frame["mapped_size_pct"] = 0.0
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
