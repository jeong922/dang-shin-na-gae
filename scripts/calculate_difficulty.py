from pathlib import Path

import pandas as pd
from sklearn.preprocessing import MinMaxScaler

# ==========================================================
# 경로 설정
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "features" / "parks_features.csv"

OUTPUT_PATH = BASE_DIR / "data" / "features" / "parks_difficulty.csv"

# ==========================================================
# 데이터 불러오기
# ==========================================================

parks = pd.read_csv(INPUT_PATH, keep_default_na=False)

print(f"공원 수 : {len(parks)}")

# ==========================================================
# 사용할 Feature
# ==========================================================

feature_columns = [
    "area",
    "elevation_diff",
    "avg_slope",
]

# 결측치 제거
parks = parks.dropna(subset=feature_columns).reset_index(drop=True)

# ==========================================================
# Feature 정규화
# ==========================================================

scaler = MinMaxScaler()

normalized = scaler.fit_transform(parks[feature_columns])

parks["area_score"] = normalized[:, 0]
parks["elevation_score"] = normalized[:, 1]
parks["slope_score"] = normalized[:, 2]

# ==========================================================
# 난이도 점수 계산
# ==========================================================

AREA_WEIGHT = 0.3
ELEVATION_WEIGHT = 0.4
SLOPE_WEIGHT = 0.3

parks["difficulty_score"] = (
    parks["area_score"] * AREA_WEIGHT
    + parks["elevation_score"] * ELEVATION_WEIGHT
    + parks["slope_score"] * SLOPE_WEIGHT
)

# ==========================================================
# 난이도 분류
# ==========================================================

parks["difficulty"] = pd.cut(
    parks["difficulty_score"],
    bins=[0.0, 0.25, 0.5, 0.75, 1.0],
    labels=[
        "easy",
        "medium",
        "hard",
        "expert",
    ],
    include_lowest=True,
)

# ==========================================================
# 결과 확인
# ==========================================================

print("\n난이도 분포")

print(parks["difficulty"].value_counts().sort_index())

print("\n상위 10개 난이도")

print(
    parks[
        [
            "name",
            "difficulty_score",
            "difficulty",
        ]
    ]
    .sort_values(
        "difficulty_score",
        ascending=False,
    )
    .head(10)
)

# ==========================================================
# 저장
# ==========================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)

parks.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)

print("=" * 50)
print("난이도 계산 완료")
print(f"저장 위치 : {OUTPUT_PATH}")
print("=" * 50)
