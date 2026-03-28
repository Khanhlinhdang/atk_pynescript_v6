from source import indicator, input, request


indicator("Pyne Request Seed Runtime Indicator", overlay=False)

seed_window = input.int(4, title="Seed Window", key="seed_window", minval=2)


def build_indicator_frame(df, params=None):
    frame = df.copy().reset_index(drop=True)
    window = max(int((params or {}).get("seed_window", seed_window) or seed_window), 2)

    seeded_source = {
        "seeded_close": frame["close"].rolling(window, min_periods=1).mean().round(4).tolist(),
        "seeded_bias": ["bullish" if close_value >= open_value else "bearish" for open_value, close_value in zip(frame["open"], frame["close"])],
    }

    frame["seeded_close"] = request.seed(seeded_source, "seeded_close")
    frame["seeded_bias"] = request.seed(seeded_source, "seeded_bias")
    frame["seeded_gap"] = frame["close"] - frame["seeded_close"]

    frame.attrs["seed_source_kind"] = "inline"
    frame.attrs["seed_window"] = window
    frame.attrs["seed_last_bias"] = str(frame["seeded_bias"].iloc[-1]) if not frame.empty else ""
    return frame