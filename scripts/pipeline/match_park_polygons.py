from pathlib import Path
from difflib import SequenceMatcher
import re

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

# SHP_PATH = BASE_DIR / "data" / "seoul_parks" / "seoul_parks.shp"
SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "official_park_matches.csv"


# ============================================================
# 설정
# ============================================================

# 공원 대표 좌표에서 이 거리 안에 있는 Polygon만 후보로 사용
SEARCH_DISTANCE_M = 1500

# 이 점수 이상이면 자동 매칭
HIGH_CONFIDENCE_SCORE = 180

# 최소 매칭 점수
MIN_MATCH_SCORE = 100

# 1등과 2등 점수 차이가 이 값보다 작으면 검토 필요
AMBIGUOUS_MARGIN = 20


# ============================================================
# 이름 정규화
# ============================================================

PARK_TYPE_WORDS = [
    "도시자연공원",
    "도시자연공원구역",
    "근린공원",
    "어린이공원",
    "생태공원",
    "문화공원",
    "체육공원",
    "역사공원",
    "수변공원",
    "묘지공원",
    "국립공원",
    "기타공원",
    "강변공원",
    "공원",
]


def normalize_name(name):
    """
    공원 이름 비교를 위한 정규화.

    예)
    남산공원
        -> 남산

    근린공원(서울숲)
        -> 서울숲

    도시자연공원((일자산)<길동생태공원>)
        -> 일자산길동
    """

    if pd.isna(name):
        return ""

    name = str(name).lower()

    # 공원 유형 단어 제거
    for word in PARK_TYPE_WORDS:
        name = name.replace(word, "")

    # 시공원 같은 관리용 표현 제거
    name = name.replace("시공원", "")

    # 괄호 자체는 없애되 안의 이름은 유지
    name = re.sub(r"[()\[\]{}<>]", "", name)

    # 공백 / 특수문자 제거
    name = re.sub(r"[^0-9a-z가-힣]", "", name)

    return name


# ============================================================
# 이름 점수
# ============================================================


def calculate_name_score(park_name, polygon_label):
    park = normalize_name(park_name)
    polygon = normalize_name(polygon_label)

    if not park or not polygon:
        return 0

    # --------------------------------------------------------
    # 완전히 동일
    # --------------------------------------------------------

    if park == polygon:
        return 150

    # --------------------------------------------------------
    # 한쪽 이름이 다른 쪽에 포함
    #
    # 길동생태공원
    # 도시자연공원((일자산)<길동생태공원>)
    #
    # 같은 경우를 잡기 위함
    # --------------------------------------------------------

    if park in polygon or polygon in park:
        return 130

    # --------------------------------------------------------
    # 문자열 유사도
    # --------------------------------------------------------

    ratio = SequenceMatcher(
        None,
        park,
        polygon,
    ).ratio()

    return ratio * 100


# ============================================================
# 공간 점수
# ============================================================


def calculate_spatial_score(point, polygon):
    if polygon.covers(point):
        return 200, 0.0

    distance = point.distance(polygon)

    if distance <= 50:
        return 150, distance

    if distance <= 100:
        return 120, distance

    if distance <= 300:
        return 80, distance

    if distance <= 500:
        return 50, distance

    if distance <= 1000:
        return 20, distance

    if distance <= SEARCH_DISTANCE_M:
        return 0, distance

    return 0, distance


# ============================================================
# 전체 점수
# ============================================================


def calculate_match_score(
    park_name,
    point,
    polygon_label,
    polygon_geometry,
):
    name_score = calculate_name_score(
        park_name,
        polygon_label,
    )

    spatial_score, distance = calculate_spatial_score(
        point,
        polygon_geometry,
    )

    total_score = name_score + spatial_score

    return {
        "total_score": total_score,
        "name_score": name_score,
        "spatial_score": spatial_score,
        "distance_m": distance,
    }


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

polygons = gpd.read_file(SHP_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print("공원 개수:", len(parks))
print("Polygon 개수:", len(polygons))

print()
print("Polygon CRS:", polygons.crs)


# ============================================================
# 공원 Point 생성
# ============================================================

park_points = gpd.GeoDataFrame(
    parks.copy(),
    geometry=gpd.points_from_xy(
        parks["lon"],
        parks["lat"],
    ),
    crs="EPSG:4326",
)


# ============================================================
# CRS 통일
# ============================================================

park_points = park_points.to_crs(polygons.crs)


# ============================================================
# Spatial Index
# ============================================================

spatial_index = polygons.sindex


# ============================================================
# 공원별 Polygon 매칭
# ============================================================

results = []


for _, park in park_points.iterrows():

    park_id = park["id"]
    park_name = park["name"]

    point = park.geometry

    # --------------------------------------------------------
    # 검색 범위
    # --------------------------------------------------------

    search_area = point.buffer(SEARCH_DISTANCE_M)

    candidate_indices = list(
        spatial_index.query(
            search_area,
            predicate="intersects",
        )
    )

    # --------------------------------------------------------
    # 후보 없음
    # --------------------------------------------------------

    if not candidate_indices:

        results.append(
            {
                "park_id": park_id,
                "park_name": park_name,
                "polygon_id": None,
                "polygon_label": None,
                "total_score": 0,
                "name_score": 0,
                "spatial_score": 0,
                "distance_m": None,
                "candidate_count": 0,
                "second_score": None,
                "score_margin": None,
                "status": "unmatched",
            }
        )

        continue

    # --------------------------------------------------------
    # 후보 평가
    # --------------------------------------------------------

    candidates = []

    for polygon_index in candidate_indices:

        polygon = polygons.iloc[polygon_index]

        score = calculate_match_score(
            park_name,
            point,
            polygon["LABEL"],
            polygon.geometry,
        )

        candidates.append(
            {
                "polygon_index": polygon_index,
                "polygon_id": polygon["ID"],
                "polygon_label": polygon["LABEL"],
                **score,
            }
        )

    # --------------------------------------------------------
    # 점수순 정렬
    # --------------------------------------------------------

    candidates.sort(
        key=lambda x: (
            x["total_score"],
            -x["distance_m"],
        ),
        reverse=True,
    )

    best = candidates[0]

    second = candidates[1] if len(candidates) > 1 else None

    # --------------------------------------------------------
    # 1등 / 2등 차이
    # --------------------------------------------------------

    if second:

        score_margin = best["total_score"] - second["total_score"]

        second_score = second["total_score"]

    else:

        score_margin = None
        second_score = None

    # ============================================================
    # 상태 결정
    # ============================================================

    if best["distance_m"] > 1000 and best["name_score"] < 130:
        status = "unmatched"

    elif score_margin is not None and score_margin < AMBIGUOUS_MARGIN:
        status = "review"

    elif best["distance_m"] == 0 and best["name_score"] >= 40:
        status = "high"

    elif best["name_score"] >= 130 and best["distance_m"] <= 300:
        status = "high"

    else:
        status = "review"

    # ============================================================
    # 결과 저장
    # ============================================================
    # 중요:
    # 이 부분은 if / elif / else 바깥에 있어야 함

    results.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            "polygon_id": best["polygon_id"],
            "polygon_label": best["polygon_label"],
            "total_score": round(
                best["total_score"],
                2,
            ),
            "name_score": round(
                best["name_score"],
                2,
            ),
            "spatial_score": best["spatial_score"],
            "distance_m": round(
                best["distance_m"],
                2,
            ),
            "candidate_count": len(candidates),
            "second_score": (
                round(second_score, 2) if second_score is not None else None
            ),
            "score_margin": (
                round(score_margin, 2) if score_margin is not None else None
            ),
            "status": status,
        }
    )

# ============================================================
# DataFrame 생성
# ============================================================

matches = pd.DataFrame(results)


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

matches.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 결과 출력
# ============================================================

print()
print("=" * 70)
print("매칭 결과")
print("=" * 70)

print(matches["status"].value_counts().to_string())


print()
print("=" * 70)
print("검토 필요")
print("=" * 70)

review = matches[matches["status"] == "review"]

for _, row in review.iterrows():

    print(
        f'{row["park_name"]:<25}'
        f' -> {row["polygon_label"]:<35}'
        f' score={row["total_score"]:>6}'
        f' distance={row["distance_m"]:>8}m'
        f' margin={row["score_margin"]}'
    )


print()
print("저장:", OUTPUT_CSV)
