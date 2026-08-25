from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

FINAL_POLYGONS = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OUTPUT_DIR = BASE_DIR / "data" / "analysis"

OUTPUT_CSV = OUTPUT_DIR / "park_polygon_area_validation.csv"


# ============================================================
# 설정
# ============================================================
#
# polygon_area / official_area
#
# 예:
#
# 0.95
# → Polygon이 공식 면적의 95%
#
# 0.30
# → Polygon이 공식 면적의 30%밖에 안 됨
#
# 2.00
# → Polygon이 공식 면적의 2배
#
# 아래 기준은 절대적인 정답이 아니라
# "검토 대상을 찾기 위한 기준"이다.
# ============================================================

GOOD_MIN_RATIO = 0.70
GOOD_MAX_RATIO = 1.30

REVIEW_MIN_RATIO = 0.40
REVIEW_MAX_RATIO = 2.00


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

polygons = gpd.read_file(FINAL_POLYGONS)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "전체 공원:",
    len(parks),
)

print(
    "Polygon 보유 공원:",
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
    "park_name",
    "geometry_source",
}

missing_polygon_columns = required_polygon_columns - set(polygons.columns)


if missing_polygon_columns:

    raise ValueError(
        "final_park_polygons.geojson에 "
        "필요한 컬럼이 없습니다: "
        f"{sorted(missing_polygon_columns)}"
    )


# ============================================================
# Polygon 면적 계산
# ============================================================
#
# GeoJSON은 EPSG:4326이므로
# geometry.area를 바로 사용하면 안 된다.
#
# 서울 지역 거리/면적 계산에 사용할 수 있는
# EPSG:5186으로 변환해서 면적을 다시 계산한다.
# ============================================================

polygons_m = polygons.to_crs("EPSG:5186")


polygons_m["polygon_area_m2"] = polygons_m.geometry.area


# ============================================================
# 필요한 Polygon 정보만 추출
# ============================================================

polygon_info = polygons_m[
    [
        "park_id",
        "park_name",
        "geometry_source",
        "match_method",
        "geometry_type",
        "polygon_area_m2",
    ]
].copy()


# ============================================================
# parks.csv와 결합
# ============================================================

validation = parks[
    [
        "id",
        "name",
        "area",
    ]
].copy()


validation = validation.rename(
    columns={
        "id": "park_id",
        "name": "park_name",
        "area": "official_area_m2",
    }
)


validation = validation.merge(
    polygon_info,
    on="park_id",
    how="left",
    suffixes=(
        "_official",
        "_polygon",
    ),
)


# ============================================================
# 이름 컬럼 정리
# ============================================================
#
# merge 후:
#
# park_name_official
# park_name_polygon
#
# 형태가 된다.
# ============================================================

validation = validation.rename(
    columns={
        "park_name_official": "park_name",
    }
)


# ============================================================
# Polygon 존재 여부
# ============================================================

validation["has_polygon"] = validation["polygon_area_m2"].notna()


# ============================================================
# 면적 데이터 숫자형 변환
# ============================================================

validation["official_area_m2"] = pd.to_numeric(
    validation["official_area_m2"],
    errors="coerce",
)


validation["polygon_area_m2"] = pd.to_numeric(
    validation["polygon_area_m2"],
    errors="coerce",
)


# ============================================================
# 면적 비율 계산
# ============================================================
#
# polygon_area / official_area
#
# 예:
#
# official = 100,000
# polygon  = 80,000
#
# ratio = 0.8
# ============================================================

validation["area_ratio"] = (
    validation["polygon_area_m2"] / validation["official_area_m2"]
)


# ============================================================
# 면적 차이 계산
# ============================================================

validation["area_difference_m2"] = (
    validation["polygon_area_m2"] - validation["official_area_m2"]
)


# ============================================================
# 면적 차이율
# ============================================================
#
# 절댓값 기준
#
# 0.10 = 10% 차이
# 0.50 = 50% 차이
# ============================================================

validation["area_difference_ratio"] = (
    validation["area_difference_m2"].abs() / validation["official_area_m2"]
)


# ============================================================
# 상태 분류
# ============================================================


def classify_area(row):

    # --------------------------------------------------------
    # Polygon 없음
    # --------------------------------------------------------

    if not row["has_polygon"]:
        return "no_polygon"

    # --------------------------------------------------------
    # 공식 면적 없음
    # --------------------------------------------------------

    official_area = row["official_area_m2"]

    if pd.isna(official_area) or official_area <= 0:
        return "no_official_area"

    ratio = row["area_ratio"]

    # --------------------------------------------------------
    # 정상 범위
    # --------------------------------------------------------

    if GOOD_MIN_RATIO <= ratio <= GOOD_MAX_RATIO:
        return "good"

    # --------------------------------------------------------
    # 검토 필요
    # --------------------------------------------------------

    if REVIEW_MIN_RATIO <= ratio <= REVIEW_MAX_RATIO:
        return "review"

    # --------------------------------------------------------
    # 차이가 매우 큼
    # --------------------------------------------------------

    return "strong_mismatch"


validation["area_status"] = validation.apply(
    classify_area,
    axis=1,
)


# ============================================================
# 숫자 보기 좋게 정리
# ============================================================

validation["official_area_m2"] = validation["official_area_m2"].round(2)


validation["polygon_area_m2"] = validation["polygon_area_m2"].round(2)


validation["area_difference_m2"] = validation["area_difference_m2"].round(2)


validation["area_ratio"] = validation["area_ratio"].round(4)


validation["area_difference_ratio"] = validation["area_difference_ratio"].round(4)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("면적 검증 결과")
print("=" * 70)

print(validation["area_status"].value_counts(dropna=False).to_string())


# ============================================================
# 강한 이상 후보
# ============================================================

strong_mismatch = validation[validation["area_status"] == "strong_mismatch"].copy()


# 차이가 큰 순서
strong_mismatch = strong_mismatch.sort_values(
    "area_difference_ratio",
    ascending=False,
)


print()
print("=" * 70)
print("강한 면적 불일치")
print("=" * 70)


if strong_mismatch.empty:

    print("없음")

else:

    print(
        strong_mismatch[
            [
                "park_id",
                "park_name",
                "official_area_m2",
                "polygon_area_m2",
                "area_ratio",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 일반 검토 대상
# ============================================================

review = validation[validation["area_status"] == "review"].copy()


review = review.sort_values(
    "area_difference_ratio",
    ascending=False,
)


print()
print("=" * 70)
print("면적 검토 필요")
print("=" * 70)


if review.empty:

    print("없음")

else:

    print(
        review[
            [
                "park_id",
                "park_name",
                "official_area_m2",
                "polygon_area_m2",
                "area_ratio",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )


# ============================================================
# Polygon 없는 공원
# ============================================================

no_polygon = validation[validation["area_status"] == "no_polygon"].copy()


print()
print("=" * 70)
print("Polygon 없음")
print("=" * 70)

print(
    "개수:",
    len(no_polygon),
)


if not no_polygon.empty:

    print()

    print(
        no_polygon[
            [
                "park_id",
                "park_name",
                "official_area_m2",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 서울숲 별도 확인
# ============================================================
#
# 지금 우리가 특히 확인하고 싶은 대상이므로
# 콘솔에서 바로 볼 수 있게 한다.
# ============================================================

seoul_forest = validation[
    validation["park_name"].str.contains(
        "서울숲",
        na=False,
    )
]


print()
print("=" * 70)
print("서울숲 확인")
print("=" * 70)


if seoul_forest.empty:

    print("서울숲을 찾을 수 없습니다.")

else:

    print(
        seoul_forest[
            [
                "park_id",
                "park_name",
                "official_area_m2",
                "polygon_area_m2",
                "area_ratio",
                "area_status",
                "geometry_source",
                "match_method",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 저장
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


validation.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
