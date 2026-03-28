# @name: pynescript_atk_table_bridge
import pandas as pd

from source import indicator, ta


indicator("Pyne ATK Table Bridge", overlay=True, max_bars_back=200)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    frame["basis"] = ta.ema(frame["close"], 5)
    if not frame.empty:
        last = frame.iloc[-1]
        frame.attrs["visual_table_payload"] = {
            "position": "top-left",
            "title": "ATK Bridge",
            "columns": 2,
            "rows": 2,
            "cells": [
                {"column": 0, "row": 0, "text": "Metric", "text_color": "#ffffff", "bgcolor": "#0f172a"},
                {"column": 1, "row": 0, "text": "Value", "text_color": "#ffffff", "bgcolor": "#0f172a"},
                {"column": 0, "row": 1, "text": "Close"},
                {"column": 1, "row": 1, "text": f"{float(last['close']):.2f}", "text_color": "#00c853"},
            ],
        }
    else:
        frame.attrs["visual_table_payload"] = {}
    return frame


def build_visuals(frame: pd.DataFrame, params: dict | None = None, ctx=None):
    payload = dict(frame.attrs.get("visual_table_payload") or {})
    if not payload:
        return None
    return ctx.atk.table(
        key="atk_dashboard",
        **payload,
    )