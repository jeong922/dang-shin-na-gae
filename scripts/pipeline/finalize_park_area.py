from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

FINAL_POLYGON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "parks_with_final_area.csv"

UNRESOLVED_CSV = BASE_DIR / "data" / "analysis" / "unresolved_park_area.csv"


# ============================================================
# 수동 확인 면적
# ============================================================
#
# 원본 데이터의 area가 비정형이거나 잘못 파싱되어
# 외부 자료 등을 통해 사람이 직접 확인한 값.
#
# parks.csv에서 이미 보정되어 있더라도,
# 최종 area의 출처를 명확히 기록하기 위해 관리한다.
# ============================================================

MANUAL_AREA_OVERRIDES = {
    7: {
        "area_m2": 983_791.0,
        "note": (
            "진관근린공원(구파발폭포): "
            "원본 area 컬럼이 시설 설명으로 구성되어 있어 "
            "직접 확인한 공원 면적 983,791㎡로 보정"
        ),
    },
    132: {
        "area_m2": 21_363.0,
        "note": (
            "서소문역사공원: 전체 연면적 약 46,000㎡가 아니라 "
            "지상 역사공원 부지 면적 21,363㎡를 공원 면적으로 사용"
        ),
    },
    133: {
        "area_m2": 2_103.0,
        "note": ("순화문화공원: 확인한 공원 면적 2,103㎡를 사용"),
    },
}


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

polygons = gpd.read_file(FINAL_POLYGON_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "공원:",
    len(parks),
)

print(
    "확정 Polygon:",
    len(polygons),
)

print(
    "Polygon CRS:",
    polygons.crs,
)


# ============================================================
# 필수 컬럼 확인
# ============================================================

required_park_columns = {
    "id",
    "name",
    "area",
}

missing_park_columns = required_park_columns - set(parks.columns)


if missing_park_columns:

    raise ValueError(
        "parks.csv에 필요한 컬럼이 없습니다: " f"{sorted(missing_park_columns)}"
    )


required_polygon_columns = {
    "park_id",
    "geometry",
}

missing_polygon_columns = required_polygon_columns - set(polygons.columns)


if missing_polygon_columns:

    raise ValueError(
        "final_park_polygons.geojson에 "
        "필요한 컬럼이 없습니다: "
        f"{sorted(missing_polygon_columns)}"
    )


# ============================================================
# park_id 중복 검사
# ============================================================

duplicated_park_ids = parks[parks["id"].duplicated(keep=False)]


if not duplicated_park_ids.empty:

    print()
    print("=" * 70)
    print("parks.csv 중복 ID")
    print("=" * 70)

    print(
        duplicated_park_ids[
            [
                "id",
                "name",
            ]
        ].to_string(index=False)
    )

    raise ValueError("parks.csv에 동일한 id가 여러 개 존재합니다.")


duplicated_polygon_ids = polygons[polygons["park_id"].duplicated(keep=False)]


if not duplicated_polygon_ids.empty:

    print()
    print("=" * 70)
    print("Polygon 중복 ID")
    print("=" * 70)

    print(
        duplicated_polygon_ids[
            [
                "park_id",
                "park_name",
            ]
        ].to_string(index=False)
    )

    raise ValueError(
        "final_park_polygons.geojson에 " "동일한 park_id가 여러 개 존재합니다."
    )


# ============================================================
# Polygon 면적 계산
# ============================================================
#
# EPSG:4326 상태에서 geometry.area를 사용하면
# degree² 단위가 되므로 사용하면 안 된다.
#
# 서울 지역 미터 기반 CRS인 EPSG:5186으로 변환하여
# 실제 면적(m²)을 계산한다.
# ============================================================

polygons_m = polygons.to_crs("EPSG:5186").copy()


polygons_m["polygon_area_m2"] = polygons_m.geometry.area


polygon_info = polygons_m[
    [
        "park_id",
        "polygon_area_m2",
    ]
].copy()


# ============================================================
# parks + Polygon 정보 병합
# ============================================================

result = parks.merge(
    polygon_info,
    left_on="id",
    right_on="park_id",
    how="left",
)


# 병합용 park_id는 더 이상 필요 없음
result = result.drop(columns=["park_id"])


# ============================================================
# 최종 면적 컬럼 초기화
# ============================================================

result["official_area_m2"] = pd.to_numeric(
    result["area"],
    errors="coerce",
)


result["final_area_m2"] = pd.NA

result["area_source"] = ""

result["area_note"] = ""


# ============================================================
# 최종 면적 결정
# ============================================================
#
# 우선순위
#
# 1. 수동 확인 면적
# 2. 공식 면적
# 3. 확정 Polygon 면적
# 4. 결측 유지
#
# 중요한 점:
#
# Polygon 면적은 공식 면적이 없는 경우에만 사용한다.
#
# 공식 면적과 Polygon 면적이 다르다고 해서
# Polygon 면적으로 공식 면적을 덮어쓰지 않는다.
# ============================================================

for index, row in result.iterrows():

    park_id = int(row["id"])

    park_name = row["name"]

    official_area = row["official_area_m2"]

    polygon_area = row["polygon_area_m2"]

    # --------------------------------------------------------
    # 1. 수동 보정
    # --------------------------------------------------------

    if park_id in MANUAL_AREA_OVERRIDES:

        override = MANUAL_AREA_OVERRIDES[park_id]

        result.at[
            index,
            "final_area_m2",
        ] = override["area_m2"]

        result.at[
            index,
            "area_source",
        ] = "manual_override"

        result.at[
            index,
            "area_note",
        ] = override["note"]

        continue

    # --------------------------------------------------------
    # 2. 공식 면적
    # --------------------------------------------------------

    if pd.notna(official_area) and official_area > 0:

        result.at[
            index,
            "final_area_m2",
        ] = official_area

        result.at[
            index,
            "area_source",
        ] = "official"

        result.at[
            index,
            "area_note",
        ] = "서울시 공원 데이터의 공식 면적 사용"

        continue

    # --------------------------------------------------------
    # 3. 공식 면적 없음 + 확정 Polygon 존재
    # --------------------------------------------------------
    #
    # final_park_polygons.geojson 자체가
    # 검증 후 채택한 Polygon만 포함하는 최종 데이터이므로
    # 공식 면적이 없는 경우 fallback으로 사용할 수 있다.
    # --------------------------------------------------------

    if pd.notna(polygon_area) and polygon_area > 0:

        result.at[
            index,
            "final_area_m2",
        ] = polygon_area

        result.at[
            index,
            "area_source",
        ] = "polygon"

        result.at[
            index,
            "area_note",
        ] = (
            "공식 면적이 없어 " "검증된 최종 Polygon 면적으로 보완"
        )

        continue

    # --------------------------------------------------------
    # 4. 신뢰할 수 있는 면적 없음
    # --------------------------------------------------------

    result.at[
        index,
        "final_area_m2",
    ] = pd.NA

    result.at[
        index,
        "area_source",
    ] = "missing"

    result.at[
        index,
        "area_note",
    ] = (
        "공식 면적과 신뢰 가능한 Polygon 면적을 " "모두 확보하지 못함"
    )


# ============================================================
# 숫자 타입 정리
# ============================================================

result["final_area_m2"] = pd.to_numeric(
    result["final_area_m2"],
    errors="coerce",
)


result["polygon_area_m2"] = pd.to_numeric(
    result["polygon_area_m2"],
    errors="coerce",
)


result["polygon_area_m2"] = result["polygon_area_m2"].round(2)


result["final_area_m2"] = result["final_area_m2"].round(2)


# ============================================================
# 참고용 면적 비율
# ============================================================
#
# 공식 면적과 Polygon 면적이 둘 다 존재하는 경우만 계산.
#
# 최종 area 결정에는 사용하지 않고
# 검증 및 참고용으로만 저장한다.
# ============================================================

result["polygon_area_ratio"] = result["polygon_area_m2"] / result["official_area_m2"]


result["polygon_area_ratio"] = result["polygon_area_ratio"].round(4)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("최종 면적 출처")
print("=" * 70)

print(result["area_source"].value_counts(dropna=False).to_string())


# ============================================================
# 수동 보정 결과
# ============================================================

manual_rows = result[result["area_source"] == "manual_override"]


print()
print("=" * 70)
print("수동 보정 면적")
print("=" * 70)


if manual_rows.empty:

    print("없음")

else:

    print(
        manual_rows[
            [
                "id",
                "name",
                "official_area_m2",
                "final_area_m2",
                "area_source",
            ]
        ].to_string(index=False)
    )


# ============================================================
# Polygon으로 보완한 공원
# ============================================================

polygon_fallback_rows = result[result["area_source"] == "polygon"]


print()
print("=" * 70)
print("Polygon 면적으로 보완")
print("=" * 70)


if polygon_fallback_rows.empty:

    print("없음")

else:

    print(
        polygon_fallback_rows[
            [
                "id",
                "name",
                "official_area_m2",
                "polygon_area_m2",
                "final_area_m2",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 최종 면적 미확정 공원
# ============================================================

unresolved = result[result["area_source"] == "missing"].copy()


print()
print("=" * 70)
print("최종 면적 미확정")
print("=" * 70)

print(
    "개수:",
    len(unresolved),
)


if unresolved.empty:

    print("없음")

else:

    print()

    print(
        unresolved[
            [
                "id",
                "name",
                "official_area_m2",
                "polygon_area_m2",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 이상 상태 검사
# ============================================================

invalid_final_area = result[
    (result["final_area_m2"].notna()) & (result["final_area_m2"] <= 0)
]


if not invalid_final_area.empty:

    raise ValueError(
        "0 이하의 final_area_m2가 존재합니다:\n"
        + invalid_final_area[
            [
                "id",
                "name",
                "final_area_m2",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 컬럼 순서 정리
# ============================================================

original_columns = [column for column in parks.columns if column != "area"]


final_columns = [
    "id",
    "name",
    "official_area_m2",
    "polygon_area_m2",
    "polygon_area_ratio",
    "final_area_m2",
    "area_source",
    "area_note",
]


remaining_columns = [
    column
    for column in original_columns
    if column
    not in {
        "id",
        "name",
    }
]


result = result[final_columns + remaining_columns]


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)


result.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


UNRESOLVED_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)


unresolved.to_csv(
    UNRESOLVED_CSV,
    index=False,
    encoding="utf-8-sig",
)


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(
    "최종 면적 데이터:",
    OUTPUT_CSV,
)

print(
    "면적 미확정 데이터:",
    UNRESOLVED_CSV,
)
