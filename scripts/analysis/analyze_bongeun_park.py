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

SEOUL_SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"


# ============================================================
# 설정
# ============================================================

PARK_ID = 64

# 후보 분석 결과에서 확인된 관련 서울시 후보
SEOUL_CANDIDATES = {
    "bongeun": "생활서비스시설_공원_1622",
    "seonjeongneung": "생활서비스시설_공원_1614",
    "cheongdam": "생활서비스시설_공원_1631",
}

# 관련 OSM 후보
OSM_CANDIDATES = {
    "bongeun_tennis": "417638568",
    "seonjeongneung": "5493161",
    "cheongdam": "417437657",
}


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
print("현재 Polygon")
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

print(
    "대표 좌표 포함:",
    current_geometry.covers(park_point),
)

print(
    "대표 좌표 거리:",
    f"{current_geometry.distance(park_point):,.2f}m",
)


# ============================================================
# 서울시 후보 가져오기
# ============================================================

seoul_candidates = {}


for key, polygon_id in SEOUL_CANDIDATES.items():

    selected = seoul_m[seoul_m["ID"].astype(str) == polygon_id]

    if selected.empty:
        raise ValueError(f"서울시 Polygon을 찾을 수 없습니다: {polygon_id}")

    if len(selected) > 1:
        raise ValueError(f"서울시 Polygon ID가 중복됩니다: {polygon_id}")

    row = selected.iloc[0]

    seoul_candidates[key] = {
        "geometry": row.geometry,
        "name": row.get(
            "LABEL",
            "",
        ),
        "id": polygon_id,
    }


# ============================================================
# OSM 후보 가져오기
# ============================================================

osm_m["_osm_id_str"] = osm_m["osm_id"].astype(str)


osm_candidates = {}


for key, osm_id in OSM_CANDIDATES.items():

    selected = osm_m[osm_m["_osm_id_str"] == osm_id]

    if selected.empty:
        raise ValueError(f"OSM ID={osm_id}를 찾을 수 없습니다.")

    if len(selected) > 1:
        raise ValueError(f"OSM ID={osm_id}가 여러 개 존재합니다.")

    row = selected.iloc[0]

    osm_candidates[key] = {
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
# 후보 요약 출력
# ============================================================

print()
print("=" * 70)
print("서울시 후보")
print("=" * 70)


for key, info in seoul_candidates.items():

    geometry = info["geometry"]

    print()

    print(key)

    print(
        "이름:",
        info["name"],
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
print("OSM 후보")
print("=" * 70)


for key, info in osm_candidates.items():

    geometry = info["geometry"]

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
# 현재 Polygon vs 주변 후보
# ============================================================

for key, info in seoul_candidates.items():

    if key == "bongeun":
        continue

    analyze_pair(
        "current",
        current_geometry,
        f"seoul_{key}",
        info["geometry"],
    )


for key, info in osm_candidates.items():

    analyze_pair(
        "current",
        current_geometry,
        f"osm_{key}",
        info["geometry"],
    )


# ============================================================
# 주변 서울시 후보 Union 실험
# ============================================================
#
# 이 부분은 "공식 면적과 비슷해지니까 합친다"는 의미가 아니다.
#
# 단지 봉은공원의 현재 Polygon이 주변 다른 Polygon과
# 공간적으로 연결되어 있는지 확인하기 위한 분석이다.
# ============================================================

print()
print("=" * 70)
print("주변 Polygon Union 참고")
print("=" * 70)


for key, info in seoul_candidates.items():

    if key == "bongeun":
        continue

    union = current_geometry.union(info["geometry"])

    print(
        f"current + {key}: "
        f"{union.area:,.2f}㎡ | "
        f"공식 대비 "
        f"{union.area / official_area:.4f}"
    )


print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
