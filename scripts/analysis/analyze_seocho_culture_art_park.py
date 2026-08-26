from pathlib import Path
import re

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

FINAL_POLYGON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

SEOUL_SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"


# ============================================================
# 설정
# ============================================================

PARK_ID = 106

SEARCH_RADIUS_M = 1500

TOP_N = 15


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

final_polygons = gpd.read_file(FINAL_POLYGON_PATH)

seoul = gpd.read_file(SEOUL_SHP_PATH)

osm = gpd.read_file(OSM_GEOJSON_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "공원:",
    len(parks),
)

print(
    "최종 Polygon:",
    len(final_polygons),
)

print(
    "서울시 Polygon:",
    len(seoul),
)

print(
    "OSM Polygon:",
    len(osm),
)


# ============================================================
# 공원 정보
# ============================================================

park_rows = parks[parks["id"] == PARK_ID]


if park_rows.empty:
    raise ValueError(f"parks.csv에서 park_id={PARK_ID}를 찾을 수 없습니다.")


if len(park_rows) > 1:
    raise ValueError(f"parks.csv에 park_id={PARK_ID}가 여러 개 존재합니다.")


park_row = park_rows.iloc[0]

park_name = park_row["name"]

official_area = park_row["area"]

lat = park_row["lat"]

lon = park_row["lon"]


print()
print("=" * 70)
print("공원 정보")
print("=" * 70)

print(
    "park_id:",
    PARK_ID,
)

print(
    "공원명:",
    park_name,
)

print(
    "공식 면적:",
    f"{official_area:,.2f}㎡",
)

print(
    "대표 좌표:",
    f"{lat}, {lon}",
)


# ============================================================
# CRS 변환
# ============================================================

final_m = final_polygons.to_crs("EPSG:5186")

seoul_m = seoul.to_crs("EPSG:5186")

osm_m = osm.to_crs("EPSG:5186")


# ============================================================
# 대표 좌표 생성
# ============================================================

park_point = (
    gpd.GeoSeries(
        [
            Point(
                lon,
                lat,
            )
        ],
        crs="EPSG:4326",
    )
    .to_crs("EPSG:5186")
    .iloc[0]
)


# ============================================================
# 현재 Polygon
# ============================================================

current_rows = final_m[final_m["park_id"] == PARK_ID]


if current_rows.empty:
    raise ValueError("현재 최종 Polygon이 없습니다.")


if len(current_rows) > 1:
    raise ValueError("현재 최종 Polygon이 여러 개 존재합니다.")


current_row = current_rows.iloc[0]

current_geometry = current_row.geometry


print()
print("=" * 70)
print("현재 Polygon")
print("=" * 70)

print(
    "geometry_source:",
    current_row.get(
        "geometry_source",
        "",
    ),
)

print(
    "match_method:",
    current_row.get(
        "match_method",
        "",
    ),
)

print(
    "source_names:",
    current_row.get(
        "source_names",
        "",
    ),
)

print(
    "면적:",
    f"{current_geometry.area:,.2f}㎡",
)

print(
    "공식 면적 대비:",
    f"{current_geometry.area / official_area:.4f}",
)

print(
    "대표 좌표 포함:",
    current_geometry.covers(park_point),
)

print(
    "대표 좌표 거리:",
    f"{current_geometry.distance(park_point):,.2f}m",
)


# ============================================================
# 공통 함수
# ============================================================


def get_name(
    row,
    columns,
):

    for column in columns:

        if column not in row.index:
            continue

        value = row[column]

        if pd.isna(value):
            continue

        value = str(value).strip()

        if value:
            return value

    return "(이름 없음)"


def normalize_name(
    value,
):

    if pd.isna(value):
        return ""

    value = str(value).lower()

    value = re.sub(
        r"\s+",
        "",
        value,
    )

    value = re.sub(
        r"[()<>[\]{}]",
        "",
        value,
    )

    return value


def simplify_park_name(
    value,
):
    """
    공원 유형 단어를 일부 제거하고
    핵심 명칭만 비교하기 위한 함수.
    """

    value = normalize_name(value)

    removable_words = [
        "도시자연공원",
        "근린공원",
        "문화공원",
        "공원",
    ]

    for word in removable_words:

        value = value.replace(
            word,
            "",
        )

    return value


def classify_name(
    name,
):
    """
    문화예술공원 / 서초문화예술공원 후보 분류.
    """

    normalized = normalize_name(name)

    simplified = simplify_park_name(name)

    # --------------------------------------------------------
    # 가장 강한 후보
    # --------------------------------------------------------

    if "서초문화예술" in normalized or "서초문화예술" in simplified:
        return "exact_seocho"

    # --------------------------------------------------------
    # 문화예술공원
    # --------------------------------------------------------

    if "문화예술" in normalized or "문화예술" in simplified:
        return "culture_art"

    # --------------------------------------------------------
    # 서초 관련
    # --------------------------------------------------------

    if "서초" in normalized:
        return "seocho_related"

    return "other"


def analyze_geometry(
    geometry,
):

    area = geometry.area

    distance = geometry.distance(park_point)

    covers_point = geometry.covers(park_point)

    intersection = current_geometry.intersection(geometry)

    intersection_area = intersection.area

    current_overlap = (
        intersection_area / current_geometry.area if current_geometry.area > 0 else 0
    )

    candidate_overlap = intersection_area / area if area > 0 else 0

    return {
        "area_m2": area,
        "area_ratio": (area / official_area if official_area > 0 else None),
        "distance_m": distance,
        "covers_point": covers_point,
        "intersection_m2": intersection_area,
        "current_overlap": current_overlap,
        "candidate_overlap": candidate_overlap,
    }


# ============================================================
# 서울시 후보 검색
# ============================================================

seoul_candidates = []


for index, row in seoul_m.iterrows():

    geometry = row.geometry

    if geometry is None or geometry.is_empty:
        continue

    distance = geometry.distance(park_point)

    if distance > SEARCH_RADIUS_M:
        continue

    name = get_name(
        row,
        [
            "LABEL",
            "name",
        ],
    )

    result = analyze_geometry(geometry)

    seoul_candidates.append(
        {
            "index": index,
            "id": row.get(
                "ID",
                "",
            ),
            "name": name,
            "name_type": classify_name(name),
            **result,
        }
    )


seoul_candidates = sorted(
    seoul_candidates,
    key=lambda x: (
        x["distance_m"],
        abs(1 - x["area_ratio"]),
    ),
)


# ============================================================
# OSM 후보 검색
# ============================================================

osm_candidates = []


for index, row in osm_m.iterrows():

    geometry = row.geometry

    if geometry is None or geometry.is_empty:
        continue

    distance = geometry.distance(park_point)

    if distance > SEARCH_RADIUS_M:
        continue

    name = get_name(
        row,
        [
            "name",
            "LABEL",
        ],
    )

    result = analyze_geometry(geometry)

    osm_candidates.append(
        {
            "index": index,
            "osm_id": row.get(
                "osm_id",
                "",
            ),
            "name": name,
            "name_type": classify_name(name),
            "fclass": row.get(
                "fclass",
                "",
            ),
            **result,
        }
    )


osm_candidates = sorted(
    osm_candidates,
    key=lambda x: (
        x["distance_m"],
        abs(1 - x["area_ratio"]),
    ),
)


# ============================================================
# 서울시 주변 후보 출력
# ============================================================

print()
print("=" * 70)
print(f"서울시 주변 후보 " f"(반경 {SEARCH_RADIUS_M}m)")
print("=" * 70)


for candidate in seoul_candidates[:TOP_N]:

    print()

    print(
        "ID:",
        candidate["id"],
    )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "이름 유형:",
        candidate["name_type"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "대표 좌표 거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "현재 Polygon과 교차:",
        f"{candidate['intersection_m2']:,.2f}㎡",
    )

    print(
        "현재 Polygon 기준 겹침:",
        f"{candidate['current_overlap']:.2%}",
    )

    print(
        "후보 기준 겹침:",
        f"{candidate['candidate_overlap']:.2%}",
    )


# ============================================================
# OSM 주변 후보 출력
# ============================================================

print()
print("=" * 70)
print(f"OSM 주변 후보 " f"(반경 {SEARCH_RADIUS_M}m)")
print("=" * 70)


for candidate in osm_candidates[:TOP_N]:

    print()

    print(
        "OSM ID:",
        candidate["osm_id"],
    )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "이름 유형:",
        candidate["name_type"],
    )

    print(
        "fclass:",
        candidate["fclass"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "대표 좌표 거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "현재 Polygon과 교차:",
        f"{candidate['intersection_m2']:,.2f}㎡",
    )

    print(
        "현재 Polygon 기준 겹침:",
        f"{candidate['current_overlap']:.2%}",
    )

    print(
        "후보 기준 겹침:",
        f"{candidate['candidate_overlap']:.2%}",
    )


# ============================================================
# 이름 관련 후보
# ============================================================

print()
print("=" * 70)
print("문화예술공원 관련 이름 후보")
print("=" * 70)


name_candidates = []


for candidate in seoul_candidates:

    if candidate["name_type"] not in {
        "exact_seocho",
        "culture_art",
    }:
        continue

    name_candidates.append(
        {
            "source": "seoul",
            **candidate,
        }
    )


for candidate in osm_candidates:

    if candidate["name_type"] not in {
        "exact_seocho",
        "culture_art",
    }:
        continue

    name_candidates.append(
        {
            "source": "osm",
            **candidate,
        }
    )


name_candidates = sorted(
    name_candidates,
    key=lambda x: (
        0 if x["name_type"] == "exact_seocho" else 1,
        x["distance_m"],
        abs(1 - x["area_ratio"]),
    ),
)


if not name_candidates:

    print("문화예술공원 관련 이름 후보가 없습니다.")


for candidate in name_candidates:

    print()

    print(
        "source:",
        candidate["source"],
    )

    if candidate["source"] == "seoul":

        print(
            "ID:",
            candidate["id"],
        )

    else:

        print(
            "OSM ID:",
            candidate["osm_id"],
        )

        print(
            "fclass:",
            candidate["fclass"],
        )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "이름 유형:",
        candidate["name_type"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "현재 Polygon과 겹침:",
        f"{candidate['current_overlap']:.2%}",
        "/",
        f"{candidate['candidate_overlap']:.2%}",
    )


# ============================================================
# 현재 Polygon 내부 OSM 후보
# ============================================================
#
# 현재 큰 parent Polygon 안에
# 실제 서초문화예술공원으로 보이는 작은 Polygon이
# 존재하는지 확인한다.
# ============================================================

print()
print("=" * 70)
print("현재 Polygon 내부 OSM 후보")
print("=" * 70)


inside_osm = []


for candidate in osm_candidates:

    # 후보 대부분이 현재 parent 내부
    if candidate["candidate_overlap"] < 0.8:
        continue

    inside_osm.append(candidate)


inside_osm = sorted(
    inside_osm,
    key=lambda x: (
        (
            0
            if x["name_type"] == "exact_seocho"
            else (1 if x["name_type"] == "culture_art" else 2)
        ),
        abs(1 - x["area_ratio"]),
        x["distance_m"],
    ),
)


if not inside_osm:

    print("현재 Polygon 내부 OSM 후보가 없습니다.")


for candidate in inside_osm[:TOP_N]:

    print()

    print(
        "OSM ID:",
        candidate["osm_id"],
    )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "이름 유형:",
        candidate["name_type"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "후보 기준 parent 포함 비율:",
        f"{candidate['candidate_overlap']:.2%}",
    )

    print(
        "현재 Polygon 기준 비율:",
        f"{candidate['current_overlap']:.2%}",
    )


# ============================================================
# 공식 면적과 가까운 후보
# ============================================================

print()
print("=" * 70)
print("공식 면적과 가까운 후보")
print("=" * 70)


all_candidates = []


for candidate in seoul_candidates:

    all_candidates.append(
        {
            "source": "seoul",
            **candidate,
        }
    )


for candidate in osm_candidates:

    all_candidates.append(
        {
            "source": "osm",
            **candidate,
        }
    )


area_candidates = sorted(
    all_candidates,
    key=lambda x: abs(1 - x["area_ratio"]),
)


for candidate in area_candidates[:15]:

    print()

    print(
        "source:",
        candidate["source"],
    )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "이름 유형:",
        candidate["name_type"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "현재 Polygon과 겹침:",
        f"{candidate['current_overlap']:.2%}",
        "/",
        f"{candidate['candidate_overlap']:.2%}",
    )


# ============================================================
# 유력 교체 후보
# ============================================================
#
# 이름, 위치, 면적을 모두 어느 정도 만족하는 후보만 출력.
#
# 단, 자동 교체하지 않는다.
# 실제 지도와 비교해서 마지막으로 사람이 확인한다.
# ============================================================

print()
print("=" * 70)
print("유력 교체 후보")
print("=" * 70)


replacement_candidates = []


for candidate in all_candidates:

    if candidate["name_type"] not in {
        "exact_seocho",
        "culture_art",
    }:
        continue

    # 공식 면적 대비 지나치게 작은/큰 후보 제외
    if not (0.3 <= candidate["area_ratio"] <= 3.0):
        continue

    # 대표 좌표 1km 이내
    if candidate["distance_m"] > 1000:
        continue

    replacement_candidates.append(candidate)


replacement_candidates = sorted(
    replacement_candidates,
    key=lambda x: (
        0 if x["name_type"] == "exact_seocho" else 1,
        abs(1 - x["area_ratio"]),
        x["distance_m"],
    ),
)


if not replacement_candidates:

    print("조건을 만족하는 " "서초문화예술공원 교체 후보가 없습니다.")


for candidate in replacement_candidates:

    print()

    print(
        "source:",
        candidate["source"],
    )

    print(
        "이름:",
        candidate["name"],
    )

    print(
        "면적:",
        f"{candidate['area_m2']:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{candidate['area_ratio']:.4f}",
    )

    print(
        "대표 좌표 포함:",
        candidate["covers_point"],
    )

    print(
        "대표 좌표 거리:",
        f"{candidate['distance_m']:,.2f}m",
    )

    print(
        "현재 Polygon과 겹침:",
        f"{candidate['current_overlap']:.2%}",
        "/",
        f"{candidate['candidate_overlap']:.2%}",
    )


print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
