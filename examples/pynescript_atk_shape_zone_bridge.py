# @name: pynescript_atk_shape_zone_bridge
import pandas as pd

from source import Location, Position, Shape
from source import indicator, ta


indicator("Pyne ATK Shape Zone Bridge", overlay=True, max_bars_back=320)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.sma(frame["close"], 5)
    tail = frame.tail(3).reset_index(drop=True)
    if len(tail.index) >= 3:
        last = tail.iloc[-1]
        prev = tail.iloc[-2]
        first = tail.iloc[0]
        frame.attrs["visual_shape_zone_payload"] = {
            "shape_text": {
                "points": [(float(last["index"]), float(last["close"]))],
                "shapes": [Shape.ArrowUp],
                "shape_sizes": [12.0],
                "shape_colors": ["#2962ff"],
                "texts": ["LONG"],
                "text_sizes": [9.0],
                "text_colors": ["#ffffff"],
                "fonts": ["Arial"],
                "weights": [500],
                "locations": [Location.Above],
                "positions": [Position.AboveBar],
            },
            "polyline": {
                "points": [
                    (float(first["index"]), float(first["close"])),
                    (float(prev["index"]), float(prev["high"])),
                    (float(last["index"]), float(last["close"])),
                ],
                "line_color": "#ffd600",
                "line_width": 1.0,
                "show_points": True,
            },
            "rectangles": {
                "data": {
                    "rectangles": [
                        (
                            float(prev["index"]),
                            float(prev["low"] - 0.2),
                            float(last["index"]),
                            float(last["high"] + 0.2),
                        )
                    ],
                    "line_colors": ["#00c853"],
                    "line_widths": [1.0],
                    "fill_colors": ["#00c853"],
                    "fill_alphas": [26],
                },
            },
            "rectangle_ray": {
                "x": float(prev["index"]),
                "h1": float(prev["low"] - 0.3),
                "h2": float(last["high"] + 0.3),
                "border_color": "#ff6d00",
                "fill_color": "#ff6d00",
                "border_width": 1,
            },
        }
    else:
        frame.attrs["visual_shape_zone_payload"] = {}
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    payload = dict(frame.attrs.get("visual_shape_zone_payload") or {})
    if not payload:
        return []
    return [
        ctx.atk.shape_text(
            key="atk_shape_marks",
            **dict(payload.get("shape_text") or {}),
        ),
        ctx.atk.polyline(
            key="atk_polyline_path",
            **dict(payload.get("polyline") or {}),
        ),
        ctx.atk.rectangles(
            key="atk_rectangles_zone",
            **dict(payload.get("rectangles") or {}),
        ),
        ctx.atk.rectangle_ray(
            key="atk_rectangle_ray_zone",
            **dict(payload.get("rectangle_ray") or {}),
        ),
    ]