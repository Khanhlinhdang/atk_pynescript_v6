# @name: pynescript_matrix_runtime_indicator
import pandas as pd

from source import indicator, input, matrix

indicator("Pyne Matrix Runtime Indicator", overlay=False)
window = input.int(3, title="Window", key="window", minval=1)


def build_indicator_frame(df: pd.DataFrame, params: dict | None = None) -> pd.DataFrame:
    frame = df.copy().reset_index(drop=True)
    merged = {"window": int(window)} | dict(params or {})
    window_size = max(int(merged.get("window", 3) or 3), 1)

    tail = frame.tail(window_size).reset_index(drop=True)
    grid = matrix.new(len(tail), 2, 0.0)
    for row_index, row in tail.iterrows():
        matrix.set(grid, row_index, 0, float(row["open"]))
        matrix.set(grid, row_index, 1, float(row["close"]))
    matrix.add_col(grid, values=(tail["high"] - tail["low"]).astype(float).tolist())

    frame["matrix_open_sum"] = float(sum(matrix.col(grid, 0))) if matrix.rows(grid) > 0 else 0.0
    frame["matrix_close_sum"] = float(sum(matrix.col(grid, 1))) if matrix.rows(grid) > 0 else 0.0
    frame["matrix_range_sum"] = float(sum(matrix.col(grid, 2))) if matrix.rows(grid) > 0 else 0.0
    frame.attrs["matrix_shape"] = {"rows": matrix.rows(grid), "columns": matrix.columns(grid)}
    frame.attrs["matrix_last_row"] = matrix.row(grid, matrix.rows(grid) - 1) if matrix.rows(grid) > 0 else []
    return frame