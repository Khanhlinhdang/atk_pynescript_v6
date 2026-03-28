# @name: pynescript_mt5_gtd_pending_strategy
# Docs: strategy-authoring-handbook.html#order-type-matrix
# Docs: examples-copybook.html#strategy-order-types
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta


strategy("Pyne MT5 GTD Pending Strategy", overlay=True, process_orders_on_close=True, max_bars_back=160)
fast_period = input.int(10, title="Fast EMA", key="fast_period")
slow_period = input.int(21, title="Slow EMA", key="slow_period")
limit_buffer_pct = input.float(0.0015, title="Limit Buffer %", key="limit_buffer_pct")
expire_after_minutes = input.int(60, title="Expire After Minutes", key="expire_after_minutes")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "limit_buffer_pct": float(limit_buffer_pct),
        "expire_after_minutes": int(expire_after_minutes),
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
        frame["close"] * (1.0 - float(p["limit_buffer_pct"])),
        np.where(frame["entry_side"] == "SELL", frame["close"] * (1.0 + float(p["limit_buffer_pct"])), 0.0),
    )
    frame["quantity"] = float(p["trade_qty"])
    frame["size_pct"] = 0.0
    frame["time_in_force"] = np.where(frame["entry_side"] != "", "GTD", "GTC")
    frame["expiration"] = np.where(
        frame["entry_side"] != "",
        pd.to_numeric(frame["time"], errors="coerce").fillna(0).astype("int64") // 1000 + max(int(p["expire_after_minutes"]), 1) * 60,
        0,
    )
    frame["tag"] = np.where(frame["entry_side"] != "", "MT5_GTD_PENDING", "")
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)