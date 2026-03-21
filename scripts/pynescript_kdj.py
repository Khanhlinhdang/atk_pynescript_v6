# @name: pynescript_kdj
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator, input, hline, plot, ta

indicator("Pyne KDJ", overlay=False, max_bars_back=320)
length = input.int(9, title="Length", key="length")
signal = input.int(3, title="Signal", key="signal")
plot("k", key="kdj_k_line", title="K", color="#089981", width=1)
plot("d", key="kdj_d_line", title="D", color="#f23645", width=1)
plot("j", key="kdj_j_line", title="J", color="#ffeb3b", width=1)
hline(80, key="kdj_80", title="80", color="#ffffff")
hline(20, key="kdj_20", title="20", color="#ffffff")

def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "length": int(length),
        "signal": int(signal),
    } | dict(params or {})
    k_value, d_value, j_value = ta.kdj(
        frame,
        length=max(int(merged.get("length", 9) or 9), 1),
        signal=max(int(merged.get("signal", 3) or 3), 1),
    )
    frame["k"] = pd.to_numeric(k_value, errors="coerce")
    frame["d"] = pd.to_numeric(d_value, errors="coerce")
    frame["j"] = pd.to_numeric(j_value, errors="coerce")
    return frame
