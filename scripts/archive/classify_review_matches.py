from pathlib import Path

import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

REVIEW_CANDIDATES_CSV = (
    BASE_DIR / "data" / "processed" / "review_candidate_analysis.csv"
)

OUTPUT_CSV = BASE_DIR / "data" / "processed" / "classified_review_matches.csv"


# ============================================================
# 설정
# ============================================================

# 이름이 강하게 일치한다고 볼 기준
STRONG_NAME_SCORE = 130

# 이름이 어느 정도 일치한다고 볼 기준
MODERATE_NAME_SCORE = 50

# 충분히 가까운 거리
CLOSE_DISTANCE_M = 300

# 애매하지만 아직 후보로 볼 수 있는 거리
MEDIUM_DISTANCE_M = 500

# 1위와 2위 점수 차이가 작으면
# 여러 Polygon 또는 애매한 후보로 본다.
AMBIGUOUS_MARGIN = 20


# ============================================================
# 데이터 읽기
# ============================================================

candidates = pd.read_csv(REVIEW_CANDIDATES_CSV)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "후보 행 개수:",
    len(candidates),
)

print(
    "review 공원 개수:",
    candidates["park_id"].nunique(),
)


# ============================================================
# 공원별 분류
# ============================================================

results = []


for park_id, group in candidates.groupby("park_id"):

    group = group.sort_values("rank")

    best = group.iloc[0]

    second = group.iloc[1] if len(group) > 1 else None

    # --------------------------------------------------------
    # 기본 정보
    # --------------------------------------------------------

    park_name = best["park_name"]

    best_score = best["total_score"]

    best_name_score = best["name_score"]

    best_distance = best["distance_m"]

    best_inside = bool(best["point_inside"])

    # --------------------------------------------------------
    # 2위 정보
    # --------------------------------------------------------

    if second is not None:

        second_score = second["total_score"]

        score_margin = best_score - second_score

    else:

        second_score = None
        score_margin = None

    # ========================================================
    # 분류 규칙
    # ========================================================

    classification = None
    reason = None

    # --------------------------------------------------------
    # 1. 여러 Polygon 가능성
    #
    # 이름이 강하게 같고
    # 1위 / 2위 점수가 거의 같으면
    # 같은 공원을 여러 Polygon이 나타낼 가능성이 큼
    # --------------------------------------------------------

    if (
        second is not None
        and score_margin <= AMBIGUOUS_MARGIN
        and best_name_score >= STRONG_NAME_SCORE
        and second["name_score"] >= STRONG_NAME_SCORE
    ):

        classification = "multiple_polygons"

        reason = "1위와 2위 후보의 이름 점수가 모두 높고 " "총점 차이가 작음"

    # --------------------------------------------------------
    # 2. 이름이 강하고 충분히 가까움
    # --------------------------------------------------------

    elif best_name_score >= STRONG_NAME_SCORE and best_distance <= CLOSE_DISTANCE_M:

        classification = "likely_match"

        reason = "이름 일치도가 높고 " "Polygon까지 거리도 가까움"

    # --------------------------------------------------------
    # 3. Polygon 내부 + 이름도 어느 정도 맞음
    # --------------------------------------------------------

    elif best_inside and best_name_score >= MODERATE_NAME_SCORE:

        classification = "likely_match"

        reason = "공원 좌표가 Polygon 내부에 있고 " "이름도 일정 수준 이상 일치"

    # --------------------------------------------------------
    # 4. 이름은 강하지만 다소 멀리 떨어짐
    #
    # 북한산 / 수락산 / 와우 / 개화 같은 케이스
    # --------------------------------------------------------

    elif best_name_score >= STRONG_NAME_SCORE and best_distance <= MEDIUM_DISTANCE_M:

        classification = "likely_match"

        reason = "이름 일치도는 매우 높지만 " "공원 좌표가 Polygon 밖에 있음"

    # --------------------------------------------------------
    # 5. Polygon 내부인데 이름 근거가 없음
    #
    # 북서울꿈의숲 → 오동
    # 허브천문공원 → 일자산
    #
    # 실제 관계 확인 필요
    # --------------------------------------------------------

    elif best_inside and best_name_score < MODERATE_NAME_SCORE:

        classification = "needs_manual_review"

        reason = "공원 좌표는 Polygon 내부지만 " "이름 일치 근거가 약함"

    # --------------------------------------------------------
    # 6. 이름이 강하지만 너무 멀리 떨어짐
    #
    # 용두근린공원 → 용두희망
    # 율현공원 → 율현동
    #
    # 이름만으로 자동 확정하기 위험
    # --------------------------------------------------------

    elif best_name_score >= STRONG_NAME_SCORE and best_distance > MEDIUM_DISTANCE_M:

        classification = "needs_manual_review"

        reason = "이름은 매우 유사하지만 " "Polygon과 거리가 너무 멂"

    # --------------------------------------------------------
    # 7. 이름도 약하고 내부도 아니고
    # 거리도 애매한 경우
    #
    # 서울식물원
    # 경춘선숲길
    # 문화비축기지 등
    # --------------------------------------------------------

    else:

        classification = "no_reliable_match"

        reason = "이름 일치도와 공간적 근거가 " "모두 충분하지 않음"

    # ========================================================
    # 결과 저장
    # ========================================================

    results.append(
        {
            "park_id": park_id,
            "park_name": park_name,
            "classification": classification,
            "reason": reason,
            "best_polygon_id": best["polygon_id"],
            "best_polygon_label": best["polygon_label"],
            "best_total_score": round(
                best_score,
                2,
            ),
            "best_name_score": round(
                best_name_score,
                2,
            ),
            "best_spatial_score": best["spatial_score"],
            "best_distance_m": round(
                best_distance,
                2,
            ),
            "best_point_inside": best_inside,
            "second_polygon_id": (second["polygon_id"] if second is not None else None),
            "second_polygon_label": (
                second["polygon_label"] if second is not None else None
            ),
            "second_total_score": (
                round(
                    second_score,
                    2,
                )
                if second_score is not None
                else None
            ),
            "score_margin": (
                round(
                    score_margin,
                    2,
                )
                if score_margin is not None
                else None
            ),
        }
    )


# ============================================================
# DataFrame 생성
# ============================================================

classified = pd.DataFrame(results)


# ============================================================
# 정렬
# ============================================================

classification_order = {
    "likely_match": 1,
    "multiple_polygons": 2,
    "needs_manual_review": 3,
    "no_reliable_match": 4,
}


classified["classification_order"] = classified["classification"].map(
    classification_order
)


classified = classified.sort_values(
    [
        "classification_order",
        "park_id",
    ]
)


classified = classified.drop(columns=["classification_order"])


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

classified.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("분류 결과")
print("=" * 70)

print(classified["classification"].value_counts().to_string())


# ============================================================
# 유형별 출력
# ============================================================

for classification in [
    "likely_match",
    "multiple_polygons",
    "needs_manual_review",
    "no_reliable_match",
]:

    subset = classified[classified["classification"] == classification]

    print()
    print("=" * 70)
    print(classification)
    print("=" * 70)

    if subset.empty:

        print("없음")
        continue

    print(
        subset[
            [
                "park_id",
                "park_name",
                "best_polygon_label",
                "best_name_score",
                "best_distance_m",
                "best_point_inside",
                "score_margin",
                "reason",
            ]
        ].to_string(index=False)
    )


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
