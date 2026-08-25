from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CLASSIFIED_CSV = BASE_DIR / "data" / "processed" / "classified_review_matches.csv"

REVIEW_CANDIDATES_CSV = (
    BASE_DIR / "data" / "processed" / "review_candidate_analysis.csv"
)

SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "multiple_polygon_geometry_analysis.csv"


# ============================================================
# 설정
# ============================================================

# 공원별 상위 몇 개 후보 Polygon을 비교할지
TOP_N = 3


# ============================================================
# 데이터 읽기
# ============================================================

classified = pd.read_csv(CLASSIFIED_CSV)

candidates = pd.read_csv(REVIEW_CANDIDATES_CSV)

polygons = gpd.read_file(SHP_PATH)


# ============================================================
# multiple_polygons 대상 추출
# ============================================================

multiple = classified[classified["classification"] == "multiple_polygons"].copy()


print("=" * 70)
print("분석 대상")
print("=" * 70)

print(
    "multiple_polygons 공원 개수:",
    len(multiple),
)

print()

print(
    multiple[
        [
            "park_id",
            "park_name",
        ]
    ].to_string(index=False)
)


# ============================================================
# 결과 저장
# ============================================================

results = []


# ============================================================
# 공원별 분석
# ============================================================

for _, park_row in multiple.iterrows():

    park_id = park_row["park_id"]
    park_name = park_row["park_name"]

    print()
    print("=" * 70)
    print(f"[{park_id}] {park_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # 해당 공원의 상위 후보
    # --------------------------------------------------------

    park_candidates = candidates[candidates["park_id"] == park_id].copy()

    park_candidates = (
        park_candidates.sort_values("rank").head(TOP_N).reset_index(drop=True)
    )

    if len(park_candidates) < 2:

        print("비교할 후보가 2개 미만입니다.")

        continue

    # ========================================================
    # 후보 조합 생성
    #
    # 예:
    # 1위 ↔ 2위
    # 1위 ↔ 3위
    # 2위 ↔ 3위
    # ========================================================

    for i in range(len(park_candidates)):

        for j in range(
            i + 1,
            len(park_candidates),
        ):

            candidate_a = park_candidates.iloc[i]

            candidate_b = park_candidates.iloc[j]

            # ------------------------------------------------
            # Polygon 가져오기
            # ------------------------------------------------

            index_a = int(candidate_a["polygon_index"])

            index_b = int(candidate_b["polygon_index"])

            polygon_a = polygons.iloc[index_a]

            polygon_b = polygons.iloc[index_b]

            geom_a = polygon_a.geometry
            geom_b = polygon_b.geometry

            # =================================================
            # Geometry 기본 정보
            # =================================================

            area_a = geom_a.area
            area_b = geom_b.area

            # =================================================
            # Geometry 동일 여부
            # =================================================

            exact_equal = geom_a.equals(geom_b)

            # =================================================
            # 두 Polygon 사이 거리
            # =================================================

            polygon_distance = geom_a.distance(geom_b)

            # =================================================
            # 교집합
            # =================================================

            intersection = geom_a.intersection(geom_b)

            if intersection.is_empty:

                intersection_area = 0.0

            else:

                intersection_area = intersection.area

            # =================================================
            # 각각 기준 겹침 비율
            #
            # A 기준:
            #
            # intersection / A
            #
            # B 기준:
            #
            # intersection / B
            # =================================================

            overlap_ratio_a = intersection_area / area_a if area_a > 0 else 0

            overlap_ratio_b = intersection_area / area_b if area_b > 0 else 0

            # =================================================
            # 작은 Polygon 기준 겹침 비율
            # =================================================

            smaller_area = min(
                area_a,
                area_b,
            )

            overlap_ratio_smaller = (
                intersection_area / smaller_area if smaller_area > 0 else 0
            )

            # =================================================
            # 포함 관계
            # =================================================

            a_contains_b = geom_a.contains(geom_b)

            b_contains_a = geom_b.contains(geom_a)

            # covers는 경계가 맞닿아도 True가 될 수 있어서
            # contains와 함께 확인
            a_covers_b = geom_a.covers(geom_b)

            b_covers_a = geom_b.covers(geom_a)

            # =================================================
            # 접촉 여부
            # =================================================

            touches = geom_a.touches(geom_b)

            # =================================================
            # 교차 여부
            # =================================================

            intersects = geom_a.intersects(geom_b)

            # =================================================
            # 결과 저장
            # =================================================

            results.append(
                {
                    "park_id": park_id,
                    "park_name": park_name,
                    "rank_a": int(candidate_a["rank"]),
                    "polygon_id_a": (candidate_a["polygon_id"]),
                    "polygon_label_a": (candidate_a["polygon_label"]),
                    "rank_b": int(candidate_b["rank"]),
                    "polygon_id_b": (candidate_b["polygon_id"]),
                    "polygon_label_b": (candidate_b["polygon_label"]),
                    "area_a_m2": round(
                        area_a,
                        2,
                    ),
                    "area_b_m2": round(
                        area_b,
                        2,
                    ),
                    "intersection_area_m2": (
                        round(
                            intersection_area,
                            2,
                        )
                    ),
                    "overlap_ratio_a": (
                        round(
                            overlap_ratio_a,
                            6,
                        )
                    ),
                    "overlap_ratio_b": (
                        round(
                            overlap_ratio_b,
                            6,
                        )
                    ),
                    "overlap_ratio_smaller": (
                        round(
                            overlap_ratio_smaller,
                            6,
                        )
                    ),
                    "polygon_distance_m": (
                        round(
                            polygon_distance,
                            6,
                        )
                    ),
                    "exact_equal": (exact_equal),
                    "a_contains_b": (a_contains_b),
                    "b_contains_a": (b_contains_a),
                    "a_covers_b": (a_covers_b),
                    "b_covers_a": (b_covers_a),
                    "touches": touches,
                    "intersects": (intersects),
                }
            )

            # =================================================
            # 콘솔 출력
            # =================================================

            print()

            print(f'{int(candidate_a["rank"])}위 ' f'[{candidate_a["polygon_label"]}]')

            print("        ↕")

            print(f'{int(candidate_b["rank"])}위 ' f'[{candidate_b["polygon_label"]}]')

            print("-" * 70)

            print(f"A 면적               : " f"{area_a:.2f} m²")

            print(f"B 면적               : " f"{area_b:.2f} m²")

            print(f"교집합 면적          : " f"{intersection_area:.2f} m²")

            print(f"A 기준 겹침 비율      : " f"{overlap_ratio_a:.6f}")

            print(f"B 기준 겹침 비율      : " f"{overlap_ratio_b:.6f}")

            print(f"작은 Polygon 기준     : " f"{overlap_ratio_smaller:.6f}")

            print(f"Polygon 간 거리       : " f"{polygon_distance:.6f} m")

            print(f"geometry 동일         : " f"{exact_equal}")

            print(f"A contains B          : " f"{a_contains_b}")

            print(f"B contains A          : " f"{b_contains_a}")

            print(f"A covers B            : " f"{a_covers_b}")

            print(f"B covers A            : " f"{b_covers_a}")

            print(f"touches                : " f"{touches}")

            print(f"intersects             : " f"{intersects}")


# ============================================================
# DataFrame 생성
# ============================================================

analysis = pd.DataFrame(results)


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

analysis.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 요약
# ============================================================

print()
print("=" * 70)
print("분석 결과 요약")
print("=" * 70)

print(
    "비교한 Polygon 쌍:",
    len(analysis),
)


if not analysis.empty:

    print(
        "geometry 완전 동일:",
        analysis["exact_equal"].sum(),
    )

    print(
        "서로 교차:",
        analysis["intersects"].sum(),
    )

    print(
        "서로 접촉:",
        analysis["touches"].sum(),
    )


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
