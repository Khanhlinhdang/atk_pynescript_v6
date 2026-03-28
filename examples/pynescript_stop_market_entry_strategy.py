# @name: pynescript_stop_market_entry_strategy
# Docs: strategy-authoring-handbook.html#order-type-matrix
# Docs: examples-copybook.html#strategy-order-types
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta

strategy("Pyne Stop Market Entry Strategy", overlay=True, process_orders_on_close=True, max_bars_back=160)
breakout_length = input.int(10, title="Breakout Length", key="breakout_length")
ema_period = input.int(20, title="Trend EMA", key="ema_period")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "breakout_length": int(breakout_length),
        "ema_period": int(ema_period),
        "trade_qty": float(trade_qty),
    } | dict(params or {})

    ema_value = ta.ema(frame["close"], int(p["ema_period"]))
    trigger_high = frame["high"].rolling(int(p["breakout_length"]), min_periods=1).max().shift(1).fillna(frame["high"])
    trigger_low = frame["low"].rolling(int(p["breakout_length"]), min_periods=1).min().shift(1).fillna(frame["low"])
    frame["ema_trend"] = ema_value
    frame["buy_signal"] = (frame["close"] > ema_value) & (frame["high"] >= trigger_high)
    frame["sell_signal"] = (frame["close"] < ema_value) & (frame["low"] <= trigger_low)

    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_order_type"] = "STOP_MARKET"
    frame["entry_price"] = frame["close"]
    frame["entry_trigger_price"] = np.where(
        frame["entry_side"] == "BUY",
        trigger_high,
        np.where(frame["entry_side"] == "SELL", trigger_low, 0.0),
    )
    frame["quantity"] = float(p["trade_qty"])
    frame["size_pct"] = 0.0
    frame["time_in_force"] = "GTC"
    frame["tag"] = np.where(frame["entry_side"] != "", "STOP_MARKET_ENTRY", "")
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)