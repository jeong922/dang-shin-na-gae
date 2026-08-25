from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

OSM_DIR = BASE_DIR / "data" / "osm" / "south-korea-latest-free.shp"

LANDUSE_SHP = OSM_DIR / "gis_osm_landuse_a_free_1.shp"

POIS_SHP = OSM_DIR / "gis_osm_pois_a_free_1.shp"

PROTECTED_SHP = OSM_DIR / "gis_osm_protected_areas_a_free_1.shp"

OUTPUT_GEOJSON = BASE_DIR / "data" / "osm" / "seoul_parks_osm.geojson"

OUTPUT_CSV = BASE_DIR / "data" / "osm" / "seoul_parks_osm_summary.csv"


# ============================================================
# 서울 검색 범위
# ============================================================

SEOUL_BBOX = (
    126.70,
    37.40,
    127.20,
    37.72,
)


# ============================================================
# 추출 대상 fclass
# ============================================================

LANDUSE_FCLASSES = {
    "park",
    "recreation_ground",
}

POIS_FCLASSES = {
    "park",
    "camp_site",
    "picnic_site",
    "dog_park",
    "zoo",
}

PROTECTED_FCLASSES = {
    "national_park",
    "nature_reserve",
}


# ============================================================
# Shapefile 읽기 함수
# ============================================================


def read_osm_layer(
    path,
    allowed_fclasses,
    source_layer,
):
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다:\n{path}")

    gdf = gpd.read_file(
        path,
        bbox=SEOUL_BBOX,
    )

    if gdf.empty:
        return gdf

    gdf = gdf[gdf["fclass"].isin(allowed_fclasses)].copy()

    if gdf.empty:
        return gdf

    gdf["source_layer"] = source_layer

    return gdf


# ============================================================
# 각 레이어 추출
# ============================================================

print("=" * 70)
print("OSM 공원 후보 추출")
print("=" * 70)


landuse = read_osm_layer(
    LANDUSE_SHP,
    LANDUSE_FCLASSES,
    "landuse",
)

pois = read_osm_layer(
    POIS_SHP,
    POIS_FCLASSES,
    "pois",
)

protected = read_osm_layer(
    PROTECTED_SHP,
    PROTECTED_FCLASSES,
    "protected_areas",
)


print(
    "landuse:",
    len(landuse),
)

print(
    "pois:",
    len(pois),
)

print(
    "protected:",
    len(protected),
)


# ============================================================
# 컬럼 통일
# ============================================================

TARGET_COLUMNS = [
    "osm_id",
    "code",
    "fclass",
    "name",
    "source_layer",
    "geometry",
]


def normalize_columns(gdf):
    if gdf.empty:
        return gpd.GeoDataFrame(
            columns=TARGET_COLUMNS,
            geometry="geometry",
            crs="EPSG:4326",
        )

    for column in TARGET_COLUMNS:
        if column not in gdf.columns:
            gdf[column] = None

    return gdf[TARGET_COLUMNS].copy()


landuse = normalize_columns(landuse)

pois = normalize_columns(pois)

protected = normalize_columns(protected)


# ============================================================
# 병합
# ============================================================

combined = pd.concat(
    [
        landuse,
        pois,
        protected,
    ],
    ignore_index=True,
)


combined = gpd.GeoDataFrame(
    combined,
    geometry="geometry",
    crs="EPSG:4326",
)


# ============================================================
# 유효하지 않은 geometry 제거
# ============================================================

combined = combined[combined.geometry.notna()].copy()

combined = combined[~combined.geometry.is_empty].copy()


# ============================================================
# 중복 제거
# ============================================================
#
# landuse와 pois에 같은 OSM park가
# 동시에 들어오는 경우가 있을 수 있으므로
# osm_id + geometry 타입 기준으로 중복 제거
# ============================================================

combined["geometry_type"] = combined.geometry.geom_type


before_count = len(combined)


combined = combined.drop_duplicates(
    subset=[
        "osm_id",
        "geometry_type",
    ]
).copy()


after_count = len(combined)


print()
print("=" * 70)
print("중복 제거")
print("=" * 70)

print(
    "제거 전:",
    before_count,
)

print(
    "제거 후:",
    after_count,
)

print(
    "제거:",
    before_count - after_count,
)


# ============================================================
# 인덱스 정리
# ============================================================

combined = combined.reset_index(drop=True)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("최종 OSM 후보")
print("=" * 70)

print(
    "객체 수:",
    len(combined),
)

print()
print("[fclass]")

print(combined["fclass"].value_counts().to_string())

print()
print("[source_layer]")

print(combined["source_layer"].value_counts().to_string())

print()
print("[geometry]")

print(combined.geometry.geom_type.value_counts().to_string())


# ============================================================
# 저장
# ============================================================

OUTPUT_GEOJSON.parent.mkdir(
    parents=True,
    exist_ok=True,
)


combined.to_file(
    OUTPUT_GEOJSON,
    driver="GeoJSON",
)


summary = combined.drop(columns=["geometry"])

summary.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(
    "GeoJSON:",
    OUTPUT_GEOJSON,
)

print(
    "CSV:",
    OUTPUT_CSV,
)
