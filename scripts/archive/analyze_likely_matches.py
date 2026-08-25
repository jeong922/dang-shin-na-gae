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

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "likely_match_analysis.csv"


# ============================================================
# 설정
# ============================================================

# 공원별 상위 후보 몇 개를 확인할지
TOP_N = 5


# ============================================================
# 데이터 읽기
# ============================================================

classified = pd.read_csv(CLASSIFIED_CSV)

candidates = pd.read_csv(REVIEW_CANDIDATES_CSV)

polygons = gpd.read_file(SHP_PATH)


# ============================================================
# likely_match 대상 추출
# ============================================================

likely_matches = classified[classified["classification"] == "likely_match"].copy()


print("=" * 70)
print("분석 대상")
print("=" * 70)

print(
    "likely_match 공원 개수:",
    len(likely_matches),
)

print()

print(
    likely_matches[
        [
            "park_id",
            "park_name",
            "best_polygon_label",
            "best_name_score",
            "best_distance_m",
            "best_point_inside",
            "score_margin",
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

for _, likely_row in likely_matches.iterrows():

    park_id = likely_row["park_id"]
    park_name = likely_row["park_name"]

    print()
    print("=" * 70)
    print(f"[{park_id}] {park_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # 해당 공원의 후보 가져오기
    # --------------------------------------------------------

    park_candidates = candidates[candidates["park_id"] == park_id].copy()

    park_candidates = (
        park_candidates.sort_values("rank").head(TOP_N).reset_index(drop=True)
    )

    if park_candidates.empty:

        print("후보 없음")

        continue

    # ========================================================
    # 후보별 분석
    # ========================================================

    for _, candidate in park_candidates.iterrows():

        polygon_index = int(candidate["polygon_index"])

        polygon = polygons.iloc[polygon_index]

        geometry = polygon.geometry

        # ----------------------------------------------------
        # Polygon 면적
        # ----------------------------------------------------

        area_m2 = geometry.area

        # ----------------------------------------------------
        # Geometry 타입
        # ----------------------------------------------------

        geometry_type = geometry.geom_type

        # ----------------------------------------------------
        # 후보 정보 저장
        # ----------------------------------------------------

        results.append(
            {
                "park_id": park_id,
                "park_name": park_name,
                "rank": int(candidate["rank"]),
                "polygon_index": polygon_index,
                "polygon_id": candidate["polygon_id"],
                "polygon_label": candidate["polygon_label"],
                "total_score": round(
                    candidate["total_score"],
                    2,
                ),
                "name_score": round(
                    candidate["name_score"],
                    2,
                ),
                "spatial_score": candidate["spatial_score"],
                "distance_m": round(
                    candidate["distance_m"],
                    2,
                ),
                "point_inside": bool(candidate["point_inside"]),
                "polygon_area_m2": round(
                    area_m2,
                    2,
                ),
                "geometry_type": geometry_type,
            }
        )

    # ========================================================
    # 콘솔 출력
    # ========================================================

    for _, candidate in park_candidates.iterrows():

        polygon_index = int(candidate["polygon_index"])

        polygon = polygons.iloc[polygon_index]

        print(
            f'{int(candidate["rank"])}위 | '
            f'{candidate["polygon_label"]} | '
            f'score={candidate["total_score"]:.2f} | '
            f'name={candidate["name_score"]:.2f} | '
            f'spatial={candidate["spatial_score"]} | '
            f'distance={candidate["distance_m"]:.2f}m | '
            f'inside={candidate["point_inside"]} | '
            f"area={polygon.geometry.area:.2f}m²"
        )


# ============================================================
# DataFrame 생성
# ============================================================

analysis = pd.DataFrame(results)


# ============================================================
# 1위와 2위 비교 정보
# ============================================================

comparison_results = []


for park_id, group in analysis.groupby("park_id"):

    group = group.sort_values("rank")

    best = group.iloc[0]

    second = group.iloc[1] if len(group) >= 2 else None

    if second is not None:

        score_margin = best["total_score"] - second["total_score"]

        distance_margin = second["distance_m"] - best["distance_m"]

    else:

        score_margin = None
        distance_margin = None

    comparison_results.append(
        {
            "park_id": park_id,
            "park_name": best["park_name"],
            "best_polygon_label": best["polygon_label"],
            "best_total_score": best["total_score"],
            "best_name_score": best["name_score"],
            "best_distance_m": best["distance_m"],
            "best_point_inside": best["point_inside"],
            "best_polygon_area_m2": best["polygon_area_m2"],
            "second_polygon_label": (
                second["polygon_label"] if second is not None else None
            ),
            "second_total_score": (
                second["total_score"] if second is not None else None
            ),
            "score_margin": (
                round(
                    score_margin,
                    2,
                )
                if score_margin is not None
                else None
            ),
            "distance_margin_m": (
                round(
                    distance_margin,
                    2,
                )
                if distance_margin is not None
                else None
            ),
        }
    )


comparison = pd.DataFrame(comparison_results)


# ============================================================
# CSV 저장
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
# 1위 후보 요약
# ============================================================

print()
print("=" * 70)
print("1위 후보 요약")
print("=" * 70)

print(
    comparison[
        [
            "park_id",
            "park_name",
            "best_polygon_label",
            "best_name_score",
            "best_distance_m",
            "best_point_inside",
            "best_polygon_area_m2",
            "second_polygon_label",
            "score_margin",
            "distance_margin_m",
        ]
    ].to_string(index=False)
)


# ============================================================
# 간단한 검증 포인트 출력
# ============================================================

print()
print("=" * 70)
print("검토 포인트")
print("=" * 70)


for _, row in comparison.iterrows():

    print()

    print(f'[{row["park_id"]}] ' f'{row["park_name"]}')

    print(f"  1위: " f'{row["best_polygon_label"]}')

    print(f"  이름 점수: " f'{row["best_name_score"]}')

    print(f"  거리: " f'{row["best_distance_m"]:.2f}m')

    print(f"  Polygon 면적: " f'{row["best_polygon_area_m2"]:.2f}m²')

    print(f"  2위와 점수 차이: " f'{row["score_margin"]}')


# ============================================================
# 저장 완료
# ============================================================

print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
