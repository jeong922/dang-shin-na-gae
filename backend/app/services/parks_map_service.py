from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "features" / "parks_difficulty.csv"


def get_map_parks():
    df = pd.read_csv(DATA_PATH)

    df = df.reset_index()

    df = df.rename(
        columns={
            "index": "id",
            "avg_slope": "avgSlope",
            "elevation_diff": "elevationDiff",
        }
    )

    df = df[
        [
            "id",
            "name",
            "lat",
            "lon",
            "difficulty",
            "avgSlope",
            "elevationDiff",
            "area",
            "district",
        ]
    ]

    return df.to_dict(orient="records")
