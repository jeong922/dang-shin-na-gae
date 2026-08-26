from pathlib import Path

import geopandas as gpd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SEOUL_SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"


# ============================================================
# 대상 ID
# ============================================================

SEOUL_IDS = {
    "seoul_0035": "생활서비스시설_공원_0035",
    "seoul_0043": "생활서비스시설_공원_0043",
}

OSM_ID = "17338887"


# ============================================================
# 데이터 읽기
# ============================================================

seoul = gpd.read_file(SEOUL_SHP_PATH)

osm = gpd.read_file(OSM_GEOJSON_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "서울시 Polygon:",
    len(seoul),
)

print(
    "OSM Polygon:",
    len(osm),
)


# ============================================================
# CRS 통일
# ============================================================
#
# 면적 계산을 위해 EPSG:5186 사용
# ============================================================

seoul_m = seoul.to_crs("EPSG:5186")

osm_m = osm.to_crs("EPSG:5186")


# ============================================================
# 서울숲 Polygon 가져오기
# ============================================================

selected = {}


for key, polygon_id in SEOUL_IDS.items():

    row = seoul_m[seoul_m["ID"].astype(str) == polygon_id]

    if row.empty:
        raise ValueError(f"서울시 Polygon을 찾을 수 없습니다: {polygon_id}")

    if len(row) > 1:
        raise ValueError(f"서울시 Polygon ID가 중복됩니다: {polygon_id}")

    selected[key] = row.iloc[0].geometry


# ============================================================
# OSM 서울숲 가져오기
# ============================================================

osm_row = osm_m[osm_m["osm_id"].astype(str) == OSM_ID]


if osm_row.empty:
    raise ValueError(f"OSM Polygon을 찾을 수 없습니다: {OSM_ID}")


if len(osm_row) > 1:
    raise ValueError(f"OSM ID가 중복됩니다: {OSM_ID}")


selected["osm"] = osm_row.iloc[0].geometry


# ============================================================
# 기본 면적
# ============================================================

print()
print("=" * 70)
print("기본 면적")
print("=" * 70)


for key, geometry in selected.items():

    print(f"{key:12} " f"{geometry.area:,.2f}㎡")


# ============================================================
# Polygon 관계 분석 함수
# ============================================================


def analyze_pair(
    name_a,
    geometry_a,
    name_b,
    geometry_b,
):

    intersection = geometry_a.intersection(geometry_b)

    union = geometry_a.union(geometry_b)

    intersection_area = intersection.area

    union_area = union.area

    area_a = geometry_a.area
    area_b = geometry_b.area

    overlap_ratio_a = intersection_area / area_a if area_a > 0 else 0

    overlap_ratio_b = intersection_area / area_b if area_b > 0 else 0

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
        f"{overlap_ratio_a:.2%}",
    )

    print(
        f"{name_b} 기준 겹침:",
        f"{overlap_ratio_b:.2%}",
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
# 1. 서울시 0035 vs 0043
# ============================================================

analyze_pair(
    "seoul_0035",
    selected["seoul_0035"],
    "seoul_0043",
    selected["seoul_0043"],
)


# ============================================================
# 2. 서울시 0035 vs OSM
# ============================================================

analyze_pair(
    "seoul_0035",
    selected["seoul_0035"],
    "osm",
    selected["osm"],
)


# ============================================================
# 3. 서울시 0043 vs OSM
# ============================================================

analyze_pair(
    "seoul_0043",
    selected["seoul_0043"],
    "osm",
    selected["osm"],
)


# ============================================================
# 서울시 Polygon 2개 Union
# ============================================================

seoul_union = selected["seoul_0035"].union(selected["seoul_0043"])


print()
print("=" * 70)
print("서울시 서울숲 Union")
print("=" * 70)

print(
    "0035 + 0043 Union:",
    f"{seoul_union.area:,.2f}㎡",
)


# ============================================================
# Union과 OSM 비교
# ============================================================

analyze_pair(
    "seoul_union",
    seoul_union,
    "osm",
    selected["osm"],
)


# ============================================================
# 공식 면적 비교
# ============================================================

OFFICIAL_AREA = 480_994.0


print()
print("=" * 70)
print("공식 면적 비교")
print("=" * 70)


comparison = {
    "seoul_0035": selected["seoul_0035"].area,
    "seoul_0043": selected["seoul_0043"].area,
    "seoul_union": (seoul_union.area),
    "osm": selected["osm"].area,
}


for key, area in comparison.items():

    ratio = area / OFFICIAL_AREA

    difference = area - OFFICIAL_AREA

    print(
        f"{key:12} "
        f"{area:,.2f}㎡ | "
        f"공식 대비 {ratio:.4f} | "
        f"차이 {difference:+,.2f}㎡"
    )


print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
