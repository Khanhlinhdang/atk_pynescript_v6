# @name: pynescript_barstate_log_indicator
# Docs: function-cookbook.html#barstate-log-recipes
# Docs: examples-copybook.html#barstate-log
import pandas as pd

from source import barstate, indicator, log, plot, plotshape, ta


indicator("Pyne Barstate Log Indicator", overlay=True, max_bars_back=120)

plot("basis", key="basis_line", title="Basis", color="#2962ff", width=2)
plotshape("first_bar_marker", key="first_marker", title="First Bar", location="belowbar", style="circle", color="#00c853", text="FIRST")
plotshape("last_bar_marker", key="last_marker", title="Last Bar", location="abovebar", style="diamond", color="#f23645", text="LAST")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.sma(frame["close"], 5)

    simulate_realtime = bool((params or {}).get("simulate_realtime", False))
    total = len(frame)
    first_flags: list[bool] = []
    last_flags: list[bool] = []
    realtime_flags: list[bool] = []
    confirmed_flags: list[bool] = []

    for index in range(total):
        state = barstate.from_index(index, total, is_realtime=simulate_realtime and index == total - 1)
        first_flags.append(bool(state.isfirst))
        last_flags.append(bool(state.islast))
        realtime_flags.append(bool(state.isrealtime))
        confirmed_flags.append(bool(state.isconfirmed))

    frame["first_bar_marker"] = first_flags
    frame["last_bar_marker"] = last_flags
    frame["is_realtime_bar"] = realtime_flags
    frame["is_confirmed_bar"] = confirmed_flags

    if total:
        log.info("barstate example prepared {} bars", total)
        if bool(realtime_flags[-1]):
            log.warning("last bar marked realtime for demo output")

    return frame