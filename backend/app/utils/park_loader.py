from functools import lru_cache
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


@lru_cache()
def load_parks():
    """
    공원 데이터 로드 및 전처리
    """

    df = pd.read_csv(
        DATA_PATH,
        keep_default_na=False,
    )

    df = df.rename(
        columns={
            "avg_slope": "avgSlope",
            "elevation_diff": "elevationDiff",
            "pet_status": "petStatus",
            "pet_notice": "petNotice",
            "pet_restricted_locations": "petRestrictedLocations",
            "service_animal_allowed": "serviceAnimalAllowed",
            "map_image": "mapImage",
            "opened_at": "openedAt",
            "sample_distance": "sampleDistance",
            "avg_elevation": "avgElevation",
            "min_elevation": "minElevation",
            "max_elevation": "maxElevation",
            "area_score": "areaScore",
            "elevation_score": "elevationScore",
            "slope_score": "slopeScore",
            "difficulty_score": "difficultyScore",
        }
    )

    # JSON 컬럼 변환
    df["petRestrictedLocations"] = df["petRestrictedLocations"].apply(parse_json_column)

    # numpy 타입 제거
    bool_columns = [
        "serviceAnimalAllowed",
    ]

    for column in bool_columns:
        if column in df.columns:
            df[column] = df[column].astype(bool)

    return df
