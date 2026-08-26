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

PARK_ID = 109

# 후보 분석 결과에서 나온 OSM ID
OSM_CANDIDATES = {
    "choansan_neighborhood": "485045394",  # 초안산근린공원
    "choansan_ecological": "495487176",  # 초안산생태공원
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
# EPSG:5186으로 변환
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
# 현재 Polygon
# ============================================================

current = final_m[final_m["park_id"] == PARK_ID]


if current.empty:
    raise ValueError("현재 최종 Polygon이 없습니다.")


if len(current) > 1:
    raise ValueError("현재 최종 Polygon이 여러 개 존재합니다.")


current_geometry = current.iloc[0].geometry


# ============================================================
# OSM 후보 가져오기
# ============================================================

osm["_osm_id_str"] = osm["osm_id"].astype(str)

osm_m["_osm_id_str"] = osm_m["osm_id"].astype(str)


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
    }


# ============================================================
# 기본 면적 비교
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

    print(
        f"{key}:",
        f"{info['name']} | "
        f"{geometry.area:,.2f}㎡ | "
        f"비율 {geometry.area / official_area:.4f}",
    )


# ============================================================
# 대표 좌표 포함 여부
# ============================================================

print()
print("=" * 70)
print("대표 좌표 포함 여부")
print("=" * 70)


print(
    "현재 Polygon:",
    current_geometry.covers(park_point),
)


for key, info in candidate_geometries.items():

    geometry = info["geometry"]

    print(
        f"{key}:",
        geometry.covers(park_point),
    )


# ============================================================
# 대표 좌표와 Polygon 거리
# ============================================================

print()
print("=" * 70)
print("대표 좌표와 Polygon 거리")
print("=" * 70)


print(
    "현재 Polygon:",
    f"{current_geometry.distance(park_point):,.2f}m",
)


for key, info in candidate_geometries.items():

    geometry = info["geometry"]

    print(
        f"{key}:",
        f"{geometry.distance(park_point):,.2f}m",
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
# 현재 Polygon vs OSM 초안산근린공원
# ============================================================

analyze_pair(
    "current",
    current_geometry,
    "osm_neighborhood",
    candidate_geometries["choansan_neighborhood"]["geometry"],
)


# ============================================================
# 현재 Polygon vs OSM 초안산생태공원
# ============================================================

analyze_pair(
    "current",
    current_geometry,
    "osm_ecological",
    candidate_geometries["choansan_ecological"]["geometry"],
)


# ============================================================
# OSM 후보끼리 비교
# ============================================================

analyze_pair(
    "osm_neighborhood",
    candidate_geometries["choansan_neighborhood"]["geometry"],
    "osm_ecological",
    candidate_geometries["choansan_ecological"]["geometry"],
)


# ============================================================
# 결론용 간단 요약
# ============================================================

print()
print("=" * 70)
print("후보 요약")
print("=" * 70)


for key, info in candidate_geometries.items():

    geometry = info["geometry"]

    ratio = geometry.area / official_area

    distance = geometry.distance(park_point)

    contains_point = geometry.covers(park_point)

    print()

    print(key)

    print(
        "이름:",
        info["name"],
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
        f"{ratio:.4f}",
    )

    print(
        "대표 좌표 포함:",
        contains_point,
    )

    print(
        "대표 좌표 거리:",
        f"{distance:,.2f}m",
    )


print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
