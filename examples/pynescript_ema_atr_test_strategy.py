# @name: pynescript_ema_atr_test_strategy
# Strategy đơn giản để test replay / backtest / live trade.
#
# Logic:
#   - Entry BUY  : EMA fast cắt lên EMA slow  (crossover)
#   - Entry SELL : EMA fast cắt xuống EMA slow (crossunder)
#   - Stop Loss  : entry_price ± ATR * sl_mult
#   - Take Profit: entry_price ± ATR * tp_mult
#
# Cách test:
#   1. Add to Chart  → thấy mũi tên BUY/SELL trên chart
#   2. Publish       → tạo "EMA ATR Test" và "EMA ATR Test [Signal Preview]"
#   3. NTBacktest    → chọn "EMA ATR Test", chọn khung thời gian, bấm Run
#   4. Replay        → bind strategy, bấm Play từng bar
#   5. Live          → bind sau khi đã publish và pass certification gate
import numpy as np
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta

strategy("EMA ATR Test", overlay=True, process_orders_on_close=True, max_bars_back=100)

# ── Inputs ────────────────────────────────────────────────────────────────────
fast_period  = input.int(9,    title="Fast EMA",    key="fast_period")
slow_period  = input.int(21,   title="Slow EMA",    key="slow_period")
atr_length   = input.int(14,   title="ATR Length",  key="atr_length")
sl_mult      = input.float(1.5, title="SL ATR Mult", key="sl_mult")
tp_mult      = input.float(3.0, title="TP ATR Mult", key="tp_mult")
trade_qty    = input.float(1.0, title="Trade Qty",   key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "atr_length":  int(atr_length),
        "sl_mult":     float(sl_mult),
        "tp_mult":     float(tp_mult),
        "trade_qty":   float(trade_qty),
    } | dict(params or {})

    ema_fast  = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow  = ta.ema(frame["close"], int(p["slow_period"]))
    atr_value = ta.atr(frame, int(p["atr_length"]))

    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["atr"]      = atr_value

    buy_signal  = ta.crossover(ema_fast, ema_slow).fillna(False)
    sell_signal = ta.crossunder(ema_fast, ema_slow).fillna(False)

    frame["buy_signal"]  = buy_signal
    frame["sell_signal"] = sell_signal

    # ── Mapped entry fields ───────────────────────────────────────────────────
    frame["entry_side"]  = np.where(buy_signal, "BUY", np.where(sell_signal, "SELL", ""))
    frame["entry_price"] = frame["open"]
    frame["quantity"]    = float(p["trade_qty"])
    frame["size_pct"]    = 0.0

    # ── Stop Loss / Take Profit (ATR-based bracket) ───────────────────────────
    entry = frame["entry_price"]
    atr   = frame["atr"]
    sl_d  = atr * float(p["sl_mult"])
    tp_d  = atr * float(p["tp_mult"])

    frame["sl"] = np.where(
        frame["entry_side"] == "BUY",  entry - sl_d,
        np.where(frame["entry_side"] == "SELL", entry + sl_d, 0.0),
    )
    frame["tp"] = np.where(
        frame["entry_side"] == "BUY",  entry + tp_d,
        np.where(frame["entry_side"] == "SELL", entry - tp_d, 0.0),
    )
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)
