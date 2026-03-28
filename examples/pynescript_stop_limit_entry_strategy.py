# @name: pynescript_stop_limit_entry_strategy
# Docs: strategy-authoring-handbook.html#order-type-matrix
# Docs: examples-copybook.html#strategy-order-types
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta

strategy("Pyne Stop Limit Entry Strategy", overlay=True, process_orders_on_close=True, max_bars_back=160)
breakout_length = input.int(8, title="Breakout Length", key="breakout_length")
limit_buffer_pct = input.float(0.001, title="Limit Buffer %", key="limit_buffer_pct")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "breakout_length": int(breakout_length),
        "limit_buffer_pct": float(limit_buffer_pct),
        "trade_qty": float(trade_qty),
    } | dict(params or {})

    trigger_high = frame["high"].rolling(int(p["breakout_length"]), min_periods=1).max().shift(1).fillna(frame["high"])
    trigger_low = frame["low"].rolling(int(p["breakout_length"]), min_periods=1).min().shift(1).fillna(frame["low"])
    momentum = ta.ema(frame["close"], 5) - ta.ema(frame["close"], 13)
    frame["momentum"] = momentum
    frame["buy_signal"] = (momentum > 0) & (frame["high"] >= trigger_high)
    frame["sell_signal"] = (momentum < 0) & (frame["low"] <= trigger_low)

    buy_limit = trigger_high * (1.0 + float(p["limit_buffer_pct"]))
    sell_limit = trigger_low * (1.0 - float(p["limit_buffer_pct"]))
    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_order_type"] = "STOP_LIMIT"
    frame["entry_price"] = frame["close"]
    frame["entry_trigger_price"] = np.where(
        frame["entry_side"] == "BUY",
        trigger_high,
        np.where(frame["entry_side"] == "SELL", trigger_low, 0.0),
    )
    frame["entry_limit_price"] = np.where(
        frame["entry_side"] == "BUY",
        buy_limit,
        np.where(frame["entry_side"] == "SELL", sell_limit, 0.0),
    )
    frame["quantity"] = float(p["trade_qty"])
    frame["size_pct"] = 0.0
    frame["time_in_force"] = np.where(frame["entry_side"] != "", "GTD", "GTC")
    frame["expiration"] = np.where(
        frame["entry_side"] != "",
        pd.to_numeric(frame["time"], errors="coerce").fillna(0).astype("int64") // 1000 + 3600,
        0,
    )
    frame["tag"] = np.where(frame["entry_side"] != "", "STOP_LIMIT_ENTRY", "")
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)