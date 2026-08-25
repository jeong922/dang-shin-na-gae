from pathlib import Path
from difflib import SequenceMatcher
import re

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

MATCHES_CSV = BASE_DIR / "data" / "processed" / "official_park_matches.csv"

SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "review_candidate_analysis.csv"


# ============================================================
# 설정
# ============================================================

SEARCH_DISTANCE_M = 1500

TOP_N = 5


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
    if pd.isna(name):
        return ""

    name = str(name).lower()

    for word in PARK_TYPE_WORDS:
        name = name.replace(
            word,
            "",
        )

    name = name.replace(
        "시공원",
        "",
    )

    name = re.sub(
        r"[()\[\]{}<>]",
        "",
        name,
    )

    name = re.sub(
        r"[^0-9a-z가-힣]",
        "",
        name,
    )

    return name


# ============================================================
# 이름 점수
# ============================================================


def calculate_name_score(
    park_name,
    polygon_label,
):
    park = normalize_name(park_name)

    polygon = normalize_name(polygon_label)

    if not park or not polygon:
        return 0

    if park == polygon:
        return 150

    if park in polygon or polygon in park:
        return 130

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
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

matches = pd.read_csv(MATCHES_CSV)

polygons = gpd.read_file(SHP_PATH)


# ============================================================
# review 대상만 추출
# ============================================================

review_matches = matches[matches["status"] == "review"].copy()


print("=" * 70)
print("분석 대상")
print("=" * 70)

print(
    "전체 공원:",
    len(parks),
)

print(
    "전체 Polygon:",
    len(polygons),
)

print(
    "review 공원:",
    len(review_matches),
)


# ============================================================
# Point 생성
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
# review 대상 park_id Set
# ============================================================

review_ids = set(review_matches["park_id"])


# ============================================================
# Spatial Index
# ============================================================

spatial_index = polygons.sindex


# ============================================================
# 후보 분석
# ============================================================

results = []


for _, park in park_points.iterrows():

    park_id = park["id"]

    if park_id not in review_ids:
        continue

    park_name = park["name"]

    point = park.geometry

    # --------------------------------------------------------
    # 검색 영역
    # --------------------------------------------------------

    search_area = point.buffer(SEARCH_DISTANCE_M)

    candidate_indices = list(
        spatial_index.query(
            search_area,
            predicate="intersects",
        )
    )

    candidates = []

    # --------------------------------------------------------
    # 후보 점수 계산
    # --------------------------------------------------------

    for polygon_index in candidate_indices:

        polygon = polygons.iloc[polygon_index]

        polygon_label = polygon["LABEL"]

        name_score = calculate_name_score(
            park_name,
            polygon_label,
        )

        spatial_score, distance = calculate_spatial_score(
            point,
            polygon.geometry,
        )

        total_score = name_score + spatial_score

        candidates.append(
            {
                "polygon_index": polygon_index,
                "polygon_id": polygon.get("ID"),
                "polygon_label": polygon_label,
                "name_score": name_score,
                "spatial_score": spatial_score,
                "distance_m": distance,
                "total_score": total_score,
                "point_inside": (polygon.geometry.covers(point)),
                "polygon_area_m2": (polygon.geometry.area),
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

    # --------------------------------------------------------
    # 상위 N개 저장
    # --------------------------------------------------------

    top_candidates = candidates[:TOP_N]

    for rank, candidate in enumerate(
        top_candidates,
        start=1,
    ):

        results.append(
            {
                "park_id": park_id,
                "park_name": park_name,
                "rank": rank,
                "polygon_index": candidate["polygon_index"],
                "polygon_id": candidate["polygon_id"],
                "polygon_label": candidate["polygon_label"],
                "total_score": round(
                    candidate["total_score"],
                    2,
                ),
                "name_score": round(
                    candidate["name_score"],
                    2,
                ),
                "spatial_score": candidate["spatial_score"],
                "distance_m": round(
                    candidate["distance_m"],
                    2,
                ),
                "point_inside": candidate["point_inside"],
                "polygon_area_m2": round(
                    candidate["polygon_area_m2"],
                    2,
                ),
            }
        )


# ============================================================
# DataFrame 생성
# ============================================================

analysis = pd.DataFrame(results)


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

analysis.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 콘솔 출력
# ============================================================

print()
print("=" * 70)
print("review 후보 분석")
print("=" * 70)


for park_id in review_matches["park_id"]:

    park_candidates = analysis[analysis["park_id"] == park_id]

    if park_candidates.empty:
        continue

    park_name = park_candidates.iloc[0]["park_name"]

    print()
    print(f"[{park_id}] {park_name}")

    print("-" * 70)

    for _, row in park_candidates.sort_values("rank").iterrows():

        print(
            f'{int(row["rank"])}위 | '
            f'{row["polygon_label"]} | '
            f'score={row["total_score"]} | '
            f'name={row["name_score"]} | '
            f'spatial={row["spatial_score"]} | '
            f'distance={row["distance_m"]}m | '
            f'inside={row["point_inside"]}'
        )


# ============================================================
# 저장 결과
# ============================================================

print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
