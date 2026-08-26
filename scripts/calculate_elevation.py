from pathlib import Path
import math
import os

import pandas as pd
import requests
from dotenv import load_dotenv

# 기본 설정


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = BASE_DIR / "data" / "processed" / "parks_with_final_area.csv"

OUTPUT_PATH = BASE_DIR / "data" / "features" / "parks_features.csv"


# 환경 변수 로드
load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


if not API_KEY:
    raise ValueError("GOOGLE_MAPS_API_KEY가 없습니다.")


# 중심 + 주변 8방향 샘플링
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


# 동적 샘플링 거리 계산


def get_sample_distance(area_m2):
    """
    공원 면적 기반 샘플링 거리 계산

    작은 공원:
    - 가까운 거리에서 고도 변화 확인

    큰 공원:
    - 넓은 범위의 고도 변화 확인

    최소 30m ~ 최대 500m 제한
    """

    if pd.isna(area_m2) or area_m2 <= 0:
        return 100.0

    # 공원을 원형이라고 가정한 예상 반경 계산
    radius = math.sqrt(area_m2 / math.pi)

    # 예상 반경의 60% 지점을 샘플링 거리로 사용
    sample_distance = radius * 0.6

    # 너무 작은 거리 / 큰 거리 방지
    return max(30.0, min(sample_distance, 500.0))


# 샘플 좌표 생성


def create_sample_points(lat, lon, sample_distance):
    """
    중심 좌표 기준 8방향 고도 샘플 위치 생성

    반환:
    - points: Google Elevation API 요청 좌표
    - distances: 중심으로부터 실제 거리
    """

    points = []
    distances = []

    for dx, dy in DIRECTIONS:

        # 방향 벡터 기준 실제 거리 계산
        distance = math.sqrt(dx**2 + dy**2) * sample_distance

        # 위도 1도 ≈ 111.32km 기준 변환
        new_lat = lat + (dy * sample_distance / 111320)

        # 경도는 위도에 따라 보정 필요
        new_lon = lon + (dx * sample_distance / (111320 * math.cos(math.radians(lat))))

        points.append(
            (
                new_lat,
                new_lon,
            )
        )

        distances.append(distance)

    return points, distances


# Google Elevation API


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


# 데이터 불러오기


parks = pd.read_csv(
    INPUT_PATH,
    keep_default_na=False,
)


print(f"공원 수 : {len(parks)}")


# 고도 Feature 계산


results = []


for idx, row in parks.iterrows():

    print(f"[{idx + 1}/{len(parks)}] {row['name']}")

    try:

        sample_distance = get_sample_distance(row["final_area_m2"])

        points, distances = create_sample_points(
            row["lat"],
            row["lon"],
            sample_distance,
        )

        elevations = get_elevation(points)

        # 중심 고도
        center_elevation = elevations[0]

        # 주변 고도
        surrounding_elevations = elevations[1:]

        # 중심으로부터 실제 거리
        surrounding_distances = distances[1:]

        # 고도 변화 / 거리 = 경사도
        slopes = [
            abs(elevation - center_elevation) / distance
            for elevation, distance in zip(
                surrounding_elevations,
                surrounding_distances,
            )
        ]

        results.append(
            {
                "sample_distance": sample_distance,
                "avg_elevation": sum(elevations) / len(elevations),
                "min_elevation": min(elevations),
                "max_elevation": max(elevations),
                "elevation_diff": max(elevations) - min(elevations),
                "avg_slope": sum(slopes) / len(slopes),
            }
        )

    except Exception as e:

        print("오류:", e)

        results.append(
            {
                "sample_distance": None,
                "avg_elevation": None,
                "min_elevation": None,
                "max_elevation": None,
                "elevation_diff": None,
                "avg_slope": None,
            }
        )


# 저장

result_df = pd.DataFrame(results)


parks_features = pd.concat(
    [
        parks,
        result_df,
    ],
    axis=1,
)


OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


parks_features.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)


print("=" * 50)
print("고도 분석 완료")
print(f"저장 위치 : {OUTPUT_PATH}")
print("=" * 50)
