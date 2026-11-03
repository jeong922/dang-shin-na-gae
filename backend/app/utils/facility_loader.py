from functools import lru_cache
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]

DATA_PATH = BASE_DIR / "data" / "processed" / "seoul_pet_facilities.csv"


@lru_cache(maxsize=1)
def load_facilities():
    """
    시설 데이터 로드 및 ID 검증
    """

    df = pd.read_csv(
        DATA_PATH,
        encoding="utf-8-sig",
        dtype={
            "facility_id": "string",
            "phone": "string",
        },
    )

    if df["facility_id"].isna().any() or df["facility_id"].duplicated().any():
        raise ValueError("시설 ID에 결측 또는 중복이 있습니다.")

    return df
