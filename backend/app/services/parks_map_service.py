from pathlib import Path
import json
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]
DATA_PATH = BASE_DIR / "data" / "features" / "parks_difficulty.csv"


def parse_json_column(value):
    """
    JSON 문자열 컬럼 변환
    """

    if not value:
        return []

    try:
        return json.loads(value)

    except Exception:
        return []


def get_map_parks():

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

    # JSON 형태 컬럼 변환
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

    result = df.to_dict(orient="records")

    return {
        "items": result,
        "total": len(result),
    }
