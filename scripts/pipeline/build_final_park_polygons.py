from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Shapefile 기준 최종 매칭 결과
MATCHES_CSV = BASE_DIR / "data" / "processed" / "park_polygon_matches_final.csv"

# 중복 제거된 서울시 공원 Shapefile
SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

# 서울 OSM 공원 후보 전체
OSM_GEOJSON = BASE_DIR / "data" / "osm" / "seoul_parks_osm.geojson"

# no_match 19개에 대한 OSM 후보 분석 결과
OSM_CANDIDATES_CSV = BASE_DIR / "data" / "analysis" / "osm_unmatched_candidates.csv"

# 최종 GeoJSON
OUTPUT_GEOJSON = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

# 확인용 요약
OUTPUT_CSV = BASE_DIR / "data" / "processed" / "final_park_polygon_summary.csv"


# ============================================================
# 설정
# ============================================================

EXPECTED_PARK_COUNT = 130

EXPECTED_SHAPEFILE_MATCHED = 111

# OSM 분석 결과를 보고 최종적으로 채택한 공원
OSM_FALLBACK_PARK_IDS = {
    45,  # 도곡근린공원
    90,  # 서울창포원
    93,  # 중랑캠핑숲
    96,  # 금천폭포근린공원
    100,  # 용두근린공원
    102,  # 와우근린공원
    127,  # 문화비축기지
    129,  # 율현공원
}

EXPECTED_OSM_MATCHED = len(OSM_FALLBACK_PARK_IDS)

EXPECTED_FINAL_POLYGONS = EXPECTED_SHAPEFILE_MATCHED + EXPECTED_OSM_MATCHED


# ============================================================
# 파일 존재 확인
# ============================================================

required_files = [
    MATCHES_CSV,
    SHP_PATH,
    OSM_GEOJSON,
    OSM_CANDIDATES_CSV,
]


for path in required_files:

    if not path.exists():
        raise FileNotFoundError(f"필요한 파일을 찾을 수 없습니다:\n{path}")


# ============================================================
# 데이터 읽기
# ============================================================

matches = pd.read_csv(MATCHES_CSV)

polygons = gpd.read_file(SHP_PATH)

osm = gpd.read_file(OSM_GEOJSON)

osm_candidates = pd.read_csv(OSM_CANDIDATES_CSV)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "전체 공원:",
    len(matches),
)

print(
    "서울시 Polygon:",
    len(polygons),
)

print(
    "OSM 후보:",
    len(osm),
)

print(
    "OSM 매칭 후보 행:",
    len(osm_candidates),
)


# ============================================================
# 기본 검증
# ============================================================

if len(matches) != EXPECTED_PARK_COUNT:
    raise ValueError(
        f"전체 공원이 {EXPECTED_PARK_COUNT}개가 아닙니다: " f"{len(matches)}"
    )


# ============================================================
# 결과 저장용
# ============================================================

result_rows = []

result_geometries = []


# ============================================================
# 1. 서울시 Shapefile 매칭 Geometry 생성
# ============================================================

matched = matches[matches["match_status"] == "matched"].copy()


print()
print("=" * 70)
print("서울시 Shapefile Geometry 생성")
print("=" * 70)

print(
    "Shapefile matched:",
    len(matched),
)


if len(matched) != EXPECTED_SHAPEFILE_MATCHED:

    raise ValueError(
        f"기존 Shapefile matched가 "
        f"{EXPECTED_SHAPEFILE_MATCHED}개가 아닙니다: "
        f"{len(matched)}"
    )


for _, row in matched.iterrows():

    park_id = int(row["park_id"])

    park_name = row["park_name"]

    polygon_count = int(row["polygon_count"])

    polygon_ids_raw = row["polygon_ids"]

    # --------------------------------------------------------
    # Polygon ID 검증
    # --------------------------------------------------------

    if pd.isna(polygon_ids_raw):

        raise ValueError(
            f"[{park_id}] {park_name}: " "matched인데 polygon_ids가 없습니다."
        )

    polygon_ids = [
        polygon_id.strip()
        for polygon_id in str(polygon_ids_raw).split("|")
        if polygon_id.strip()
    ]

    if len(polygon_ids) != polygon_count:

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"polygon_count={polygon_count}, "
            f"실제 Polygon ID={len(polygon_ids)}"
        )

    # --------------------------------------------------------
    # 실제 Shapefile 객체 가져오기
    # --------------------------------------------------------

    selected = polygons[polygons["ID"].astype(str).isin(polygon_ids)].copy()

    if len(selected) != len(polygon_ids):

        found_ids = set(selected["ID"].astype(str).tolist())

        missing_ids = [
            polygon_id for polygon_id in polygon_ids if polygon_id not in found_ids
        ]

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"Shapefile에서 찾을 수 없는 Polygon: "
            f"{missing_ids}"
        )

    # --------------------------------------------------------
    # Geometry 생성
    # --------------------------------------------------------

    if polygon_count == 1:

        geometry = selected.iloc[0].geometry

    else:

        geometry = unary_union(selected.geometry.tolist())

    # --------------------------------------------------------
    # 결과 추가
    # --------------------------------------------------------

    result_rows.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            # 데이터 출처
            "geometry_source": "seoul_shapefile",
            "match_method": row["match_method"],
            "polygon_count": polygon_count,
            "source_ids": "|".join(polygon_ids),
            "source_names": row["polygon_labels"],
            "note": row["note"],
            "geometry_type": (geometry.geom_type),
            "area_m2": round(
                geometry.area,
                2,
            ),
        }
    )

    result_geometries.append(geometry)


# ============================================================
# 2. OSM fallback Geometry 생성
# ============================================================

print()
print("=" * 70)
print("OSM fallback Geometry 생성")
print("=" * 70)


# ------------------------------------------------------------
# OSM 후보 중 rank=1만 사용
# ------------------------------------------------------------

osm_best = osm_candidates[
    (osm_candidates["rank"] == 1)
    & (osm_candidates["park_id"].isin(OSM_FALLBACK_PARK_IDS))
].copy()


if len(osm_best) != EXPECTED_OSM_MATCHED:

    found_ids = set(osm_best["park_id"].astype(int).tolist())

    missing_ids = OSM_FALLBACK_PARK_IDS - found_ids

    raise ValueError(
        "OSM fallback 1위 후보가 모두 존재하지 않습니다.\n"
        f"누락 park_id: {sorted(missing_ids)}"
    )


# ------------------------------------------------------------
# osm_id 비교를 위해 문자열화
# ------------------------------------------------------------

osm["_osm_id_str"] = osm["osm_id"].astype(str)

osm_best["_osm_id_str"] = osm_best["osm_id"].astype(str)


for _, candidate in osm_best.iterrows():

    park_id = int(candidate["park_id"])

    park_name = candidate["park_name"]

    osm_id = candidate["_osm_id_str"]

    osm_name = candidate["osm_name"]

    # --------------------------------------------------------
    # 실제 OSM Geometry 찾기
    # --------------------------------------------------------

    selected = osm[osm["_osm_id_str"] == osm_id].copy()

    # 같은 osm_id가 여러 객체에 남아 있을 가능성에 대비
    if len(selected) > 1:

        # 후보 분석 당시 fclass까지 일치하는 것 우선
        selected = selected[selected["fclass"] == candidate["fclass"]].copy()

    if selected.empty:

        raise ValueError(
            f"[{park_id}] {park_name}: " f"OSM ID={osm_id} Geometry를 찾을 수 없습니다."
        )

    if len(selected) > 1:

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"OSM ID={osm_id}가 {len(selected)}개 존재합니다."
        )

    osm_row = selected.iloc[0]

    geometry = osm_row.geometry

    if geometry is None or geometry.is_empty:

        raise ValueError(f"[{park_id}] {park_name}: " "OSM Geometry가 비어 있습니다.")

    # --------------------------------------------------------
    # OSM 데이터는 EPSG:4326이므로
    # 면적 계산용으로만 EPSG:5186 변환
    # --------------------------------------------------------

    geometry_metric = (
        gpd.GeoSeries(
            [geometry],
            crs=osm.crs,
        )
        .to_crs("EPSG:5186")
        .iloc[0]
    )

    # --------------------------------------------------------
    # 결과 추가
    # --------------------------------------------------------

    result_rows.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            "geometry_source": "osm",
            "match_method": ("osm_fallback"),
            "polygon_count": 1,
            "source_ids": osm_id,
            "source_names": osm_name,
            "note": (
                "서울시 Shapefile에서 신뢰 가능한 Polygon을 "
                "찾지 못해 OSM 1위 후보를 수동 검증 후 사용"
            ),
            "geometry_type": (geometry.geom_type),
            "area_m2": round(
                geometry_metric.area,
                2,
            ),
        }
    )

    # 결과 Geometry는 일단 OSM 원래 CRS 유지
    result_geometries.append(geometry)

    print(f"[{park_id}] " f"{park_name} " f"-> {osm_name}")


# ============================================================
# CRS 통일
# ============================================================
#
# 앞의 Shapefile geometry는 EPSG:5174이고
# OSM geometry는 EPSG:4326이다.
#
# 같은 GeoDataFrame에 바로 넣으면 안 되므로
# 각각 EPSG:4326으로 변환해서 다시 조립한다.
# ============================================================

shapefile_count = len(matched)


shapefile_geometries = result_geometries[:shapefile_count]

osm_geometries = result_geometries[shapefile_count:]


# ------------------------------------------------------------
# Shapefile -> EPSG:4326
# ------------------------------------------------------------

shapefile_geometries_4326 = (
    gpd.GeoSeries(
        shapefile_geometries,
        crs=polygons.crs,
    )
    .to_crs("EPSG:4326")
    .tolist()
)


# ------------------------------------------------------------
# OSM -> EPSG:4326
# ------------------------------------------------------------

osm_geometries_4326 = (
    gpd.GeoSeries(
        osm_geometries,
        crs=osm.crs,
    )
    .to_crs("EPSG:4326")
    .tolist()
)


final_geometries = shapefile_geometries_4326 + osm_geometries_4326


# ============================================================
# 최종 GeoDataFrame
# ============================================================

final_gdf = gpd.GeoDataFrame(
    result_rows,
    geometry=final_geometries,
    crs="EPSG:4326",
)


# ============================================================
# 최종 검증
# ============================================================

print()
print("=" * 70)
print("최종 Geometry 검증")
print("=" * 70)


# ------------------------------------------------------------
# Feature 개수
# ------------------------------------------------------------

if len(final_gdf) != EXPECTED_FINAL_POLYGONS:

    raise ValueError(
        f"최종 Polygon이 "
        f"{EXPECTED_FINAL_POLYGONS}개가 아닙니다: "
        f"{len(final_gdf)}"
    )


# ------------------------------------------------------------
# park_id 중복
# ------------------------------------------------------------

duplicated = final_gdf[final_gdf["park_id"].duplicated(keep=False)]


if not duplicated.empty:

    print(
        duplicated[
            [
                "park_id",
                "park_name",
                "geometry_source",
            ]
        ].to_string(index=False)
    )

    raise ValueError("동일 park_id가 여러 번 존재합니다.")


# ------------------------------------------------------------
# null Geometry
# ------------------------------------------------------------

if final_gdf.geometry.isna().any():

    raise ValueError("null Geometry가 존재합니다.")


# ------------------------------------------------------------
# empty Geometry
# ------------------------------------------------------------

if final_gdf.geometry.is_empty.any():

    raise ValueError("빈 Geometry가 존재합니다.")


# ------------------------------------------------------------
# invalid Geometry
# ------------------------------------------------------------

invalid = final_gdf[~final_gdf.geometry.is_valid]


print(
    "유효하지 않은 Geometry:",
    len(invalid),
)


if not invalid.empty:

    print("유효하지 않은 Geometry를 buffer(0)으로 보정합니다.")

    final_gdf.loc[
        ~final_gdf.geometry.is_valid,
        "geometry",
    ] = final_gdf.loc[
        ~final_gdf.geometry.is_valid
    ].geometry.buffer(0)


# ============================================================
# Geometry 타입 갱신
# ============================================================

final_gdf["geometry_type"] = final_gdf.geometry.geom_type


# ============================================================
# 최종 요약
# ============================================================

print()
print("=" * 70)
print("최종 결과")
print("=" * 70)

print(
    "전체 공원:",
    EXPECTED_PARK_COUNT,
)

print(
    "서울시 Shapefile:",
    (final_gdf["geometry_source"] == "seoul_shapefile").sum(),
)

print(
    "OSM fallback:",
    (final_gdf["geometry_source"] == "osm").sum(),
)

print(
    "최종 Polygon:",
    len(final_gdf),
)

print(
    "Polygon 없음:",
    EXPECTED_PARK_COUNT - len(final_gdf),
)


print()
print("[Geometry 타입]")

print(final_gdf["geometry_type"].value_counts().to_string())


# ============================================================
# OSM fallback 결과
# ============================================================

print()
print("=" * 70)
print("OSM fallback 결과")
print("=" * 70)


osm_results = final_gdf[final_gdf["geometry_source"] == "osm"]


print(
    osm_results[
        [
            "park_id",
            "park_name",
            "source_names",
            "geometry_type",
            "area_m2",
        ]
    ].to_string(index=False)
)


# ============================================================
# 저장
# ============================================================

OUTPUT_GEOJSON.parent.mkdir(
    parents=True,
    exist_ok=True,
)


final_gdf.to_file(
    OUTPUT_GEOJSON,
    driver="GeoJSON",
)


summary = final_gdf.drop(columns=["geometry"])


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
    "요약 CSV:",
    OUTPUT_CSV,
)
