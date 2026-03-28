from source import build_mapped_trade_frame, input, strategy, strategy_alert_message, ta


strategy("Pyne Strategy Alert Template Strategy", overlay=True, process_orders_on_close=True)
strategy_alert_message(
    "{{ticker}} {{strategy.order.id}} {{strategy.order.action}} {{strategy.market_position}} {{strategy.market_position_size}} {{strategy.prev_market_position}} {{strategy.prev_market_position_size}}"
)

fast_length = input.int(9, title="Fast EMA", key="fast_length", minval=1)
slow_length = input.int(21, title="Slow EMA", key="slow_length", minval=2)
trade_qty = input.float(1.0, title="Trade Qty", key="trade_qty", minval=0.0)


def build_signal_frame(df, params=None):
    frame = df.copy().reset_index(drop=True)
    merged = dict(params or {})
    fast = max(int(merged.get("fast_length", fast_length) or fast_length), 1)
    slow = max(int(merged.get("slow_length", slow_length) or slow_length), fast + 1)
    quantity = float(merged.get("trade_qty", trade_qty) or trade_qty)

    ema_fast = ta.ema(frame["close"], fast)
    ema_slow = ta.ema(frame["close"], slow)
    buy_signal = ta.crossover(ema_fast, ema_slow).fillna(False)
    sell_signal = ta.crossunder(ema_fast, ema_slow).fillna(False)

    frame["ema_fast"] = ema_fast
    frame["ema_slow"] = ema_slow
    frame["buy_signal"] = buy_signal
    frame["sell_signal"] = sell_signal
    frame["entry_side"] = buy_signal.map({True: "BUY", False: ""})
    frame.loc[sell_signal, "entry_side"] = "SELL"
    frame["entry_price"] = frame["open"]
    frame["quantity"] = quantity
    frame["size_pct"] = 0.0
    frame["tag"] = buy_signal.map({True: "EMA-LONG", False: ""})
    frame.loc[sell_signal, "tag"] = "EMA-SHORT"
    frame["symbol"] = "BINANCE:BTCUSDT"
    return frame


def build_trade_frame(signal_df, params=None, styles=None):
    return build_mapped_trade_frame(signal_df)
