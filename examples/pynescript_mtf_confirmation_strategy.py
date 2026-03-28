# @name: pynescript_mtf_confirmation_strategy
import numpy as np
import pandas as pd

from source import strategy, input, ta, request, build_mapped_trade_frame

strategy("Pyne MTF Confirmation Strategy", overlay=True, process_orders_on_close=True, max_bars_back=180)
fast_period = input.int(10, title="Fast EMA", key="fast_period")
slow_period = input.int(24, title="Slow EMA", key="slow_period")
trend_length = input.int(34, title="HTF Trend EMA", key="trend_length")
confirm_tf = input.timeframe("15m", title="Confirm TF", key="confirm_tf")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "trend_length": int(trend_length),
        "confirm_tf": str(confirm_tf),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    htf_trend = request.security(
        frame,
        str(p["confirm_tf"]),
        lambda x: ta.ema(x["close"], int(p["trend_length"])),
    )
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["htf_trend"] = htf_trend
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False) & (frame["close"] >= htf_trend.fillna(frame["close"]))
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False) & (frame["close"] <= htf_trend.fillna(frame["close"]))
    frame["entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"] = float(trade_qty)
    frame["size_pct"] = 0.0
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
