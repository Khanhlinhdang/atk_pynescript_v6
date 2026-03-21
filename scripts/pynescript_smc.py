# @name: pynescript_smc
import warnings

import numpy as np
import pandas as pd

from source.controls.smc.smc_joshua import smc as _smc
from source.gui.scripts_editor.pynescript_runtime import indicator, input, plot, plotshape
from source.help_importer import Location, Weight


indicator(
    "SMC - Joshua Attridge",
    overlay=True,
    max_bars_back=2000,
    default_styles={
        "pen_highcolor": "#f23645",
        "pen_lowcolor": "#089981",
    },
)
look_back_bar = input.int(1000, title="Look Back Bars", key="look_back_bar")
swing_length = input.int(5, title="Swing Length", key="swing_length")
show_fvg = input.bool(True, title="Show FVG", key="show_fvg")
show_bos_choch = input.bool(True, title="Show BOS/CHOCH", key="show_bos_choch")
show_ob = input.bool(True, title="Show OB", key="show_ob")
show_liquidity = input.bool(True, title="Show Liquidity", key="show_liquidity")

def _empty_smc_frame(length_hint: int) -> pd.DataFrame:
    n_rows = max(int(length_hint or 0), 0)
    return pd.DataFrame(
        {
            "index": list(range(n_rows)),
            "FVG": [np.nan] * n_rows,
            "FVGTop": [np.nan] * n_rows,
            "FVGBottom": [np.nan] * n_rows,
            "FVGMitigatedIndex": [np.nan] * n_rows,
            "SWHighLow": [np.nan] * n_rows,
            "SWLevel": [np.nan] * n_rows,
            "BOS": [np.nan] * n_rows,
            "CHOCH": [np.nan] * n_rows,
            "BCHLevel": [np.nan] * n_rows,
            "BCHBrokenIndex": [np.nan] * n_rows,
            "OB": [np.nan] * n_rows,
            "OBTop": [np.nan] * n_rows,
            "OBBottom": [np.nan] * n_rows,
            "OBVolume": [np.nan] * n_rows,
            "OBMitigatedIndex": [np.nan] * n_rows,
            "OBPercentage": [np.nan] * n_rows,
            "Liquidity": [np.nan] * n_rows,
            "LQLevel": [np.nan] * n_rows,
            "LQEnd": [np.nan] * n_rows,
            "LQSwept": [np.nan] * n_rows,
        }
    )


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    if not isinstance(df, pd.DataFrame) or df.empty:
        return _empty_smc_frame(0)

    merged = {
        "look_back_bar": int(look_back_bar),
        "swing_length": int(swing_length),
    } | dict(params or {})

    window = df.copy().reset_index(drop=True)
    look_back = max(int(merged.get("look_back_bar", len(window)) or len(window)), 1)
    if len(window) > look_back:
        window = window.tail(look_back).reset_index(drop=True)

    required_cols = ["open", "high", "low", "close", "volume"]
    missing_cols = [column for column in required_cols if column not in window.columns]
    if missing_cols:
        raise ValueError(f"SMC example requires OHLCV columns: missing {missing_cols}")

    current_swing_length = max(int(merged.get("swing_length", 5) or 5), 1)
    if len(window) < current_swing_length * 2:
        warnings.warn("Dataset is shorter than requested swing length window; reducing swing_length for Pyne SMC example")
        current_swing_length = max(1, len(window) // 4)

    indicators_data: list[pd.DataFrame] = [window[["index"]].reset_index(drop=True)]

    try:
        indicators_data.append(_smc.fvg(window, join_consecutive=True).reset_index(drop=True))
    except Exception:
        indicators_data.append(_empty_smc_frame(len(window))[["FVG", "FVGTop", "FVGBottom", "FVGMitigatedIndex"]])

    try:
        swing_data = _smc.swing_highs_lows(window, swing_length=current_swing_length).reset_index(drop=True)
    except Exception:
        swing_data = _empty_smc_frame(len(window))[["SWHighLow", "SWLevel"]]
    indicators_data.append(swing_data)

    try:
        indicators_data.append(_smc.bos_choch(window, swing_data).reset_index(drop=True))
    except Exception:
        indicators_data.append(_empty_smc_frame(len(window))[["BOS", "CHOCH", "BCHLevel", "BCHBrokenIndex"]])

    try:
        indicators_data.append(_smc.ob(window, swing_data).reset_index(drop=True))
    except Exception:
        indicators_data.append(
            _empty_smc_frame(len(window))[["OB", "OBTop", "OBBottom", "OBVolume", "OBMitigatedIndex", "OBPercentage"]]
        )

    try:
        indicators_data.append(_smc.liquidity(window, swing_data).reset_index(drop=True))
    except Exception:
        indicators_data.append(_empty_smc_frame(len(window))[["Liquidity", "LQLevel", "LQEnd", "LQSwept"]])

    frame = pd.concat(indicators_data, axis=1, ignore_index=False)
    swing_values = pd.to_numeric(frame.get("SWHighLow"), errors="coerce")
    frame["swing_high_signal"] = swing_values.gt(0).fillna(False)
    frame["swing_low_signal"] = swing_values.lt(0).fillna(False)
    frame["__smc_anchor__"] = np.nan
    return frame


def _merged_params(params: dict | None = None) -> dict:
    return {
        "look_back_bar": int(look_back_bar),
        "swing_length": int(swing_length),
        "show_fvg": bool(show_fvg),
        "show_bos_choch": bool(show_bos_choch),
        "show_ob": bool(show_ob),
        "show_liquidity": bool(show_liquidity),
    } | dict(params or {})


def _resolve_chart_index(frame: pd.DataFrame, position_value, last_index: int) -> int:
    if pd.isna(position_value) or int(position_value or 0) == 0:
        return int(last_index)
    length = len(frame)
    offset = int(position_value)
    if offset < 0:
        return int(last_index)
    if offset >= length:
        return int(last_index)
    return int(pd.to_numeric(frame["index"], errors="coerce").fillna(last_index).iloc[offset])


def _pair_data(frame: pd.DataFrame) -> dict[str, dict[int, dict]]:
    length = len(frame)
    dict_data = {
        "FVG": {},
        "BOS": {},
        "CHOCH": {},
        "OB": {},
        "Liquidity": {},
    }
    if length == 0:
        return dict_data

    last_index = int(pd.to_numeric(frame["index"], errors="coerce").fillna(0).iloc[-1])
    all_index_vals = pd.to_numeric(frame["index"], errors="coerce").fillna(last_index).to_numpy()

    fvg_mask = ~pd.isna(frame["FVG"]) if "FVG" in frame.columns else pd.Series([], dtype=bool)
    if getattr(fvg_mask, "any", lambda: False)():
        fvg_df = frame[fvg_mask]
        idx_vals = pd.to_numeric(fvg_df["index"], errors="coerce").fillna(0).to_numpy()
        fvg_vals = pd.to_numeric(fvg_df["FVG"], errors="coerce").to_numpy()
        top_vals = pd.to_numeric(fvg_df["FVGTop"], errors="coerce").to_numpy()
        bottom_vals = pd.to_numeric(fvg_df["FVGBottom"], errors="coerce").to_numpy()
        mitigated_vals = pd.to_numeric(fvg_df["FVGMitigatedIndex"], errors="coerce").to_numpy()
        for i in range(len(idx_vals)):
            x = int(idx_vals[i])
            mitigated_index = mitigated_vals[i]
            if pd.isna(mitigated_index) or mitigated_index == 0:
                x1 = last_index
                top = float(top_vals[i])
                bottom = float(bottom_vals[i])
                dict_data["FVG"][x] = {
                    "x": x,
                    "x1": x1,
                    "fvg": float(fvg_vals[i]),
                    "top": top,
                    "bottom": bottom,
                    "mid_x": round((x + x1) / 2),
                    "mid_y": (top + bottom) / 2,
                }
            else:
                _length = int(mitigated_index)
                _ = int(all_index_vals[_length]) if _length < length else last_index

    bos_mask = ~pd.isna(frame["BOS"]) if "BOS" in frame.columns else pd.Series([], dtype=bool)
    if getattr(bos_mask, "any", lambda: False)():
        bos_df = frame[bos_mask]
        idx_vals = pd.to_numeric(bos_df["index"], errors="coerce").fillna(0).to_numpy()
        bos_vals = pd.to_numeric(bos_df["BOS"], errors="coerce").to_numpy()
        level_vals = pd.to_numeric(bos_df["BCHLevel"], errors="coerce").to_numpy()
        broken_vals = pd.to_numeric(bos_df["BCHBrokenIndex"], errors="coerce").to_numpy()
        for i in range(len(idx_vals)):
            x = int(idx_vals[i])
            broken_index = broken_vals[i]
            _length = (length - 1) if (pd.isna(broken_index) or broken_index == 0) else int(broken_index)
            x1 = int(all_index_vals[_length]) if _length < length else last_index
            bos_value = float(bos_vals[i])
            level = float(level_vals[i])
            dict_data["BOS"][x] = {
                "x": x,
                "x1": x1,
                "bos": bos_value,
                "y": level,
                "location": Location.Below if bos_value > 0 else Location.Above,
                "value": bos_value,
                "mid_x": round((x + x1) / 2),
                "mid_y": level,
            }

    choch_mask = ~pd.isna(frame["CHOCH"]) if "CHOCH" in frame.columns else pd.Series([], dtype=bool)
    if getattr(choch_mask, "any", lambda: False)():
        choch_df = frame[choch_mask]
        idx_vals = pd.to_numeric(choch_df["index"], errors="coerce").fillna(0).to_numpy()
        choch_vals = pd.to_numeric(choch_df["CHOCH"], errors="coerce").to_numpy()
        level_vals = pd.to_numeric(choch_df["BCHLevel"], errors="coerce").to_numpy()
        broken_vals = pd.to_numeric(choch_df["BCHBrokenIndex"], errors="coerce").to_numpy()
        for i in range(len(idx_vals)):
            x = int(idx_vals[i])
            broken_index = broken_vals[i]
            _length = (length - 1) if (pd.isna(broken_index) or broken_index == 0) else int(broken_index)
            x1 = int(all_index_vals[_length]) if _length < length else last_index
            choch_value = float(choch_vals[i])
            level = float(level_vals[i])
            dict_data["CHOCH"][x] = {
                "x": x,
                "x1": x1,
                "choch": choch_value,
                "y": level,
                "location": Location.Below if choch_value > 0 else Location.Above,
                "value": choch_value,
                "mid_x": round((x + x1) / 2),
                "mid_y": level,
            }

    ob_mask = ~pd.isna(frame["OB"]) if "OB" in frame.columns else pd.Series([], dtype=bool)
    if getattr(ob_mask, "any", lambda: False)():
        ob_df = frame[ob_mask]
        idx_vals = pd.to_numeric(ob_df["index"], errors="coerce").fillna(0).to_numpy()
        ob_vals = pd.to_numeric(ob_df["OB"], errors="coerce").to_numpy()
        bottom_vals = pd.to_numeric(ob_df["OBBottom"], errors="coerce").to_numpy()
        top_vals = pd.to_numeric(ob_df["OBTop"], errors="coerce").to_numpy()
        mitigated_vals = pd.to_numeric(ob_df["OBMitigatedIndex"], errors="coerce").to_numpy()
        for i in range(len(idx_vals)):
            x = int(idx_vals[i])
            mitigated_index = mitigated_vals[i]
            if pd.isna(mitigated_index) or mitigated_index == 0:
                _length = length - 1
                x1 = int(all_index_vals[_length]) if _length < length else last_index
                top = float(top_vals[i])
                bottom = float(bottom_vals[i])
                dict_data["OB"][x] = {
                    "x": x,
                    "x1": x1,
                    "ob": float(ob_vals[i]),
                    "bottom": bottom,
                    "top": top,
                    "mid_x": round((x + x1) / 2),
                    "mid_y": top,
                }
            else:
                _length = int(mitigated_index)
                _ = int(all_index_vals[_length]) if _length < length else last_index

    liquidity_mask = ~pd.isna(frame["Liquidity"]) if "Liquidity" in frame.columns else pd.Series([], dtype=bool)
    if getattr(liquidity_mask, "any", lambda: False)():
        liquidity_df = frame[liquidity_mask]
        idx_vals = pd.to_numeric(liquidity_df["index"], errors="coerce").fillna(0).to_numpy()
        liq_vals = pd.to_numeric(liquidity_df["Liquidity"], errors="coerce").to_numpy()
        level_vals = pd.to_numeric(liquidity_df["LQLevel"], errors="coerce").to_numpy()
        end_vals = pd.to_numeric(liquidity_df["LQEnd"], errors="coerce").to_numpy()
        has_swept = "LQSwept" in frame.columns
        swept_vals = pd.to_numeric(liquidity_df["LQSwept"], errors="coerce").to_numpy() if has_swept else None
        for i in range(len(idx_vals)):
            x = int(idx_vals[i])
            end_index = end_vals[i]
            _length = (length - 1) if (pd.isna(end_index) or end_index == 0) else int(end_index)
            x1 = int(all_index_vals[_length]) if _length < length else last_index
            swept = swept_vals[i] if swept_vals is not None else 0
            dict_data["Liquidity"][x] = {
                "x": x,
                "x1": x1,
                "liquidity": float(liq_vals[i]),
                "level": float(level_vals[i]),
                "swept": (not pd.isna(swept) and swept != 0),
                "mid_x": round((x + x1) / 2),
                "mid_y": float(level_vals[i]),
            }
    return dict_data


def _pair_data_filtered(frame: pd.DataFrame, params: dict | None = None) -> dict[str, dict[int, dict]]:
    data = _pair_data(frame)
    merged = _merged_params(params)
    if not merged.get("show_fvg", True):
        data["FVG"] = {}
    if not merged.get("show_bos_choch", True):
        data["BOS"] = {}
        data["CHOCH"] = {}
    if not merged.get("show_ob", True):
        data["OB"] = {}
    if not merged.get("show_liquidity", True):
        data["Liquidity"] = {}
    return data


def _build_line_text_payload(data_dict: dict[int, dict], *, title: str, color: str) -> dict:
    if not data_dict:
        return {}

    points = []
    texts = []
    colors = []
    locations = []
    for items in data_dict.values():
        x0 = items["x"]
        x1 = items["x1"]
        y_value = items["y"]
        points.append(((x0, y_value), (x1, y_value)))
        texts.append(title)
        colors.append(color)
        locations.append(items["location"])
    return {
        "points": points,
        "texts": texts,
        "colors": colors,
        "sizes": [8] * len(points),
        "fonts": ["Arial"] * len(points),
        "weights": [Weight.Normal] * len(points),
        "locations": locations,
    }


def _build_rectangles_payload(data_dict: dict[int, dict], title: str) -> dict:
    if not data_dict:
        return {}

    rectangles = []
    texts = []
    text_colors = []
    text_sizes = []
    text_fonts = []
    text_weights = []
    text_positions = []
    line_colors = []
    line_widths = []
    fill_colors = []
    fill_alphas = []
    text_offsets = []

    for items in data_dict.values():
        x0 = items["x"]
        x1 = items["x1"]
        top_value = items["top"]
        bottom_value = items["bottom"]
        direction = items["ob"] if title == "OB" else items["fvg"]
        color = "#FF5733" if direction > 0 else "#3366FF"
        if title == "OB":
            color = "#FF6B35" if direction > 0 else "#6B35FF"

        rectangles.append((x0, bottom_value, x1, top_value))
        texts.append(title)
        text_colors.append(color)
        text_sizes.append(8)
        text_fonts.append("Arial")
        text_weights.append(Weight.Normal)
        text_positions.append(Location.Inside)
        line_colors.append(color)
        line_widths.append(1)
        fill_colors.append(color)
        fill_alphas.append(60 if title == "OB" else 50)
        text_offsets.append(5)

    return {
        "rectangles": rectangles,
        "texts": texts,
        "text_colors": text_colors,
        "text_sizes": text_sizes,
        "text_fonts": text_fonts,
        "text_weights": text_weights,
        "text_positions": text_positions,
        "line_colors": line_colors,
        "line_widths": line_widths,
        "fill_colors": fill_colors,
        "fill_alphas": fill_alphas,
        "text_offsets": text_offsets,
    }


def _build_liquidity_payload(data_dict: dict[int, dict]) -> dict:
    if not data_dict:
        return {}

    points = []
    texts = []
    colors = []
    locations = []
    for items in data_dict.values():
        x0 = items["x"]
        x1 = items["x1"]
        y_value = items["level"]
        swept = items.get("swept", False)
        liquidity_value = items["liquidity"]
        points.append(((x0, y_value), (x1, y_value)))
        texts.append("LQ Swept" if swept else "LQ")
        colors.append("#808080" if swept else "#FFD700")
        locations.append(Location.Above if liquidity_value > 0 else Location.Below)
    return {
        "points": points,
        "texts": texts,
        "colors": colors,
        "sizes": [8] * len(points),
        "fonts": ["Arial"] * len(points),
        "weights": [Weight.Normal] * len(points),
        "locations": locations,
    }


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    visuals = []
    paired = _pair_data_filtered(frame, params=params)

    choch_payload = _build_line_text_payload(paired.get("CHOCH", {}), title="ChoCh", color="#4FC532") or {
        "points": [],
        "texts": [],
        "colors": [],
        "sizes": [],
        "fonts": [],
        "weights": [],
        "locations": [],
    }
    visuals.append(ctx.atk.color_line_text(key="smc_choch", **choch_payload))

    bos_payload = _build_line_text_payload(paired.get("BOS", {}), title="BOS", color="#C5C332") or {
        "points": [],
        "texts": [],
        "colors": [],
        "sizes": [],
        "fonts": [],
        "weights": [],
        "locations": [],
    }
    visuals.append(ctx.atk.color_line_text(key="smc_bos", **bos_payload))

    fvg_payload = _build_rectangles_payload(paired.get("FVG", {}), "FVG") or {
        "rectangles": [],
        "texts": [],
        "text_colors": [],
        "text_sizes": [],
        "text_fonts": [],
        "text_weights": [],
        "text_positions": [],
        "line_colors": [],
        "line_widths": [],
        "fill_colors": [],
        "fill_alphas": [],
        "text_offsets": [],
    }
    visuals.append(ctx.atk.rectangle_text(key="smc_fvg", **fvg_payload))

    ob_payload = _build_rectangles_payload(paired.get("OB", {}), "OB") or {
        "rectangles": [],
        "texts": [],
        "text_colors": [],
        "text_sizes": [],
        "text_fonts": [],
        "text_weights": [],
        "text_positions": [],
        "line_colors": [],
        "line_widths": [],
        "fill_colors": [],
        "fill_alphas": [],
        "text_offsets": [],
    }
    visuals.append(ctx.atk.rectangle_text(key="smc_ob", **ob_payload))

    liquidity_payload = _build_liquidity_payload(paired.get("Liquidity", {})) or {
        "points": [],
        "texts": [],
        "colors": [],
        "sizes": [],
        "fonts": [],
        "weights": [],
        "locations": [],
    }
    visuals.append(ctx.atk.color_line_text(key="smc_liquidity", **liquidity_payload))

    return visuals
