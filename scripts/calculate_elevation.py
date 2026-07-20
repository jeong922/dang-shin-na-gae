from pathlib import Path
import math
import os

import pandas as pd
import requests

from dotenv import load_dotenv

# ==========================================================
# 기본 설정
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "parks.csv"

OUTPUT_PATH = BASE_DIR / "data" / "features" / "parks_features.csv"

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY가 없습니다.")

# 공원당 샘플 개수
SAMPLE_DISTANCE = 100

# 중심 + 8방향
DIRECTIONS = [
    (0, 0),
    (1, 0),
    (-1, 0),
    (0, 1),
    (0, -1),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
]


# ==========================================================
# 샘플 좌표 생성
# ==========================================================


def create_sample_points(
    lat,
    lon,
):
    """
    중심 + 주변 8방향 좌표 생성
    """

    points = []

    for dx, dy in DIRECTIONS:

        new_lat = lat + (dy * SAMPLE_DISTANCE / 111320)

        new_lon = lon + (dx * SAMPLE_DISTANCE / (111320 * math.cos(math.radians(lat))))

        points.append(
            (
                new_lat,
                new_lon,
            )
        )

    return points


# ==========================================================
# Elevation API
# ==========================================================


def get_elevation(points):

    locations = "|".join([f"{lat},{lon}" for lat, lon in points])

    url = "https://maps.googleapis.com/maps/api/elevation/json"

    response = requests.get(
        url,
        params={
            "locations": locations,
            "key": API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    if data["status"] != "OK":
        raise Exception(data["status"])

    return [item["elevation"] for item in data["results"]]


# ==========================================================
# 데이터 불러오기
# ==========================================================

parks = pd.read_csv(INPUT_PATH)


print(f"공원 수 : {len(parks)}")


# ==========================================================
# 계산
# ==========================================================

results = []


for idx, row in parks.iterrows():

    name = row["name"]

    print(f"[{idx+1}/{len(parks)}] {name}")

    try:

        points = create_sample_points(
            row["lat"],
            row["lon"],
        )

        elevations = get_elevation(points)

        avg = sum(elevations) / len(elevations)

        min_e = min(elevations)

        max_e = max(elevations)

        diff = max_e - min_e

        slope = diff / SAMPLE_DISTANCE

        results.append(
            {
                "avg_elevation": avg,
                "min_elevation": min_e,
                "max_elevation": max_e,
                "elevation_diff": diff,
                "avg_slope": slope,
            }
        )

    except Exception as e:

        print("오류:", e)

        results.append(
            {
                "avg_elevation": None,
                "min_elevation": None,
                "max_elevation": None,
                "elevation_diff": None,
                "avg_slope": None,
            }
        )

# ==========================================================
# 저장
# ==========================================================

result_df = pd.DataFrame(results)


parks_features = pd.concat(
    [
        parks,
        result_df,
    ],
    axis=1,
)


OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


parks_features.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)


print("=" * 50)
print("고도 분석 완료")
print(f"저장 위치 : {OUTPUT_PATH}")
print("=" * 50)
