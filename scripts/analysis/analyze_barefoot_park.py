from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

FINAL_POLYGON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"


# ============================================================
# 설정
# ============================================================

PARK_ID = 98

# 후보 분석에서 확인한 OSM 객체
OSM_CANDIDATES = {
    # 이름이 정확히 일치하는 후보
    "barefoot_named": "484699402",
    # 공식 면적 7,000㎡와 매우 가까웠던 이름 없는 후보
    "barefoot_area_match": "697322580",
}


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

final_polygons = gpd.read_file(FINAL_POLYGON_PATH)

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
    "OSM Polygon:",
    len(osm),
)


# ============================================================
# 공원 정보
# ============================================================

park_row = parks[parks["id"] == PARK_ID]


if park_row.empty:
    raise ValueError(f"parks.csv에서 park_id={PARK_ID}를 찾을 수 없습니다.")


if len(park_row) > 1:
    raise ValueError(f"parks.csv에 park_id={PARK_ID}가 여러 개 존재합니다.")


park_row = park_row.iloc[0]

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
# 현재 최종 Polygon
# ============================================================

current = final_m[final_m["park_id"] == PARK_ID]


if current.empty:
    raise ValueError("현재 최종 Polygon이 없습니다.")


if len(current) > 1:
    raise ValueError("현재 최종 Polygon이 여러 개 존재합니다.")


current_row = current.iloc[0]

current_geometry = current_row.geometry


print()
print("=" * 70)
print("현재 Polygon 정보")
print("=" * 70)

print(
    "source:",
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


# ============================================================
# OSM ID 문자열화
# ============================================================

osm_m["_osm_id_str"] = osm_m["osm_id"].astype(str)


# ============================================================
# OSM 후보 가져오기
# ============================================================

candidate_geometries = {}


for key, osm_id in OSM_CANDIDATES.items():

    selected = osm_m[osm_m["_osm_id_str"] == osm_id]

    if selected.empty:
        raise ValueError(f"OSM ID={osm_id}를 찾을 수 없습니다.")

    if len(selected) > 1:
        raise ValueError(f"OSM ID={osm_id}가 여러 개 존재합니다.")

    row = selected.iloc[0]

    candidate_geometries[key] = {
        "geometry": row.geometry,
        "name": row.get(
            "name",
            "",
        ),
        "fclass": row.get(
            "fclass",
            "",
        ),
        "osm_id": osm_id,
    }


# ============================================================
# 기본 비교
# ============================================================

print()
print("=" * 70)
print("면적 비교")
print("=" * 70)

print(
    "공식 면적:",
    f"{official_area:,.2f}㎡",
)

print(
    "현재 Polygon:",
    f"{current_geometry.area:,.2f}㎡",
    "| 비율:",
    f"{current_geometry.area / official_area:.4f}",
)


for key, info in candidate_geometries.items():

    geometry = info["geometry"]

    name = info["name"]

    display_name = name if pd.notna(name) and str(name).strip() else "(이름 없음)"

    print(
        f"{key}: "
        f"{display_name} | "
        f"{geometry.area:,.2f}㎡ | "
        f"비율 "
        f"{geometry.area / official_area:.4f}"
    )


# ============================================================
# 대표 좌표 관계
# ============================================================

print()
print("=" * 70)
print("대표 좌표와 Polygon 관계")
print("=" * 70)


def print_point_relation(
    name,
    geometry,
):

    contains_point = geometry.covers(park_point)

    distance = geometry.distance(park_point)

    print(f"{name}: " f"포함={contains_point}, " f"거리={distance:,.2f}m")


print_point_relation(
    "current",
    current_geometry,
)


for key, info in candidate_geometries.items():

    print_point_relation(
        key,
        info["geometry"],
    )


# ============================================================
# Polygon 관계 분석
# ============================================================


def analyze_pair(
    name_a,
    geometry_a,
    name_b,
    geometry_b,
):

    intersection = geometry_a.intersection(geometry_b)

    union = geometry_a.union(geometry_b)

    area_a = geometry_a.area

    area_b = geometry_b.area

    intersection_area = intersection.area

    union_area = union.area

    overlap_a = intersection_area / area_a if area_a > 0 else 0

    overlap_b = intersection_area / area_b if area_b > 0 else 0

    print()
    print("-" * 70)

    print(f"{name_a}  vs  {name_b}")

    print("-" * 70)

    print(
        f"{name_a} 면적:",
        f"{area_a:,.2f}㎡",
    )

    print(
        f"{name_b} 면적:",
        f"{area_b:,.2f}㎡",
    )

    print(
        "교차 면적:",
        f"{intersection_area:,.2f}㎡",
    )

    print(
        f"{name_a} 기준 겹침:",
        f"{overlap_a:.2%}",
    )

    print(
        f"{name_b} 기준 겹침:",
        f"{overlap_b:.2%}",
    )

    print(
        "Union 면적:",
        f"{union_area:,.2f}㎡",
    )

    print(
        f"{name_a} contains {name_b}:",
        geometry_a.contains(geometry_b),
    )

    print(
        f"{name_b} contains {name_a}:",
        geometry_b.contains(geometry_a),
    )

    print(
        "intersects:",
        geometry_a.intersects(geometry_b),
    )

    print(
        "overlaps:",
        geometry_a.overlaps(geometry_b),
    )

    print(
        "touches:",
        geometry_a.touches(geometry_b),
    )


# ============================================================
# 현재 vs 이름 일치 OSM
# ============================================================

analyze_pair(
    "current",
    current_geometry,
    "osm_named",
    candidate_geometries["barefoot_named"]["geometry"],
)


# ============================================================
# 현재 vs 면적 일치 OSM
# ============================================================

analyze_pair(
    "current",
    current_geometry,
    "osm_area_match",
    candidate_geometries["barefoot_area_match"]["geometry"],
)


# ============================================================
# OSM 후보끼리 비교
# ============================================================

analyze_pair(
    "osm_named",
    candidate_geometries["barefoot_named"]["geometry"],
    "osm_area_match",
    candidate_geometries["barefoot_area_match"]["geometry"],
)


# ============================================================
# 후보 요약
# ============================================================

print()
print("=" * 70)
print("후보 요약")
print("=" * 70)


print()
print("[현재 Polygon]")

print(
    "이름:",
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


for key, info in candidate_geometries.items():

    geometry = info["geometry"]

    name = info["name"]

    if pd.isna(name) or not str(name).strip():
        name = "(이름 없음)"

    print()
    print(f"[{key}]")

    print(
        "OSM ID:",
        info["osm_id"],
    )

    print(
        "이름:",
        name,
    )

    print(
        "fclass:",
        info["fclass"],
    )

    print(
        "면적:",
        f"{geometry.area:,.2f}㎡",
    )

    print(
        "공식 면적 대비:",
        f"{geometry.area / official_area:.4f}",
    )

    print(
        "대표 좌표 포함:",
        geometry.covers(park_point),
    )

    print(
        "대표 좌표 거리:",
        f"{geometry.distance(park_point):,.2f}m",
    )


print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
