from pathlib import Path
import json

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "features" / "parks_difficulty.csv"


def parse_json_column(value):
    if not value:
        return []

    try:
        return json.loads(value)
    except Exception:
        return []


def get_parks(page: int = 1, page_size: int = 20):
    df = pd.read_csv(DATA_PATH, keep_default_na=False)

    df = df.reset_index()

    df = df.rename(
        columns={
            "index": "id",
            "avg_slope": "avgSlope",
            "elevation_diff": "elevationDiff",
            "pet_status": "petStatus",
            "pet_restricted_locations": "petRestrictedLocations",
            "service_animal_allowed": "serviceAnimalAllowed",
        }
    )

    df["petRestrictedLocations"] = df["petRestrictedLocations"].apply(parse_json_column)

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
            "petStatus",
            "petRestrictedLocations",
            "serviceAnimalAllowed",
        ]
    ]

    total = len(df)

    start = (page - 1) * page_size
    end = start + page_size

    items = df.iloc[start:end].to_dict(orient="records")

    return {
        "items": items,
        "page": page,
        "pageSize": page_size,
        "total": total,
        "totalPages": (total + page_size - 1) // page_size,
    }
