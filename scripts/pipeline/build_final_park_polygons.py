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

OSM_PROTECTED_SHP = (
    BASE_DIR
    / "data"
    / "osm"
    / "south-korea-latest-free.shp"
    / "gis_osm_protected_areas_a_free_1.shp"
)

OSM_CANDIDATES_CSV = BASE_DIR / "data" / "analysis" / "osm_unmatched_candidates.csv"

OUTPUT_GEOJSON = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "final_park_polygon_summary.csv"


# ============================================================
# 기존 no_match → OSM fallback
# ============================================================
#
# 중요:
# park_id가 아니라 park_name 기준으로 관리한다.
#
# 서울시 원본의 연번(id)은 공원이 추가/삭제되면 바뀔 수 있지만
# 공원명은 수동 검증 결과를 연결하는 기준으로 상대적으로 안정적이다.
#
# 아래 공원들은 서울시 Shapefile에서는 신뢰할 Polygon을 확정하지
# 못했지만, OSM 1위 후보를 사람이 직접 검증한 뒤 사용하기로 한 공원이다.
# ============================================================

OSM_FALLBACK_PARK_NAMES = {
    "도곡근린공원",
    "서울창포원",
    "중랑캠핑숲",
    "금천폭포근린공원",
    "용두근린공원",
    "와우근린공원",
    "문화비축기지",
    "율현공원",
}


# ============================================================
# 서울시 Polygon → OSM Polygon 교체
# ============================================================
#
# 서울시 Shapefile에 매칭은 되어 있었지만
# 위치/이름/면적 검증 결과 OSM Polygon이 더 신뢰할 수 있었던 공원.
#
# key는 park_name.
# osm_id는 이미 수동 검증한 OSM 객체 ID.
# ============================================================

OSM_REPLACEMENTS = {
    "응봉공원 (대현산배수지공원)": {
        "osm_id": "381793811",
        "osm_name": "대현산 배수지공원",
        "note": (
            "서울시 Polygon 면적이 공식 면적의 약 2.13배였으나 "
            "OSM 대현산 배수지공원은 공식 면적과 거의 일치하여 교체"
        ),
    },
    "금천체육공원(관악산)": {
        "osm_id": "385989548",
        "osm_name": "금천체육공원",
        "note": (
            "서울시 Polygon이 관악산 전체 영역으로 과대 매칭되어 있었고 "
            "OSM 금천체육공원은 이름, 위치, 면적이 모두 일치하여 교체"
        ),
    },
    "샘말공원(관악산근린공원 샘말지구)": {
        "osm_id": "471343618",
        "osm_name": "샘말공원",
        "note": (
            "서울시 Polygon이 관악산 전체 영역으로 과대 매칭되어 "
            "OSM 샘말공원 Polygon으로 교체"
        ),
    },
    "신사근린공원": {
        "osm_id": "223356722",
        "osm_name": "신사근린공원",
        "note": (
            "서울시 Polygon이 신사2동 마을마당으로 잘못 매칭되어 "
            "OSM 신사근린공원 Polygon으로 교체"
        ),
    },
    "허브천문공원": {
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
    "문화예술공원": {
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
    "북한산국립공원": {
        "osm_id": "17336247",
        "osm_name": "북한산국립공원",
        "source": "protected_area",
        "fclass": "national_park",
        "note": (
            "기존 서울시 Shapefile의 도시자연공원((북한산)<시공원>) Polygon은 "
            "북한산국립공원 전체 경계가 아닌 일부 영역으로 확인됨. "
            "OSM protected areas 데이터의 national_park 경계를 직접 검증한 결과 "
            "실제 북한산국립공원 범위와 일치하여 교체."
        ),
    },
}


# ============================================================
# 신뢰할 수 있는 Polygon이 없는 공원
# ============================================================
#
# 서울시 Shapefile에서는 matched였지만
# 실제 대상보다 과도하게 큰 parent Polygon이거나 잘못 매칭됐고,
# OSM에서도 신뢰할 수 있는 대체 Polygon을 찾지 못한 경우.
#
# 최종 GeoJSON에서 제외한다.
# ============================================================

EXCLUDED_PARKS = {
    "감로천생태공원(관악산)": (
        "관악산 전체 영역으로 과대 매칭되었으며 "
        "신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    "만수천공원(관악산)": (
        "관악산 전체 영역으로 과대 매칭되었으며 "
        "신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    "초안산생태공원": (
        "현재 서울시 Polygon은 초안산 전체에 가까우며, "
        "OSM 초안산생태공원은 이름은 일치하지만 "
        "대표 좌표 및 공식 면적과 차이가 커 "
        "정확한 Polygon으로 확정하기 어려움"
    ),
    "아차산공원": (
        "현재 매칭된 용마 도시자연공원 Polygon은 "
        "공식 면적보다 약 100배 크며, "
        "OSM의 아차산생태공원은 별개의 공원이므로 "
        "대체 Polygon으로 사용할 수 없음"
    ),
    "용마도시자연공원(사가정공원)": (
        "현재 Polygon이 대상 공원보다 지나치게 큰 parent Polygon이며, "
        "사가정공원에 해당하는 신뢰할 수 있는 개별 Polygon을 찾지 못함"
    ),
    "서일대뒷산공원": (
        "현재 매칭된 Polygon은 실제 공원보다 지나치게 큰 "
        "상위 산지 영역이며, 지도에서 확인되는 실제 공원 범위와 일치하지 않음"
    ),
}


# ============================================================
# 파생 설정 / 충돌 검사
# ============================================================

OSM_REPLACEMENT_PARK_NAMES = set(OSM_REPLACEMENTS.keys())
NO_RELIABLE_POLYGON_PARK_NAMES = set(EXCLUDED_PARKS.keys())

replacement_excluded_overlap = (
    OSM_REPLACEMENT_PARK_NAMES & NO_RELIABLE_POLYGON_PARK_NAMES
)

if replacement_excluded_overlap:
    raise ValueError(
        "OSM replacement와 Polygon 제외 대상이 중복됩니다: "
        f"{sorted(replacement_excluded_overlap)}"
    )

fallback_excluded_overlap = OSM_FALLBACK_PARK_NAMES & NO_RELIABLE_POLYGON_PARK_NAMES

if fallback_excluded_overlap:
    raise ValueError(
        "OSM fallback과 Polygon 제외 대상이 중복됩니다: "
        f"{sorted(fallback_excluded_overlap)}"
    )

fallback_replacement_overlap = OSM_FALLBACK_PARK_NAMES & OSM_REPLACEMENT_PARK_NAMES

if fallback_replacement_overlap:
    raise ValueError(
        "OSM fallback과 replacement 대상이 중복됩니다: "
        f"{sorted(fallback_replacement_overlap)}"
    )


# ============================================================
# 공통 함수
# ============================================================


def to_wgs84_geometry(geometry, source_crs):
    """
    Geometry 하나를 EPSG:4326으로 변환한다.

    기존 코드처럼 결과 리스트의 앞/뒤 개수를 이용해
    Shapefile/OSM Geometry를 나눠 변환하지 않고,
    Geometry를 추가하는 시점에 바로 CRS를 통일한다.
    """

    return (
        gpd.GeoSeries(
            [geometry],
            crs=source_crs,
        )
        .to_crs("EPSG:4326")
        .iloc[0]
    )


def calculate_area_m2(geometry, source_crs):
    """
    Geometry 면적을 EPSG:5186 기준 m²로 계산한다.
    """

    geometry_metric = (
        gpd.GeoSeries(
            [geometry],
            crs=source_crs,
        )
        .to_crs("EPSG:5186")
        .iloc[0]
    )

    return round(
        geometry_metric.area,
        2,
    )


# ============================================================
# 파일 존재 확인
# ============================================================

required_files = [
    MATCHES_CSV,
    SHP_PATH,
    OSM_GEOJSON,
    OSM_PROTECTED_SHP,
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

osm_protected = gpd.read_file(OSM_PROTECTED_SHP)

osm_candidates = pd.read_csv(OSM_CANDIDATES_CSV)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print("전체 공원:", len(matches))
print("서울시 Polygon:", len(polygons))
print("OSM 후보:", len(osm))
print("OSM 보호구역:", len(osm_protected))
print("OSM 매칭 후보 행:", len(osm_candidates))


# ============================================================
# 필수 컬럼 검증
# ============================================================

required_match_columns = {
    "park_id",
    "park_name",
    "match_status",
    "match_method",
    "polygon_count",
    "polygon_ids",
    "polygon_labels",
    "note",
}

missing_match_columns = required_match_columns - set(matches.columns)

if missing_match_columns:
    raise ValueError(
        "park_polygon_matches_final.csv에 필요한 컬럼이 없습니다: "
        f"{sorted(missing_match_columns)}"
    )


required_candidate_columns = {
    "park_name",
    "rank",
    "osm_id",
    "osm_name",
    "fclass",
}

missing_candidate_columns = required_candidate_columns - set(osm_candidates.columns)

if missing_candidate_columns:
    raise ValueError(
        "osm_unmatched_candidates.csv에 필요한 컬럼이 없습니다: "
        f"{sorted(missing_candidate_columns)}"
    )


# ============================================================
# 공원명 중복 검사
# ============================================================
#
# 이 파일의 수동 설정은 park_name 기준이므로
# 동일한 이름이 여러 공원에 존재하면 안전하게 중단한다.
# ============================================================

duplicated_names = matches[matches["park_name"].duplicated(keep=False)]

if not duplicated_names.empty:
    print()
    print("=" * 70)
    print("중복 공원명")
    print("=" * 70)

    print(
        duplicated_names[
            [
                "park_id",
                "park_name",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "동일한 park_name이 여러 개 존재하여 "
        "이름 기반 설정을 안전하게 적용할 수 없습니다."
    )


# ============================================================
# 설정 대상 공원 존재 여부 확인
# ============================================================

match_park_names = set(matches["park_name"].astype(str).tolist())

configured_names = (
    OSM_FALLBACK_PARK_NAMES
    | OSM_REPLACEMENT_PARK_NAMES
    | NO_RELIABLE_POLYGON_PARK_NAMES
)

missing_configured_names = configured_names - match_park_names

if missing_configured_names:
    raise ValueError(
        "설정된 공원 중 park_polygon_matches_final.csv에 "
        "존재하지 않는 공원이 있습니다: "
        f"{sorted(missing_configured_names)}"
    )


# ============================================================
# 설정 상태 검증
# ============================================================

match_by_name = matches.set_index("park_name")


for park_name in OSM_FALLBACK_PARK_NAMES:
    status = match_by_name.loc[
        park_name,
        "match_status",
    ]

    if status != "no_match":
        raise ValueError(
            f"{park_name}: OSM fallback 대상인데 " f"match_status={status} 입니다."
        )


for park_name in OSM_REPLACEMENT_PARK_NAMES | NO_RELIABLE_POLYGON_PARK_NAMES:
    status = match_by_name.loc[
        park_name,
        "match_status",
    ]

    if status != "matched":
        raise ValueError(
            f"{park_name}: replacement/excluded 대상인데 "
            f"match_status={status} 입니다."
        )


# ============================================================
# OSM ID 문자열 정리
# ============================================================

osm["_osm_id_str"] = osm["osm_id"].astype(str)

osm_protected["_osm_id_str"] = osm_protected["osm_id"].astype(str)

osm_candidates["_osm_id_str"] = osm_candidates["osm_id"].astype(str)


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


for _, row in matched.iterrows():

    park_id = int(row["park_id"])

    park_name = str(row["park_name"])

    # --------------------------------------------------------
    # OSM으로 교체할 공원
    # --------------------------------------------------------

    if park_name in OSM_REPLACEMENT_PARK_NAMES:
        continue

    # --------------------------------------------------------
    # 신뢰할 수 없는 Polygon 제외
    # --------------------------------------------------------

    if park_name in NO_RELIABLE_POLYGON_PARK_NAMES:

        print(f"[제외] [{park_id}] {park_name}: " f"{EXCLUDED_PARKS[park_name]}")

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

    if geometry is None or geometry.is_empty:
        raise ValueError(
            f"[{park_id}] {park_name}: " "Shapefile Geometry가 비어 있습니다."
        )

    area_m2 = calculate_area_m2(
        geometry,
        polygons.crs,
    )

    geometry_4326 = to_wgs84_geometry(
        geometry,
        polygons.crs,
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
            "geometry_type": geometry_4326.geom_type,
            "area_m2": area_m2,
        }
    )

    result_geometries.append(geometry_4326)


# ============================================================
# 2. 기존 no_match 공원 OSM fallback
# ============================================================

print()
print("=" * 70)
print("OSM fallback Geometry 생성")
print("=" * 70)


for park_name in sorted(OSM_FALLBACK_PARK_NAMES):

    park_match = match_by_name.loc[park_name]

    park_id = int(park_match["park_id"])

    # --------------------------------------------------------
    # 기존 OSM 후보 파일에서도 park_name 기준으로 조회
    #
    # 과거 park_id가 변경되어도 후보를 재사용할 수 있게 한다.
    # --------------------------------------------------------

    candidate_rows = osm_candidates[
        (osm_candidates["park_name"].astype(str) == park_name)
        & (osm_candidates["rank"] == 1)
    ].copy()

    if candidate_rows.empty:
        raise ValueError(
            f"[{park_id}] {park_name}: " "OSM fallback 1위 후보가 없습니다."
        )

    if len(candidate_rows) > 1:
        raise ValueError(
            f"[{park_id}] {park_name}: "
            "OSM fallback rank=1 후보가 "
            f"{len(candidate_rows)}개 존재합니다."
        )

    candidate = candidate_rows.iloc[0]

    osm_id = str(candidate["_osm_id_str"])

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

    area_m2 = calculate_area_m2(
        geometry,
        osm.crs,
    )

    geometry_4326 = to_wgs84_geometry(
        geometry,
        osm.crs,
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
            "geometry_type": geometry_4326.geom_type,
            "area_m2": area_m2,
        }
    )

    result_geometries.append(geometry_4326)

    print(f"[{park_id}] " f"{park_name} " f"-> {osm_name}")


# ============================================================
# 3. 잘못된 서울시 Polygon → OSM 교체
# ============================================================

print()
print("=" * 70)
print("OSM Polygon 교체")
print("=" * 70)


for (
    park_name,
    replacement,
) in OSM_REPLACEMENTS.items():

    park_match = match_by_name.loc[park_name]

    park_id = int(park_match["park_id"])

    osm_id = str(replacement["osm_id"])

    source = replacement.get("source", "parks")

    if source == "protected_area":
        source_gdf = osm_protected

        selected = source_gdf[source_gdf["_osm_id_str"] == osm_id].copy()

        if "fclass" in replacement:
            selected = selected[selected["fclass"] == replacement["fclass"]].copy()

    elif source == "parks":
        source_gdf = osm

        selected = source_gdf[source_gdf["_osm_id_str"] == osm_id].copy()

    else:
        raise ValueError(
            f"[{park_id}] {park_name}: " f"지원하지 않는 OSM source={source}"
        )

    if selected.empty:
        raise ValueError(
            f"[{park_id}] {park_name}: " f"OSM ID={osm_id}를 찾을 수 없습니다."
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

    area_m2 = calculate_area_m2(
        geometry,
        source_gdf.crs,
    )

    geometry_4326 = to_wgs84_geometry(
        geometry,
        source_gdf.crs,
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
            "geometry_type": geometry_4326.geom_type,
            "area_m2": area_m2,
        }
    )

    result_geometries.append(geometry_4326)

    print(
        f"[{park_id}] "
        f"{park_name} "
        f"-> {replacement['osm_name']} "
        f"({area_m2:,.2f}㎡)"
    )


# ============================================================
# 최종 GeoDataFrame 생성
# ============================================================

final_gdf = gpd.GeoDataFrame(
    result_rows,
    geometry=result_geometries,
    crs="EPSG:4326",
)

final_gdf = final_gdf.sort_values("park_id").reset_index(drop=True)


# ============================================================
# 최종 검증
# ============================================================

print()
print("=" * 70)
print("최종 Geometry 검증")
print("=" * 70)


# ------------------------------------------------------------
# 예상 Polygon 공원 수를 현재 입력 데이터로 동적 계산
#
# final =
# matched
# - excluded
# + no_match 중 OSM fallback
#
# replacement는 기존 matched 하나를 OSM 하나로 교체하므로
# 총 개수 변화 없음.
# ------------------------------------------------------------

expected_final_count = (
    len(matched) - len(NO_RELIABLE_POLYGON_PARK_NAMES) + len(OSM_FALLBACK_PARK_NAMES)
)


if len(final_gdf) != expected_final_count:
    raise ValueError(
        f"최종 Polygon 개수가 예상과 다릅니다. "
        f"예상={expected_final_count}, "
        f"실제={len(final_gdf)}"
    )


# ------------------------------------------------------------
# park_id 중복
# ------------------------------------------------------------

duplicated_ids = final_gdf[final_gdf["park_id"].duplicated(keep=False)]

if not duplicated_ids.empty:

    print(
        duplicated_ids[
            [
                "park_id",
                "park_name",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )

    raise ValueError("동일 park_id가 여러 번 존재합니다.")


# ------------------------------------------------------------
# park_name 중복
# ------------------------------------------------------------

duplicated_names = final_gdf[final_gdf["park_name"].duplicated(keep=False)]

if not duplicated_names.empty:

    print(
        duplicated_names[
            [
                "park_id",
                "park_name",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )

    raise ValueError("동일 park_name이 여러 번 존재합니다.")


# ------------------------------------------------------------
# Geometry null / empty
# ------------------------------------------------------------

if final_gdf.geometry.isna().any():
    raise ValueError("null Geometry가 존재합니다.")

if final_gdf.geometry.is_empty.any():
    raise ValueError("빈 Geometry가 존재합니다.")


# ------------------------------------------------------------
# Geometry validity
# ------------------------------------------------------------

invalid = final_gdf[~final_gdf.geometry.is_valid]


print(
    "유효하지 않은 Geometry:",
    len(invalid),
)


if not invalid.empty:

    print("유효하지 않은 Geometry를 " "buffer(0)으로 보정합니다.")

    invalid_mask = ~final_gdf.geometry.is_valid

    final_gdf.loc[
        invalid_mask,
        "geometry",
    ] = final_gdf.loc[
        invalid_mask
    ].geometry.buffer(0)


still_invalid = final_gdf[~final_gdf.geometry.is_valid]

if not still_invalid.empty:
    raise ValueError(
        "buffer(0) 보정 후에도 "
        f"유효하지 않은 Geometry가 "
        f"{len(still_invalid)}개 존재합니다."
    )


final_gdf["geometry_type"] = final_gdf.geometry.geom_type


# ============================================================
# 모든 결과가 원본 park 목록에 존재하는지 확인
# ============================================================

match_names = set(matches["park_name"].astype(str).tolist())

final_names = set(final_gdf["park_name"].astype(str).tolist())

unexpected_names = final_names - match_names

if unexpected_names:
    raise ValueError(
        "최종 Polygon에 입력 공원 목록에 없는 "
        f"공원이 있습니다: {sorted(unexpected_names)}"
    )


# ============================================================
# Polygon 없는 공원
# ============================================================

parks_without_polygon = matches[
    ~matches["park_name"].astype(str).isin(final_names)
].copy()


# ============================================================
# 최종 결과 출력
# ============================================================

print()
print("=" * 70)
print("최종 결과")
print("=" * 70)

print(
    "전체 공원:",
    len(matches),
)

print(
    "입력 Shapefile matched:",
    len(matched),
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
    len(NO_RELIABLE_POLYGON_PARK_NAMES),
)

print(
    "최종 Polygon:",
    len(final_gdf),
)

print(
    "Polygon 없음:",
    len(parks_without_polygon),
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


removed_matches = matches[
    matches["park_name"].astype(str).isin(NO_RELIABLE_POLYGON_PARK_NAMES)
].copy()


if removed_matches.empty:

    print("제외 공원 없음")

else:

    for _, row in removed_matches.sort_values("park_id").iterrows():

        park_id = int(row["park_id"])

        park_name = str(row["park_name"])

        print(f"[{park_id}] " f"{park_name}")

        print("  사유: " f"{EXCLUDED_PARKS[park_name]}")


# ============================================================
# Polygon 없는 공원 출력
# ============================================================

print()
print("=" * 70)
print("최종 Polygon 없음")
print("=" * 70)


if parks_without_polygon.empty:

    print("없음")

else:

    print(
        parks_without_polygon[
            [
                "park_id",
                "park_name",
                "match_status",
                "match_method",
            ]
        ]
        .sort_values("park_id")
        .to_string(index=False)
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
