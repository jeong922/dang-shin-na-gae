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

PARK_ID = 114

SEARCH_RADIUS_M = 2000

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
    """
    후보 이름 컬럼을 순서대로 확인해서
    첫 번째 유효한 이름을 반환한다.
    """

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
    """
    이름 비교를 위한 단순 정규화.
    """

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
    공원 유형 단어를 일부 제거해
    핵심 이름 비교에 사용한다.
    """

    value = normalize_name(value)

    removable_words = [
        "도시자연공원",
        "근린공원",
        "생태공원",
        "어린이공원",
        "공원",
    ]

    for word in removable_words:
        value = value.replace(
            word,
            "",
        )

    return value


def classify_achasan_name(
    name,
):
    """
    후보 이름을 세 그룹으로 분류.

    exact_achasan
        -> 아차산공원 자체로 볼 수 있는 이름

    ecological
        -> 아차산생태공원
           별개 공원이므로 114 replacement 후보로
           바로 사용하면 안 됨.

    related
        -> 기타 아차산 관련 시설/공원
    """

    normalized = normalize_name(name)

    simplified = simplify_park_name(name)

    # --------------------------------------------------------
    # 아차산생태공원
    # --------------------------------------------------------

    if "아차산생태" in normalized or "아차산생태" in simplified:
        return "ecological"

    # --------------------------------------------------------
    # 아차산공원 자체
    # --------------------------------------------------------

    if simplified == "아차산":
        return "exact_achasan"

    # --------------------------------------------------------
    # 기타 아차산 관련
    # --------------------------------------------------------

    if "아차산" in normalized:
        return "related"

    return "other"


def analyze_geometry(
    geometry,
):
    """
    현재 Polygon 및 공식 면적과의 관계 계산.
    """

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
            "name_type": classify_achasan_name(name),
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
            "name_type": classify_achasan_name(name),
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
# 정확한 아차산공원 이름 후보
# ============================================================

print()
print("=" * 70)
print("아차산공원 정확 이름 후보")
print("=" * 70)


exact_candidates = []


for candidate in seoul_candidates:

    if candidate["name_type"] != "exact_achasan":
        continue

    exact_candidates.append(
        {
            "source": "seoul",
            **candidate,
        }
    )


for candidate in osm_candidates:

    if candidate["name_type"] != "exact_achasan":
        continue

    exact_candidates.append(
        {
            "source": "osm",
            **candidate,
        }
    )


if not exact_candidates:

    print("아차산공원 정확 이름 후보가 없습니다.")


exact_candidates = sorted(
    exact_candidates,
    key=lambda x: (
        abs(1 - x["area_ratio"]),
        x["distance_m"],
    ),
)


for candidate in exact_candidates:

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
# 아차산생태공원 후보
# ============================================================
#
# 114번 아차산공원과 별개의 공원으로 확인했으므로
# replacement 후보로는 사용하지 않는다.
#
# 위치 관계 참고용으로만 출력한다.
# ============================================================

print()
print("=" * 70)
print("아차산생태공원 후보 - 별개 공원")
print("=" * 70)


ecological_candidates = []


for candidate in seoul_candidates:

    if candidate["name_type"] != "ecological":
        continue

    ecological_candidates.append(
        {
            "source": "seoul",
            **candidate,
        }
    )


for candidate in osm_candidates:

    if candidate["name_type"] != "ecological":
        continue

    ecological_candidates.append(
        {
            "source": "osm",
            **candidate,
        }
    )


if not ecological_candidates:

    print("아차산생태공원 후보가 없습니다.")


for candidate in ecological_candidates:

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
# 기타 아차산 관련 후보
# ============================================================

print()
print("=" * 70)
print("기타 아차산 관련 후보")
print("=" * 70)


related_candidates = []


for candidate in seoul_candidates:

    if candidate["name_type"] != "related":
        continue

    related_candidates.append(
        {
            "source": "seoul",
            **candidate,
        }
    )


for candidate in osm_candidates:

    if candidate["name_type"] != "related":
        continue

    related_candidates.append(
        {
            "source": "osm",
            **candidate,
        }
    )


if not related_candidates:

    print("기타 아차산 관련 후보가 없습니다.")


for candidate in related_candidates:

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
        "거리:",
        f"{candidate['distance_m']:,.2f}m",
    )


# ============================================================
# 공식 면적과 가까운 후보
# ============================================================
#
# 이름과 무관하게 면적만 가까운 후보를 보여준다.
#
# 단, 이 결과만 보고 replacement를 결정하면 안 된다.
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
# 아차산공원 정확 이름 후보만 대상으로 한다.
#
# 아차산생태공원은 명시적으로 제외한다.
# ============================================================

print()
print("=" * 70)
print("유력 교체 후보")
print("=" * 70)


replacement_candidates = []


for candidate in exact_candidates:

    # 공식 면적 대비 너무 극단적인 후보 제외
    if not (0.3 <= candidate["area_ratio"] <= 3.0):
        continue

    # 대표 좌표에서 1km 이내
    if candidate["distance_m"] > 1000:
        continue

    replacement_candidates.append(candidate)


replacement_candidates = sorted(
    replacement_candidates,
    key=lambda x: (
        abs(1 - x["area_ratio"]),
        x["distance_m"],
    ),
)


if not replacement_candidates:

    print("조건을 만족하는 " "아차산공원 교체 후보가 없습니다.")


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
