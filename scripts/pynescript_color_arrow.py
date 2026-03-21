# @name: pynescript_color_arrow
import pandas as pd

from source.gui.scripts_editor.pynescript_runtime import indicator


indicator("Pyne Color Arrow", overlay=True, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["visual_x"] = pd.to_numeric(frame.get("index", pd.Series(dtype=float)), errors="coerce").fillna(0.0)
    bullish = pd.to_numeric(frame.get("close", pd.Series(dtype=float)), errors="coerce").fillna(0.0) >= pd.to_numeric(
        frame.get("open", pd.Series(dtype=float)),
        errors="coerce",
    ).fillna(0.0)
    frame["visual_y"] = pd.to_numeric(
        pd.Series(
            [low if is_bullish else high for low, high, is_bullish in zip(frame.get("low", []), frame.get("high", []), bullish.tolist())],
            index=frame.index,
        ),
        errors="coerce",
    ).fillna(0.0)
    frame["visual_direction"] = bullish.map(lambda value: "up" if bool(value) else "down")
    frame["visual_color"] = bullish.map(lambda value: "#FF0000" if bool(value) else "#00FF00")
    frame["visual_size"] = 15
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    return ctx.atk.color_arrow(
        key="support_resistance_arrows",
        x=frame.get("visual_x", pd.Series(dtype=float)).tolist(),
        y=frame.get("visual_y", pd.Series(dtype=float)).tolist(),
        directions=frame.get("visual_direction", pd.Series(dtype=object)).astype(str).tolist(),
        colors=frame.get("visual_color", pd.Series(dtype=object)).astype(str).tolist(),
        sizes=pd.to_numeric(frame.get("visual_size", pd.Series(dtype=float)), errors="coerce").fillna(15).astype(int).tolist(),
    )
