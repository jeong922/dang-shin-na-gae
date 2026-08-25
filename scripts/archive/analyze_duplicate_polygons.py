from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SHP_PATH = BASE_DIR / "data" / "seoul_parks" / "seoul_parks.shp"

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "duplicate_polygon_analysis.csv"


# ============================================================
# 설정
# ============================================================

# 두 Polygon 경계 사이의 거리가 이 값 이하라면
# "거의 같은 위치의 Polygon" 후보로 본다.
#
# 현재 Shapefile CRS가 meter 단위라고 가정.
DISTANCE_THRESHOLD_M = 1.0


# 작은 Polygon 기준으로 이 비율 이상 겹치면
# 거의 동일한 Polygon 후보로 판단한다.
#
# 0.99 = 작은 Polygon 면적의 99% 이상이 겹침
OVERLAP_THRESHOLD = 0.99


# ============================================================
# Shapefile 읽기
# ============================================================

polygons = gpd.read_file(SHP_PATH)


print("=" * 70)
print("Shapefile 정보")
print("=" * 70)

print("Polygon 개수:", len(polygons))
print("CRS:", polygons.crs)
print(
    "Geometry 타입:",
    polygons.geometry.geom_type.value_counts().to_dict(),
)


# ============================================================
# 유효하지 않은 Geometry 처리
# ============================================================

invalid_count = (~polygons.geometry.is_valid).sum()

print()
print("유효하지 않은 Geometry 개수:", invalid_count)


if invalid_count > 0:
    print("유효하지 않은 Geometry를 보정합니다.")

    polygons["geometry"] = polygons.geometry.buffer(0)


# ============================================================
# 면적 계산
# ============================================================

polygons = polygons.copy()

polygons["area_m2"] = polygons.geometry.area


# ============================================================
# Spatial Index 생성
# ============================================================

spatial_index = polygons.sindex


# ============================================================
# 중복 후보 분석
# ============================================================

results = []

checked_pairs = set()


for index_a, polygon_a in polygons.iterrows():

    geom_a = polygon_a.geometry

    # --------------------------------------------------------
    # 주변 후보 검색
    # --------------------------------------------------------

    search_area = geom_a.buffer(DISTANCE_THRESHOLD_M)

    candidate_indices = spatial_index.query(
        search_area,
        predicate="intersects",
    )

    for index_b in candidate_indices:

        # 자기 자신 제외
        if index_a == index_b:
            continue

        # ----------------------------------------------------
        # 같은 조합을 두 번 검사하지 않도록 처리
        #
        # (1, 2)를 검사했다면
        # 나중에 (2, 1)은 검사하지 않음
        # ----------------------------------------------------

        pair = tuple(
            sorted(
                (
                    int(index_a),
                    int(index_b),
                )
            )
        )

        if pair in checked_pairs:
            continue

        checked_pairs.add(pair)

        polygon_b = polygons.iloc[index_b]

        geom_b = polygon_b.geometry

        # ====================================================
        # 1. 완전히 동일한 Geometry
        # ====================================================

        exact_equal = geom_a.equals(geom_b)

        # ====================================================
        # 2. 두 Polygon 거리
        # ====================================================

        distance = geom_a.distance(geom_b)

        # ====================================================
        # 3. 겹치는 면적 계산
        # ====================================================

        intersection = geom_a.intersection(geom_b)

        intersection_area = intersection.area if not intersection.is_empty else 0

        # ====================================================
        # 4. 겹침 비율
        #
        # 작은 Polygon 기준
        #
        # 예:
        #
        # A = 100
        # B = 101
        # intersection = 99
        #
        # overlap_ratio = 99 / 100
        #               = 0.99
        # ====================================================

        area_a = geom_a.area
        area_b = geom_b.area

        smaller_area = min(
            area_a,
            area_b,
        )

        if smaller_area > 0:

            overlap_ratio = intersection_area / smaller_area

        else:

            overlap_ratio = 0

        # ====================================================
        # 5. 거의 동일한 Polygon 판단
        # ====================================================

        near_duplicate = overlap_ratio >= OVERLAP_THRESHOLD

        # ====================================================
        # 중복 후보가 아니면 저장하지 않음
        # ====================================================

        if not (exact_equal or near_duplicate):
            continue

        # ====================================================
        # 결과 저장
        # ====================================================

        results.append(
            {
                "index_a": index_a,
                "index_b": index_b,
                "id_a": polygon_a.get("ID"),
                "id_b": polygon_b.get("ID"),
                "label_a": polygon_a.get("LABEL"),
                "label_b": polygon_b.get("LABEL"),
                "area_a_m2": round(
                    area_a,
                    2,
                ),
                "area_b_m2": round(
                    area_b,
                    2,
                ),
                "intersection_area_m2": round(
                    intersection_area,
                    2,
                ),
                "overlap_ratio": round(
                    overlap_ratio,
                    6,
                ),
                "distance_m": round(
                    distance,
                    6,
                ),
                "exact_equal": exact_equal,
                "near_duplicate": near_duplicate,
                "same_label": (polygon_a.get("LABEL") == polygon_b.get("LABEL")),
            }
        )


# ============================================================
# 결과 DataFrame 생성
# ============================================================

duplicates = pd.DataFrame(results)


# ============================================================
# 결과 정렬
# ============================================================

if not duplicates.empty:

    duplicates = duplicates.sort_values(
        by=[
            "exact_equal",
            "overlap_ratio",
        ],
        ascending=[
            False,
            False,
        ],
    )


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

duplicates.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("중복 Polygon 분석 결과")
print("=" * 70)

print(
    "전체 중복 후보 쌍:",
    len(duplicates),
)


if not duplicates.empty:

    print(
        "완전히 동일한 Polygon:",
        duplicates["exact_equal"].sum(),
    )

    print(
        "99% 이상 겹치는 Polygon:",
        duplicates["near_duplicate"].sum(),
    )

    print(
        "LABEL도 동일:",
        duplicates["same_label"].sum(),
    )


# ============================================================
# 완전히 동일한 Polygon 출력
# ============================================================

print()
print("=" * 70)
print("완전히 동일한 Polygon")
print("=" * 70)


if duplicates.empty:

    print("없음")

else:

    exact_duplicates = duplicates[duplicates["exact_equal"]]

    if exact_duplicates.empty:

        print("없음")

    else:

        print(
            exact_duplicates[
                [
                    "id_a",
                    "label_a",
                    "id_b",
                    "label_b",
                    "area_a_m2",
                    "area_b_m2",
                ]
            ].to_string(index=False)
        )


# ============================================================
# 거의 동일한 Polygon 출력
# ============================================================

print()
print("=" * 70)
print("거의 동일한 Polygon")
print("=" * 70)


if duplicates.empty:

    print("없음")

else:

    near_duplicates = duplicates[
        (duplicates["near_duplicate"]) & (~duplicates["exact_equal"])
    ]

    if near_duplicates.empty:

        print("없음")

    else:

        print(
            near_duplicates[
                [
                    "id_a",
                    "label_a",
                    "id_b",
                    "label_b",
                    "overlap_ratio",
                    "distance_m",
                ]
            ].to_string(index=False)
        )


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
