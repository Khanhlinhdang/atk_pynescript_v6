# @name: pynescript_smc_ict
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator, input, ta


indicator("Pyne SMC ICT", overlay=True, max_bars_back=1500)
look_back_bar = input.int(300, title="Look Back Bars", key="look_back_bar")
min_confluence = input.int(2, title="Min Confluence", key="min_confluence")


def _safe_bool_count(series: pd.Series | None) -> int:
    if series is None:
        return 0
    return int(pd.Series(series).fillna(False).astype(bool).sum())


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "look_back_bar": int(look_back_bar),
        "min_confluence": int(min_confluence),
    } | dict(params or {})

    lookback = max(int(merged.get("look_back_bar", len(frame)) or len(frame)), 20)
    if len(frame) > lookback:
        frame = frame.tail(lookback).reset_index(drop=True)

    frame["ema_fast"] = ta.ema(frame["close"], 9)
    frame["ema_slow"] = ta.ema(frame["close"], 21)
    frame["bias_up"] = (frame["ema_fast"] > frame["ema_slow"]).fillna(False)
    frame["bos_signal"] = ta.crossover(frame["ema_fast"], frame["ema_slow"]).fillna(False)
    frame["choch_signal"] = ta.crossunder(frame["ema_fast"], frame["ema_slow"]).fillna(False)

    rolling_window = max(int(merged.get("min_confluence", 2) or 2) * 8, 8)
    frame["swing_high"] = frame["high"].eq(frame["high"].rolling(rolling_window, min_periods=1).max()).fillna(False)
    frame["swing_low"] = frame["low"].eq(frame["low"].rolling(rolling_window, min_periods=1).min()).fillna(False)
    frame["premium_top"] = frame["high"].rolling(rolling_window, min_periods=1).max()
    frame["discount_bottom"] = frame["low"].rolling(rolling_window, min_periods=1).min()
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    if frame is None or frame.empty or ctx is None:
        return None

    summary_panel = ctx.panel("smc_ict_summary", title="SMC ICT Summary", placement="sub", preferred_height=150)
    last = frame.iloc[-1]
    bos_count = _safe_bool_count(frame.get("bos_signal"))
    choch_count = _safe_bool_count(frame.get("choch_signal"))
    swing_high_count = _safe_bool_count(frame.get("swing_high"))
    swing_low_count = _safe_bool_count(frame.get("swing_low"))
    market_bias = "Bullish" if bool(last.get("bias_up", False)) else "Bearish"

    return [
        ctx.table.new(summary_panel, 2, 4, key="smc_ict_dashboard", title="SMC ICT"),
        ctx.atk.table(
            key="smc_ict_bridge_table",
            panel="smc_ict_summary",
            position="top-left",
            title="SMC ICT",
            columns=2,
            rows=4,
            cells=[
                {"column": 0, "row": 0, "text": "Bias", "bgcolor": "#0f172a", "text_color": "#ffffff"},
                {"column": 1, "row": 0, "text": market_bias, "text_color": "#00c853" if market_bias == "Bullish" else "#f23645"},
                {"column": 0, "row": 1, "text": "BOS"},
                {"column": 1, "row": 1, "text": str(bos_count)},
                {"column": 0, "row": 2, "text": "CHOCH"},
                {"column": 1, "row": 2, "text": str(choch_count)},
                {"column": 0, "row": 3, "text": "Swings"},
                {"column": 1, "row": 3, "text": f"{swing_high_count}/{swing_low_count}"},
            ],
        ),
    ]