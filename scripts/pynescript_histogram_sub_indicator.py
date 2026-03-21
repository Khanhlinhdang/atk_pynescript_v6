# @name: pynescript_histogram_sub_indicator
import pandas as pd

from source.controls.pandas_ta.momentum import squeeze
from source.gui.scripts_editor.pynescript_runtime import indicator, input, hline


indicator("Pyne Squeeze Histogram", overlay=False, max_bars_back=320)
bb_length = input.int(20, title="BB Length", key="bb_length")
bb_std = input.float(2.0, title="BB Std", key="bb_std")
kc_length = input.int(20, title="KC Length", key="kc_length")
kc_scalar = input.float(1.5, title="KC Scalar", key="kc_scalar")
mom_length = input.int(12, title="Momentum Length", key="mom_length")
mom_smooth = input.int(6, title="Momentum Smooth", key="mom_smooth")
hline(0, key="sqz_zero", title="Zero", color="#666666")


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {
        "bb_length": int(bb_length),
        "bb_std": float(bb_std),
        "kc_length": int(kc_length),
        "kc_scalar": float(kc_scalar),
        "mom_length": int(mom_length),
        "mom_smooth": int(mom_smooth),
    } | dict(params or {})
    sqz = squeeze(
        close=frame["close"],
        high=frame["high"],
        low=frame["low"],
        bb_length=max(int(merged.get("bb_length", 20) or 20), 1),
        bb_std=float(merged.get("bb_std", 2.0) or 2.0),
        kc_length=max(int(merged.get("kc_length", 20) or 20), 1),
        kc_scalar=float(merged.get("kc_scalar", 1.5) or 1.5),
        mom_length=max(int(merged.get("mom_length", 12) or 12), 1),
        mom_smooth=max(int(merged.get("mom_smooth", 6) or 6), 1),
        mamode="sma",
        use_tr=True,
        lazybear=True,
        detailed=False,
    )
    sqz_column = next((col for col in sqz.columns if str(col).startswith("SQZ")), None)
    frame["squeeze"] = pd.to_numeric(sqz.get(sqz_column), errors="coerce") if sqz_column else float("nan")
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    colors = ["#089981" if float(value) >= 0 else "#f23645" for value in frame["squeeze"].fillna(0.0).tolist()]
    return ctx.atk.histogram(
        key="squeeze_histogram",
        x=frame["index"].tolist(),
        y=frame["squeeze"].fillna(0.0).tolist(),
        colors=colors,
    )
