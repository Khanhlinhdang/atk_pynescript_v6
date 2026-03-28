# @name: pynescript_strategy_intent_surface
# Docs: function-cookbook.html#strategy-intent-recipes
# Docs: examples-copybook.html#strategy-intent-surface
import pandas as pd

from source import build_mapped_trade_frame, input, strategy, ta


strategy("Pyne Strategy Intent Surface", overlay=True, process_orders_on_close=True)
fast_length = input.int(8, title="Fast EMA", key="fast_length", minval=1)
slow_length = input.int(21, title="Slow EMA", key="slow_length", minval=2)
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty", minval=0.0)

# These helpers are supported as explicit payload builders.
# The canonical ATK execution path for strategies still uses canonical trade-frame fields.
ENTRY_TEMPLATE = strategy.entry("L", "BUY", when=True, limit=100.0, comment="entry-template")
ORDER_TEMPLATE = strategy.order("S", "SELL", when=True, stop=99.0, comment="order-template")
EXIT_TEMPLATE = strategy.exit("LX", from_entry="L", when=True, stop=98.0, limit=105.0)
CLOSE_TEMPLATE = strategy.close("L", when=True, comment="close-template")
CLOSE_ALL_TEMPLATE = strategy.close_all(when=True, comment="close-all-template")
CANCEL_TEMPLATE = strategy.cancel("L", when=True)
CANCEL_ALL_TEMPLATE = strategy.cancel_all(when=True)


def build_signal_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "fast_length": int(fast_length),
        "slow_length": int(slow_length),
        "trade_qty": float(trade_qty),
    } | dict(params or {})

    fast = max(int(merged.get("fast_length", fast_length) or fast_length), 1)
    slow = max(int(merged.get("slow_length", slow_length) or slow_length), fast + 1)
    quantity = float(merged.get("trade_qty", trade_qty) or trade_qty)

    frame["ema_fast"] = ta.ema(frame["close"], fast)
    frame["ema_slow"] = ta.ema(frame["close"], slow)
    frame["buy_signal"] = ta.crossover(frame["ema_fast"], frame["ema_slow"]).fillna(False)
    frame["sell_signal"] = ta.crossunder(frame["ema_fast"], frame["ema_slow"]).fillna(False)

    frame["entry_side"] = ""
    frame.loc[frame["buy_signal"], "entry_side"] = "BUY"
    frame.loc[frame["sell_signal"], "entry_side"] = "SELL"
    frame["entry_price"] = frame["open"]
    frame["quantity"] = quantity
    frame["size_pct"] = 0.0

    frame.attrs["intent_surface_examples"] = {
        "entry": dict(ENTRY_TEMPLATE or {}),
        "order": dict(ORDER_TEMPLATE or {}),
        "exit": dict(EXIT_TEMPLATE or {}),
        "close": dict(CLOSE_TEMPLATE or {}),
        "close_all": dict(CLOSE_ALL_TEMPLATE or {}),
        "cancel": dict(CANCEL_TEMPLATE or {}),
        "cancel_all": dict(CANCEL_ALL_TEMPLATE or {}),
    }
    return frame


def build_trade_frame(signal_df: pd.DataFrame, params: dict | None = None, styles: dict | None = None) -> pd.DataFrame:
    return build_mapped_trade_frame(signal_df)