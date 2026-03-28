# @name: pynescript_input_interactions_indicator
# Docs: function-cookbook.html#input-recipes
# Docs: examples-copybook.html#input-interactions
import pandas as pd

from source import indicator, input, plot, ta


indicator("Pyne Input Interactions Indicator", overlay=True, max_bars_back=240)

# These inputs demonstrate the extended input family that the runtime preserves
# in module metadata for the editor, publishing, and chart-pick flows.
notes = input.text_area("Watch for pullbacks near the trigger zone.", title="Notes", key="notes", group="notes")
source_type = input.source("close", title="Source", key="source_type", group="core")
confirm_tf = input.timeframe("15m", title="Confirm TF", key="confirm_tf", group="core")
trigger_time = input.time(1700000000000, title="Trigger Time", key="trigger_time", confirm=True, group="anchor", inline="anchor")
trigger_price = input.price(101.25, title="Trigger Price", key="trigger_price", minval=0.0, step=0.25, group="anchor", inline="anchor")
ticker = input.symbol("BINANCE:BTCUSDT", title="Ticker", key="ticker", group="context")
session_value = input.session("0930-1600", title="Session", key="session_value", group="context")
accent_color = input.color("#2962ff", title="Accent", key="accent_color", group="styles")
mode = input.enum("slow", title="Mode", key="mode", options=["fast", "slow", "auto"], group="core")

plot("basis", key="basis_line", title="Basis", color="#2962ff", width=2)
plot("trigger_level", key="trigger_level", title="Trigger", color="#ff6d00", style="linebr")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "source_type": str(source_type),
        "confirm_tf": str(confirm_tf),
        "trigger_time": int(trigger_time),
        "trigger_price": float(trigger_price),
        "ticker": str(ticker),
        "session_value": str(session_value),
        "accent_color": str(accent_color),
        "mode": str(mode),
        "notes": str(notes),
    } | dict(params or {})

    source_name = str(merged.get("source_type", "close") or "close")
    source_series = frame[source_name] if source_name in frame.columns else frame["close"]
    length_map = {"fast": 8, "slow": 21, "auto": 34}
    basis_length = int(length_map.get(str(merged.get("mode", "slow") or "slow"), 21))

    frame["basis"] = ta.ema(source_series, basis_length)
    frame["trigger_level"] = float(merged.get("trigger_price", trigger_price) or trigger_price)
    frame["distance_to_trigger"] = frame["close"] - frame["trigger_level"]

    # attrs is used here only for static descriptive metadata.
    frame.attrs["input_interactions_summary"] = {
        "ticker": str(merged.get("ticker", ticker) or ticker),
        "confirm_tf": str(merged.get("confirm_tf", confirm_tf) or confirm_tf),
        "session_value": str(merged.get("session_value", session_value) or session_value),
        "notes": str(merged.get("notes", notes) or notes),
    }
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    if frame is None or frame.empty or ctx is None:
        return None

    merged = {
        "trigger_price": float(trigger_price),
        "accent_color": str(accent_color),
        "mode": str(mode),
        "confirm_tf": str(confirm_tf),
    } | dict(params or {})

    first_index = int(frame.iloc[0]["index"])
    last_index = int(frame.iloc[-1]["index"])
    trigger_level = float(frame["trigger_level"].iloc[-1])
    basis_value = float(frame["basis"].iloc[-1]) if pd.notna(frame["basis"].iloc[-1]) else trigger_level

    # Dynamic x/y values come from the current frame slice, not attrs.
    ctx.line.new(
        key="picked_trigger_line",
        x1=first_index,
        y1=trigger_level,
        x2=last_index,
        y2=trigger_level,
        color=str(merged.get("accent_color", accent_color) or accent_color),
        width=2,
    )
    return ctx.label.new(
        key="input_mode_label",
        x=last_index,
        y=basis_value,
        text=f"{str(merged.get('mode', mode) or mode).upper()} @ {str(merged.get('confirm_tf', confirm_tf) or confirm_tf)}",
        style="label_down",
        color=str(merged.get("accent_color", accent_color) or accent_color),
        textcolor="#ffffff",
    )