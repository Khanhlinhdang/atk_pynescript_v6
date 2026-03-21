# @name: pynescript_bracket_strategy
# Docs: strategy-authoring-handbook.html#risk-fields
# Docs: function-cookbook.html#mapped-strategy-recipes
import numpy as np
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import strategy, input, ta, build_mapped_trade_frame

strategy("Pyne Bracket Strategy", overlay=True, process_orders_on_close=True, max_bars_back=120)
fast_period = input.int(12, title="Fast EMA", key="fast_period")
slow_period = input.int(26, title="Slow EMA", key="slow_period")
atr_length = input.int(14, title="ATR Length", key="atr_length")
sl_atr = input.float(1.5, title="SL ATR", key="sl_atr")
tp_atr = input.float(3.0, title="TP ATR", key="tp_atr")
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty")


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    p = {
        "fast_period": int(fast_period),
        "slow_period": int(slow_period),
        "atr_length": int(atr_length),
        "trade_qty": float(trade_qty),
        "sl_atr": float(sl_atr),
        "tp_atr": float(tp_atr),
    } | dict(params or {})
    ema_fast = ta.ema(frame["close"], int(p["fast_period"]))
    ema_slow = ta.ema(frame["close"], int(p["slow_period"]))
    atr_value = ta.atr(frame, int(p["atr_length"]))
    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["atr"] = atr_value
    frame["buy_signal"] = ta.crossover(ema_fast, ema_slow).fillna(False)
    frame["sell_signal"] = ta.crossunder(ema_fast, ema_slow).fillna(False)
    frame["mapped_entry_side"] = np.where(frame["buy_signal"], "BUY", np.where(frame["sell_signal"], "SELL", ""))
    frame["mapped_entry_price"] = frame["open"]
    frame["mapped_quantity"] = float(p.get("trade_qty", 0.0) or 0.0)
    frame["mapped_size_pct"] = 0.0
    # Bracket exits are strategy intent, so mapped_sl and mapped_tp are emitted here.
    frame["mapped_sl"] = np.where(
        frame["mapped_entry_side"] == "BUY",
        frame["mapped_entry_price"] - (frame["atr"] * float(p["sl_atr"])),
        np.where(frame["mapped_entry_side"] == "SELL", frame["mapped_entry_price"] + (frame["atr"] * float(p["sl_atr"])), 0.0),
    )
    frame["mapped_tp"] = np.where(
        frame["mapped_entry_side"] == "BUY",
        frame["mapped_entry_price"] + (frame["atr"] * float(p["tp_atr"])),
        np.where(frame["mapped_entry_side"] == "SELL", frame["mapped_entry_price"] - (frame["atr"] * float(p["tp_atr"])), 0.0),
    )
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    # Mapping remains thin after bracket fields are prepared.
    return build_mapped_trade_frame(signal_df)
