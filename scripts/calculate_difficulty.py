from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.preprocessing import MinMaxScaler

# 기본 설정


BASE_DIR = Path(__file__).resolve().parent.parent


INPUT_PATH = BASE_DIR / "data" / "features" / "parks_features.csv"


OUTPUT_PATH = BASE_DIR / "data" / "features" / "parks_difficulty.csv"


# 데이터 로드


parks = pd.read_csv(
    INPUT_PATH,
    keep_default_na=False,
)


# 난이도 계산에 사용할 Feature
feature_columns = [
    "area",
    "elevation_diff",
    "avg_slope",
]


# 결측 데이터 제거
parks = parks.dropna(subset=feature_columns).reset_index(drop=True)


# Feature 전처리


scaled_features = parks[feature_columns].copy()


# 면적과 고도차는 값의 범위가 크기 때문에 로그 변환
scaled_features["area"] = np.log1p(scaled_features["area"])


scaled_features["elevation_diff"] = np.log1p(scaled_features["elevation_diff"])


# 모든 Feature를 0~1 사이로 정규화
scaler = MinMaxScaler()


normalized = scaler.fit_transform(scaled_features)


parks["area_score"] = normalized[:, 0]

parks["elevation_score"] = normalized[:, 1]

parks["slope_score"] = normalized[:, 2]


# 난이도 점수 계산


# 가중치
AREA_WEIGHT = 0.3

ELEVATION_WEIGHT = 0.3

SLOPE_WEIGHT = 0.4


parks["difficulty_score"] = (
    parks["area_score"] * AREA_WEIGHT
    + parks["elevation_score"] * ELEVATION_WEIGHT
    + parks["slope_score"] * SLOPE_WEIGHT
)


# 난이도 분류


def classify_difficulty(score):

    if score < 0.25:
        return "easy"

    elif score < 0.5:
        return "medium"

    elif score < 0.75:
        return "hard"

    else:
        return "expert"


parks["difficulty"] = parks["difficulty_score"].apply(classify_difficulty)


# 저장


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
