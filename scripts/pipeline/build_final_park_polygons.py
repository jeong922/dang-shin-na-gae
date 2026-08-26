from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.ops import unary_union

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

MATCHES_CSV = BASE_DIR / "data" / "processed" / "park_polygon_matches_final.csv"

SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"

OSM_CANDIDATES_CSV = BASE_DIR / "data" / "analysis" / "osm_unmatched_candidates.csv"

OUTPUT_GEOJSON = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "final_park_polygon_summary.csv"


# ============================================================
# 설정
# ============================================================

EXPECTED_PARK_COUNT = 130

EXPECTED_SHAPEFILE_MATCHED = 111


# ============================================================
# 기존 no_match → OSM fallback
# ============================================================
#
# 서울시 Shapefile에서 적절한 Polygon을 찾지 못했지만,
# OSM 후보를 직접 검증한 뒤 사용하기로 결정한 공원.
#
# 이 공원들은 기존 matched 111개와 별도로 추가된다.
# ============================================================

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


# ============================================================
# 서울시 Polygon → OSM Polygon 교체
# ============================================================
#
# 서울시 Shapefile에는 Polygon이 매칭되어 있었지만,
# 면적/이름/위치 검증 결과 더 신뢰할 수 있는
# OSM Polygon으로 교체하기로 결정한 공원.
#
# replacement는 기존 matched 공원을 교체하는 것이므로
# 최종 Polygon 개수를 증가시키지는 않는다.
# ============================================================

OSM_REPLACEMENTS = {
    9: {
        "osm_id": "381793811",
        "osm_name": "대현산 배수지공원",
        "note": (
            "서울시 Polygon 면적이 공식 면적의 약 2.13배였으나 "
            "OSM 대현산 배수지공원은 공식 면적과 거의 일치하여 교체"
        ),
    },
    95: {
        "osm_id": "385989548",
        "osm_name": "금천체육공원",
        "note": (
            "서울시 Polygon이 관악산 전체 영역으로 과대 매칭되어 있었고 "
            "OSM 금천체육공원은 이름, 위치, 면적이 모두 일치하여 교체"
        ),
    },
    108: {
        "osm_id": "471343618",
        "osm_name": "샘말공원",
        "note": (
            "서울시 Polygon이 관악산 전체 영역으로 과대 매칭되어 "
            "OSM 샘말공원 Polygon으로 교체"
        ),
    },
    119: {
        "osm_id": "223356722",
        "osm_name": "신사근린공원",
        "note": (
            "서울시 Polygon이 신사2동 마을마당으로 잘못 매칭되어 "
            "OSM 신사근린공원 Polygon으로 교체"
        ),
    },
    122: {
        "osm_id": "672784474",
        "osm_name": "일자산허브천문공원",
        "note": (
            "서울시 데이터에서는 일자산 전체 parent Polygon이 매칭되어 "
            "공식 면적보다 크게 잡혔으며, "
            "OSM의 일자산허브천문공원이 이름과 위치가 일치하여 교체. "
            "OSM 경계 면적은 공식 면적보다 크므로 "
            "경계 정의 차이 가능성이 있음."
        ),
    },
    106: {
        "osm_id": "370130119",
        "osm_name": "서초문화예술공원",
        "note": (
            "기존 서울시 Shapefile에서는 근린공원(시민의숲) 전체 Polygon이 "
            "매칭되어 공식 면적보다 약 3.54배 크게 잡힘. "
            "OSM의 서초문화예술공원은 이름과 위치가 일치하고 대표 좌표를 포함하며, "
            "면적 71,941.94㎡로 공식 면적 74,385㎡와 약 3.3% 차이이므로 "
            "대상 공원의 개별 Polygon으로 판단하여 교체."
        ),
    },
}


# ============================================================
# 신뢰할 수 있는 Polygon이 없는 공원
# ============================================================
#
# 서울시 Shapefile에서는 matched였지만,
#
# - 과도하게 큰 parent Polygon이 매칭되었거나
# - 실제 공원과 다른 Polygon이 매칭되었거나
# - OSM에서도 신뢰할 수 있는 대체 Polygon을 찾지 못한 경우
#
# 최종 GeoJSON에서 제외한다.
#
# 앞으로 제외 대상이 생기면 이 딕셔너리에만 추가한다.
# NO_RELIABLE_POLYGON_PARK_IDS는 아래에서 자동 생성한다.
# ============================================================

EXCLUDED_PARKS = {
    26: (
        "관악산 전체 영역으로 과대 매칭되었으며 "
        "신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    97: (
        "관악산 전체 영역으로 과대 매칭되었으며 "
        "신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    109: (
        "현재 서울시 Polygon은 초안산 전체에 가까우며, "
        "OSM 초안산생태공원은 이름은 일치하지만 "
        "대표 좌표 및 공식 면적과 차이가 커 "
        "정확한 Polygon으로 확정하기 어려움"
    ),
    114: (
        "현재 매칭된 용마 도시자연공원 Polygon은 "
        "공식 면적보다 약 100배 크며, "
        "OSM의 아차산생태공원은 별개의 공원이므로 "
        "대체 Polygon으로 사용할 수 없음"
    ),
    126: (
        "현재 Polygon이 대상 공원보다 지나치게 큰 parent Polygon이며, "
        "사가정공원에 해당하는 신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    125: (
        "서일대뒷산공원: 현재 매칭된 Polygon은 실제 공원보다 지나치게 큰 "
        "상위 산지 영역이며, 지도에서 확인되는 실제 공원 범위와 일치하지 않음"
    ),
}


# ============================================================
# 파생 설정
# ============================================================
#
# 위의 설정값에서 자동으로 생성한다.
#
# 같은 park_id를 여러 곳에서 중복 관리하지 않도록 한다.
# ============================================================

OSM_REPLACEMENT_PARK_IDS = set(OSM_REPLACEMENTS.keys())

NO_RELIABLE_POLYGON_PARK_IDS = set(EXCLUDED_PARKS.keys())


# ============================================================
# 설정 충돌 검사
# ============================================================
#
# 하나의 공원이
#
# - OSM replacement
# - Polygon 제외
#
# 두 상태를 동시에 가지면 안 된다.
# ============================================================

replacement_excluded_overlap = OSM_REPLACEMENT_PARK_IDS & NO_RELIABLE_POLYGON_PARK_IDS

if replacement_excluded_overlap:
    raise ValueError(
        "OSM replacement와 Polygon 제외 대상이 "
        "중복됩니다: "
        f"{sorted(replacement_excluded_overlap)}"
    )


fallback_excluded_overlap = OSM_FALLBACK_PARK_IDS & NO_RELIABLE_POLYGON_PARK_IDS

if fallback_excluded_overlap:
    raise ValueError(
        "OSM fallback과 Polygon 제외 대상이 "
        "중복됩니다: "
        f"{sorted(fallback_excluded_overlap)}"
    )


# ============================================================
# 예상 개수
# ============================================================

EXPECTED_OSM_FALLBACK = len(OSM_FALLBACK_PARK_IDS)

EXPECTED_OSM_REPLACEMENT = len(OSM_REPLACEMENTS)

EXPECTED_NO_RELIABLE = len(NO_RELIABLE_POLYGON_PARK_IDS)


# replacement는 기존 matched를 교체하므로 개수 변화 없음.
#
# 최종 =
# 기존 Shapefile matched
# - 신뢰 불가 Polygon
# + 기존 no_match 중 OSM fallback
#
EXPECTED_FINAL_POLYGONS = (
    EXPECTED_SHAPEFILE_MATCHED - EXPECTED_NO_RELIABLE + EXPECTED_OSM_FALLBACK
)


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


# ============================================================
# 데이터 정보
# ============================================================

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
        f"전체 공원이 " f"{EXPECTED_PARK_COUNT}개가 아닙니다: " f"{len(matches)}"
    )


# ============================================================
# 설정 대상 park_id 존재 여부 확인
# ============================================================

match_park_ids = set(matches["park_id"].astype(int).tolist())


configured_ids = (
    OSM_FALLBACK_PARK_IDS | OSM_REPLACEMENT_PARK_IDS | NO_RELIABLE_POLYGON_PARK_IDS
)


missing_configured_ids = configured_ids - match_park_ids


if missing_configured_ids:

    raise ValueError(
        "설정된 park_id 중 "
        "park_polygon_matches_final.csv에 "
        "존재하지 않는 ID가 있습니다: "
        f"{sorted(missing_configured_ids)}"
    )


# ============================================================
# 결과 저장용
# ============================================================

result_rows = []

result_geometries = []


# ============================================================
# 1. 서울시 Shapefile Geometry 생성
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

    # --------------------------------------------------------
    # OSM으로 교체할 공원
    # --------------------------------------------------------
    #
    # Shapefile Geometry는 넣지 않고,
    # 아래 OSM replacement 단계에서 추가한다.
    # --------------------------------------------------------

    if park_id in OSM_REPLACEMENT_PARK_IDS:
        continue

    # --------------------------------------------------------
    # 신뢰할 수 없는 Polygon 제외
    # --------------------------------------------------------

    if park_id in NO_RELIABLE_POLYGON_PARK_IDS:

        print(f"[제외] " f"[{park_id}] " f"{park_name}: " f"{EXCLUDED_PARKS[park_id]}")

        continue

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
    # Shapefile에서 Polygon 가져오기
    # --------------------------------------------------------

    selected = polygons[polygons["ID"].astype(str).isin(polygon_ids)].copy()

    if len(selected) != len(polygon_ids):

        found_ids = set(selected["ID"].astype(str).tolist())

        missing_ids = [
            polygon_id for polygon_id in polygon_ids if polygon_id not in found_ids
        ]

        raise ValueError(
            f"[{park_id}] {park_name}: "
            "Shapefile에서 찾을 수 없는 Polygon: "
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
    # 미터 CRS에서 면적 계산
    # --------------------------------------------------------

    geometry_metric = (
        gpd.GeoSeries(
            [geometry],
            crs=polygons.crs,
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
            "geometry_source": "seoul_shapefile",
            "match_method": row["match_method"],
            "polygon_count": polygon_count,
            "source_ids": "|".join(polygon_ids),
            "source_names": row["polygon_labels"],
            "note": row["note"],
            "geometry_type": (geometry.geom_type),
            "area_m2": round(
                geometry_metric.area,
                2,
            ),
        }
    )

    result_geometries.append(geometry)


# ============================================================
# 2. 기존 no_match 공원 OSM fallback
# ============================================================

print()
print("=" * 70)
print("OSM fallback Geometry 생성")
print("=" * 70)


osm_best = osm_candidates[
    (osm_candidates["rank"] == 1)
    & (osm_candidates["park_id"].isin(OSM_FALLBACK_PARK_IDS))
].copy()


if len(osm_best) != EXPECTED_OSM_FALLBACK:

    found_ids = set(osm_best["park_id"].astype(int).tolist())

    missing_ids = OSM_FALLBACK_PARK_IDS - found_ids

    raise ValueError(
        "OSM fallback 1위 후보가 "
        "모두 존재하지 않습니다.\n"
        f"누락 park_id: "
        f"{sorted(missing_ids)}"
    )


osm["_osm_id_str"] = osm["osm_id"].astype(str)


osm_best["_osm_id_str"] = osm_best["osm_id"].astype(str)


for _, candidate in osm_best.iterrows():

    park_id = int(candidate["park_id"])

    park_name = candidate["park_name"]

    osm_id = candidate["_osm_id_str"]

    osm_name = candidate["osm_name"]

    selected = osm[osm["_osm_id_str"] == osm_id].copy()

    if len(selected) > 1:

        selected = selected[selected["fclass"] == candidate["fclass"]].copy()

    if selected.empty:

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"OSM ID={osm_id} Geometry를 "
            "찾을 수 없습니다."
        )

    if len(selected) > 1:

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"OSM ID={osm_id}가 "
            f"{len(selected)}개 존재합니다."
        )

    geometry = selected.iloc[0].geometry

    if geometry is None or geometry.is_empty:

        raise ValueError(f"[{park_id}] {park_name}: " "OSM Geometry가 비어 있습니다.")

    geometry_metric = (
        gpd.GeoSeries(
            [geometry],
            crs=osm.crs,
        )
        .to_crs("EPSG:5186")
        .iloc[0]
    )

    result_rows.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            "geometry_source": "osm",
            "match_method": "osm_fallback",
            "polygon_count": 1,
            "source_ids": osm_id,
            "source_names": osm_name,
            "note": (
                "서울시 Shapefile에서 신뢰 가능한 Polygon을 "
                "찾지 못해 OSM 후보를 수동 검증 후 사용"
            ),
            "geometry_type": (geometry.geom_type),
            "area_m2": round(
                geometry_metric.area,
                2,
            ),
        }
    )

    result_geometries.append(geometry)

    print(f"[{park_id}] " f"{park_name} " f"-> {osm_name}")


# ============================================================
# 3. 잘못된 서울시 Polygon → OSM 교체
# ============================================================

print()
print("=" * 70)
print("OSM Polygon 교체")
print("=" * 70)


for (
    park_id,
    replacement,
) in OSM_REPLACEMENTS.items():

    park_match = matches[matches["park_id"] == park_id]

    if park_match.empty:

        raise ValueError(
            f"park_id={park_id}를 "
            "park_polygon_matches_final.csv에서 "
            "찾을 수 없습니다."
        )

    park_match = park_match.iloc[0]

    park_name = park_match["park_name"]

    osm_id = str(replacement["osm_id"])

    selected = osm[osm["_osm_id_str"] == osm_id].copy()

    if selected.empty:

        raise ValueError(
            f"[{park_id}] {park_name}: " f"OSM ID={osm_id}를 " "찾을 수 없습니다."
        )

    if len(selected) > 1:

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"OSM ID={osm_id}가 "
            f"{len(selected)}개 존재합니다."
        )

    geometry = selected.iloc[0].geometry

    if geometry is None or geometry.is_empty:

        raise ValueError(f"[{park_id}] {park_name}: " "OSM Geometry가 비어 있습니다.")

    geometry_metric = (
        gpd.GeoSeries(
            [geometry],
            crs=osm.crs,
        )
        .to_crs("EPSG:5186")
        .iloc[0]
    )

    result_rows.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            "geometry_source": "osm",
            "match_method": "osm_replacement",
            "polygon_count": 1,
            "source_ids": osm_id,
            "source_names": replacement["osm_name"],
            "note": replacement["note"],
            "geometry_type": (geometry.geom_type),
            "area_m2": round(
                geometry_metric.area,
                2,
            ),
        }
    )

    result_geometries.append(geometry)

    print(
        f"[{park_id}] "
        f"{park_name} "
        f"-> {replacement['osm_name']} "
        f"({geometry_metric.area:,.2f}㎡)"
    )


# ============================================================
# CRS 통일
# ============================================================
#
# result_geometries에는
#
# 1. 서울시 Shapefile Geometry
# 2. OSM fallback Geometry
# 3. OSM replacement Geometry
#
# 순서로 들어 있다.
# ============================================================

shapefile_count = (
    EXPECTED_SHAPEFILE_MATCHED
    - len(OSM_REPLACEMENT_PARK_IDS)
    - len(NO_RELIABLE_POLYGON_PARK_IDS)
)


shapefile_geometries = result_geometries[:shapefile_count]

osm_geometries = result_geometries[shapefile_count:]


shapefile_geometries_4326 = (
    gpd.GeoSeries(
        shapefile_geometries,
        crs=polygons.crs,
    )
    .to_crs("EPSG:4326")
    .tolist()
)


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
# 최종 GeoDataFrame 생성
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


if len(final_gdf) != EXPECTED_FINAL_POLYGONS:

    raise ValueError(
        f"최종 Polygon이 "
        f"{EXPECTED_FINAL_POLYGONS}개가 아닙니다: "
        f"{len(final_gdf)}"
    )


duplicated = final_gdf[final_gdf["park_id"].duplicated(keep=False)]


if not duplicated.empty:

    print(
        duplicated[
            [
                "park_id",
                "park_name",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )

    raise ValueError("동일 park_id가 여러 번 존재합니다.")


if final_gdf.geometry.isna().any():

    raise ValueError("null Geometry가 존재합니다.")


if final_gdf.geometry.is_empty.any():

    raise ValueError("빈 Geometry가 존재합니다.")


invalid = final_gdf[~final_gdf.geometry.is_valid]


print(
    "유효하지 않은 Geometry:",
    len(invalid),
)


if not invalid.empty:

    print("유효하지 않은 Geometry를 " "buffer(0)으로 보정합니다.")

    final_gdf.loc[
        ~final_gdf.geometry.is_valid,
        "geometry",
    ] = final_gdf.loc[
        ~final_gdf.geometry.is_valid
    ].geometry.buffer(0)


# 보정 후 다시 검증
still_invalid = final_gdf[~final_gdf.geometry.is_valid]


if not still_invalid.empty:

    raise ValueError(
        "buffer(0) 보정 후에도 "
        f"유효하지 않은 Geometry가 "
        f"{len(still_invalid)}개 존재합니다."
    )


final_gdf["geometry_type"] = final_gdf.geometry.geom_type


# ============================================================
# 최종 결과
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
    (final_gdf["match_method"] == "osm_fallback").sum(),
)

print(
    "OSM replacement:",
    (final_gdf["match_method"] == "osm_replacement").sum(),
)

print(
    "OSM 전체:",
    (final_gdf["geometry_source"] == "osm").sum(),
)

print(
    "신뢰 불가 Polygon 제거:",
    EXPECTED_NO_RELIABLE,
)

print(
    "최종 Polygon:",
    len(final_gdf),
)

print(
    "Polygon 없음:",
    (EXPECTED_PARK_COUNT - len(final_gdf)),
)


print()
print("[Geometry 타입]")

print(final_gdf["geometry_type"].value_counts().to_string())


# ============================================================
# OSM 사용 결과
# ============================================================

print()
print("=" * 70)
print("OSM 사용 결과")
print("=" * 70)


osm_results = final_gdf[final_gdf["geometry_source"] == "osm"].copy()


if osm_results.empty:

    print("OSM 사용 공원 없음")

else:

    print(
        osm_results[
            [
                "park_id",
                "park_name",
                "match_method",
                "source_names",
                "geometry_type",
                "area_m2",
            ]
        ]
        .sort_values("park_id")
        .to_string(index=False)
    )


# ============================================================
# 신뢰 불가 Polygon 제외 결과
# ============================================================

print()
print("=" * 70)
print("신뢰 불가 Polygon 제외")
print("=" * 70)


removed_matches = matches[matches["park_id"].isin(NO_RELIABLE_POLYGON_PARK_IDS)].copy()


if removed_matches.empty:

    print("제외 공원 없음")

else:

    for _, row in removed_matches.sort_values("park_id").iterrows():

        park_id = int(row["park_id"])

        print(f"[{park_id}] " f"{row['park_name']}")

        print(f"  사유: " f"{EXCLUDED_PARKS[park_id]}")


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
