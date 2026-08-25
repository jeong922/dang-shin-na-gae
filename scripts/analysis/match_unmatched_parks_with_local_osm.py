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

MATCHES_CSV = BASE_DIR / "data" / "processed" / "park_polygon_matches_final.csv"

OSM_GEOJSON = BASE_DIR / "data" / "osm" / "seoul_parks_osm.geojson"

OUTPUT_DIR = BASE_DIR / "data" / "analysis"

OUTPUT_CSV = OUTPUT_DIR / "osm_unmatched_candidates.csv"


# ============================================================
# 설정
# ============================================================

# 공원 좌표 기준 후보 탐색 반경
SEARCH_RADIUS_M = 2000

# 공원별 상위 후보
TOP_N = 10


# ============================================================
# 이름 정규화
# ============================================================


def normalize_name(name):
    if pd.isna(name):
        return ""

    name = str(name).lower()

    name = re.sub(
        r"[\(\)\[\]\{\}<>]",
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
# 공원 유형 단어 제거
# ============================================================


def simplify_park_name(name):
    name = normalize_name(name)

    removable_words = [
        "도시자연공원",
        "근린공원",
        "어린이공원",
        "생태공원",
        "문화공원",
        "체육공원",
        "역사공원",
        "수목원",
        "식물원",
        "캠핑숲",
        "숲길",
        "공원",
    ]

    for word in removable_words:
        name = name.replace(
            word,
            "",
        )

    return name


# ============================================================
# 이름 점수
# ============================================================


def calculate_name_score(
    park_name,
    osm_name,
):
    if pd.isna(osm_name):
        return 0.0

    park_normalized = normalize_name(park_name)

    osm_normalized = normalize_name(osm_name)

    if not park_normalized or not osm_normalized:
        return 0.0

    # 완전 일치
    if park_normalized == osm_normalized:
        return 150.0

    park_simple = simplify_park_name(park_name)

    osm_simple = simplify_park_name(osm_name)

    # 공원 종류만 제거했을 때 동일
    if park_simple and osm_simple and park_simple == osm_simple:
        return 130.0

    # 포함 관계
    if (
        park_simple
        and osm_simple
        and (park_simple in osm_simple or osm_simple in park_simple)
    ):
        return 100.0

    similarity = SequenceMatcher(
        None,
        park_normalized,
        osm_normalized,
    ).ratio()

    return round(
        similarity * 90,
        2,
    )


# ============================================================
# 공간 점수
# ============================================================


def calculate_spatial_score(
    point,
    geometry,
):
    distance = point.distance(geometry)

    point_inside = geometry.covers(point)

    if point_inside:
        score = 120

    elif distance <= 100:
        score = 100

    elif distance <= 300:
        score = 80

    elif distance <= 500:
        score = 60

    elif distance <= 1000:
        score = 30

    elif distance <= 1500:
        score = 10

    else:
        score = 0

    return (
        score,
        float(distance),
        point_inside,
    )


# ============================================================
# OSM fclass 점수
# ============================================================


def calculate_fclass_score(
    fclass,
):
    scores = {
        "park": 30,
        "national_park": 30,
        "nature_reserve": 25,
        "recreation_ground": 20,
        "camp_site": 15,
        "picnic_site": 10,
        "dog_park": 10,
        "zoo": 10,
    }

    return scores.get(
        fclass,
        0,
    )


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

matches = pd.read_csv(MATCHES_CSV)

osm = gpd.read_file(OSM_GEOJSON)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "전체 공원:",
    len(parks),
)

print(
    "최종 매칭 결과:",
    len(matches),
)

print(
    "OSM 후보:",
    len(osm),
)


# ============================================================
# no_match 추출
# ============================================================

unmatched = matches[matches["match_status"] == "no_match"].copy()


print(
    "OSM 재매칭 대상:",
    len(unmatched),
)


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
# 거리 계산용 CRS
# ============================================================

park_points_m = park_points.to_crs("EPSG:5186")

osm_m = osm.to_crs("EPSG:5186")


# ============================================================
# 공간 인덱스
# ============================================================

osm_sindex = osm_m.sindex


# ============================================================
# 결과
# ============================================================

results = []


# ============================================================
# no_match 공원별 분석
# ============================================================

for sequence, (_, match_row) in enumerate(
    unmatched.iterrows(),
    start=1,
):

    park_id = int(match_row["park_id"])

    park_name = match_row["park_name"]

    print()
    print("=" * 70)
    print(f"[{sequence}/{len(unmatched)}] " f"[{park_id}] {park_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # Point 찾기
    # --------------------------------------------------------

    park = park_points_m[park_points_m["id"] == park_id]

    if park.empty:
        print("parks.csv에서 공원을 찾을 수 없습니다.")
        continue

    point = park.iloc[0].geometry

    # --------------------------------------------------------
    # 검색 범위 생성
    # --------------------------------------------------------

    search_area = point.buffer(SEARCH_RADIUS_M)

    # --------------------------------------------------------
    # bbox 후보 검색
    # --------------------------------------------------------

    candidate_indices = list(osm_sindex.intersection(search_area.bounds))

    if not candidate_indices:
        print("검색 반경 내 OSM 후보 없음")
        continue

    candidates = osm_m.iloc[candidate_indices].copy()

    # --------------------------------------------------------
    # 실제 반경 내 객체만
    # --------------------------------------------------------

    candidates["distance_m"] = candidates.geometry.apply(
        lambda geometry: point.distance(geometry)
    )

    candidates = candidates[candidates["distance_m"] <= SEARCH_RADIUS_M].copy()

    if candidates.empty:
        print("검색 반경 내 OSM 후보 없음")
        continue

    # ========================================================
    # 후보 점수 계산
    # ========================================================

    candidate_rows = []

    for osm_index, candidate in candidates.iterrows():

        geometry = candidate.geometry

        osm_name = candidate.get("name")

        fclass = candidate.get("fclass")

        name_score = calculate_name_score(
            park_name,
            osm_name,
        )

        (
            spatial_score,
            distance_m,
            point_inside,
        ) = calculate_spatial_score(
            point,
            geometry,
        )

        fclass_score = calculate_fclass_score(fclass)

        total_score = name_score + spatial_score + fclass_score

        area_m2 = float(geometry.area)

        candidate_rows.append(
            {
                "osm_index": osm_index,
                "park_id": park_id,
                "park_name": park_name,
                "osm_id": candidate.get("osm_id"),
                "osm_name": osm_name,
                "fclass": fclass,
                "source_layer": (candidate.get("source_layer")),
                "geometry_type": (geometry.geom_type),
                "distance_m": round(
                    distance_m,
                    2,
                ),
                "point_inside": (point_inside),
                "area_m2": round(
                    area_m2,
                    2,
                ),
                "name_score": (name_score),
                "spatial_score": (spatial_score),
                "fclass_score": (fclass_score),
                "total_score": round(
                    total_score,
                    2,
                ),
            }
        )

    # ========================================================
    # 점수 정렬
    # ========================================================

    candidate_df = pd.DataFrame(candidate_rows)

    candidate_df = (
        candidate_df.sort_values(
            by=[
                "total_score",
                "name_score",
                "distance_m",
            ],
            ascending=[
                False,
                False,
                True,
            ],
        )
        .head(TOP_N)
        .reset_index(drop=True)
    )

    candidate_df["rank"] = candidate_df.index + 1

    # ========================================================
    # 1위와 2위 점수 차이
    # ========================================================

    best_score = candidate_df.iloc[0]["total_score"]

    second_score = (
        candidate_df.iloc[1]["total_score"] if len(candidate_df) > 1 else None
    )

    score_margin = (
        round(
            best_score - second_score,
            2,
        )
        if second_score is not None
        else None
    )

    candidate_df["score_margin"] = score_margin

    # ========================================================
    # 콘솔 출력
    # ========================================================

    for _, row in candidate_df.iterrows():

        print(
            f"{int(row['rank'])}위 | "
            f"{row['osm_name']} | "
            f"{row['fclass']} | "
            f"score={row['total_score']:.2f} | "
            f"name={row['name_score']:.2f} | "
            f"spatial={row['spatial_score']} | "
            f"distance={row['distance_m']:.2f}m | "
            f"inside={row['point_inside']} | "
            f"area={row['area_m2']:.2f}m²"
        )

    results.extend(candidate_df.to_dict("records"))


# ============================================================
# 결과 저장
# ============================================================

result_df = pd.DataFrame(results)


OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


result_df.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("OSM 매칭 후보 분석 완료")
print("=" * 70)

print(
    "no_match 공원:",
    len(unmatched),
)

print(
    "후보 행:",
    len(result_df),
)


if not result_df.empty:

    print()
    print("=" * 70)
    print("공원별 1위 OSM 후보")
    print("=" * 70)

    best_candidates = result_df[result_df["rank"] == 1].sort_values("park_id")

    print(
        best_candidates[
            [
                "park_id",
                "park_name",
                "osm_name",
                "fclass",
                "total_score",
                "name_score",
                "spatial_score",
                "distance_m",
                "point_inside",
                "area_m2",
                "score_margin",
            ]
        ].to_string(index=False)
    )


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
