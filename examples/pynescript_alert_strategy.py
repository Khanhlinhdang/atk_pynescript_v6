# @name: pynescript_alert_strategy
import numpy as np
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import alert, alertcondition, build_mapped_trade_frame, input, strategy, ta

strategy("Pyne Alert Strategy", overlay=True, process_orders_on_close=True)
fast_period = input.int(9, title="Fast EMA", key="fast_period")
slow_period = input.int(21, title="Slow EMA", key="slow_period")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")

# alertcondition(...) is a declarative rule that appears in metadata and alert surfaces.
alertcondition(True, title="EMA Cross Armed", message="Strategy loaded and EMA cross alerts are armed")

# alert(...) records a runtime alert call surface for the script itself.
alert("manual-strategy-alert", freq="once_per_bar_close")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "trade_qty": float(trade_qty),
    } | dict(params or {})

    ema_fast = ta.ema(frame["close"], max(int(merged.get("fast_period", 9) or 9), 1))
    ema_slow = ta.ema(frame["close"], max(int(merged.get("slow_period", 21) or 21), 1))
    buy_signal = ta.crossover(ema_fast, ema_slow).fillna(False)
    sell_signal = ta.crossunder(ema_fast, ema_slow).fillna(False)

    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["buy_signal"] = buy_signal
    frame["sell_signal"] = sell_signal
    frame["entry_side"] = np.where(buy_signal, "BUY", np.where(sell_signal, "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"] = float(merged.get("trade_qty", 1.0) or 1.0)
    frame["size_pct"] = 0.0
    frame["alert_message"] = np.where(
        buy_signal,
        "Bull EMA cross confirmed",
        np.where(sell_signal, "Bear EMA cross confirmed", ""),
    )
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)