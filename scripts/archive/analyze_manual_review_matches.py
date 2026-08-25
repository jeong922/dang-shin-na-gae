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

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "manual_review_analysis.csv"


# ============================================================
# 설정
# ============================================================

TOP_N = 5


# ============================================================
# 데이터 읽기
# ============================================================

classified = pd.read_csv(CLASSIFIED_CSV)

candidates = pd.read_csv(REVIEW_CANDIDATES_CSV)

polygons = gpd.read_file(SHP_PATH)


# ============================================================
# needs_manual_review 대상 추출
# ============================================================

manual_review = classified[classified["classification"] == "needs_manual_review"].copy()


print("=" * 70)
print("분석 대상")
print("=" * 70)

print(
    "needs_manual_review 공원 개수:",
    len(manual_review),
)

print()

print(
    manual_review[
        [
            "park_id",
            "park_name",
            "best_polygon_label",
            "best_name_score",
            "best_distance_m",
            "best_point_inside",
        ]
    ].to_string(index=False)
)


# ============================================================
# 결과 저장
# ============================================================

results = []


# ============================================================
# 공원별 상세 분석
# ============================================================

for _, review_row in manual_review.iterrows():

    park_id = review_row["park_id"]
    park_name = review_row["park_name"]

    print()
    print("=" * 70)
    print(f"[{park_id}] {park_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # 상위 후보 추출
    # --------------------------------------------------------

    park_candidates = candidates[candidates["park_id"] == park_id].copy()

    park_candidates = (
        park_candidates.sort_values("rank").head(TOP_N).reset_index(drop=True)
    )

    if park_candidates.empty:

        print("후보 없음")
        continue

    # ========================================================
    # 후보별 추가 정보 계산
    # ========================================================

    for _, candidate in park_candidates.iterrows():

        polygon_index = int(candidate["polygon_index"])

        polygon = polygons.iloc[polygon_index]

        geometry = polygon.geometry

        # ----------------------------------------------------
        # 면적
        # ----------------------------------------------------

        area_m2 = geometry.area

        # ----------------------------------------------------
        # geometry 타입
        # ----------------------------------------------------

        geometry_type = geometry.geom_type

        # ----------------------------------------------------
        # 대표점
        # ----------------------------------------------------

        representative_point = geometry.representative_point()

        results.append(
            {
                "park_id": park_id,
                "park_name": park_name,
                "rank": int(candidate["rank"]),
                "polygon_index": (polygon_index),
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
                "spatial_score": (candidate["spatial_score"]),
                "distance_m": round(
                    candidate["distance_m"],
                    2,
                ),
                "point_inside": bool(candidate["point_inside"]),
                "polygon_area_m2": round(
                    area_m2,
                    2,
                ),
                "geometry_type": (geometry_type),
                "representative_x": round(
                    representative_point.x,
                    3,
                ),
                "representative_y": round(
                    representative_point.y,
                    3,
                ),
            }
        )

    # ========================================================
    # 콘솔 출력
    # ========================================================

    for _, candidate in park_candidates.iterrows():

        print(
            f'{int(candidate["rank"])}위 | '
            f'{candidate["polygon_label"]} | '
            f'score={candidate["total_score"]:.2f} | '
            f'name={candidate["name_score"]:.2f} | '
            f'spatial={candidate["spatial_score"]} | '
            f'distance={candidate["distance_m"]:.2f}m | '
            f'inside={candidate["point_inside"]}'
        )


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
# 공원별 요약 출력
# ============================================================

print()
print("=" * 70)
print("공원별 1위 후보 요약")
print("=" * 70)


best_candidates = analysis[analysis["rank"] == 1].copy()


print(
    best_candidates[
        [
            "park_id",
            "park_name",
            "polygon_label",
            "name_score",
            "spatial_score",
            "distance_m",
            "point_inside",
            "polygon_area_m2",
            "geometry_type",
        ]
    ].to_string(index=False)
)


# ============================================================
# 저장 완료
# ============================================================

print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
