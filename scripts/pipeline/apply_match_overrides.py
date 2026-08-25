from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 자동 매칭 결과
AUTO_MATCHES_CSV = BASE_DIR / "data" / "processed" / "official_park_matches.csv"

# 중복 제거된 Polygon
SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

# 최종 매칭 결과
OUTPUT_CSV = BASE_DIR / "data" / "processed" / "park_polygon_matches_final.csv"


# ============================================================
# 설정
# ============================================================

EXPECTED_PARK_COUNT = 130

EXPECTED_MATCHED_COUNT = 111
EXPECTED_NO_MATCH_COUNT = 19


# ============================================================
# 수동 Override
# ============================================================
#
# type
#
# auto_best
#     match_park_polygons.py가 뽑은 1위 후보를 사용
#
# labels
#     지정한 LABEL의 여러 Polygon을 모두 사용
#
# no_match
#     최종적으로 Polygon을 연결하지 않음
#
# ============================================================

OVERRIDES = {
    # ========================================================
    # 자동 1위 후보를 수동 검증 후 확정
    # ========================================================
    17: {
        "type": "auto_best",
        "method": "manual_single_polygon",
        "note": ("보라매공원 후보 2개가 약 97% 겹쳐 " "자동 1위 Polygon을 대표로 사용"),
    },
    34: {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("허준공원은 구암근린공원의 다른 명칭으로 " "확인하여 Polygon 매칭"),
    },
    78: {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("삼일근린공원과 근린공원(3.1)은 " "명칭 표기 차이로 판단"),
    },
    91: {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("북서울꿈의숲은 오동근린공원 영역과 " "대응하는 것으로 판단"),
    },
    106: {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": (
            "문화예술공원은 시민의숲 관리구역 일부로 확인되어 "
            "시민의숲 상위 Polygon 사용"
        ),
    },
    114: {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("아차산공원은 용마 도시자연공원 계열 " "Polygon을 상위 영역으로 사용"),
    },
    122: {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("허브천문공원은 일자산 도시자연공원 " "내부 시설로 판단"),
    },
    125: {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("서일대뒷산공원은 용마 도시자연공원 " "내부 영역으로 판단"),
    },
    69: {
        "type": "auto_best",
        "method": "manual_likely_match",
        "note": (
            "북한산 이름이 강하게 일치하고 " "대규모 도시자연공원 Polygon으로 판단"
        ),
    },
    84: {
        "type": "auto_best",
        "method": "manual_likely_match",
        "note": (
            "수락산 이름이 강하게 일치하고 " "대규모 도시자연공원 Polygon으로 판단"
        ),
    },
    # ========================================================
    # 하나의 공원에 여러 Polygon 사용
    # ========================================================
    115: {
        "type": "labels",
        "labels": [
            "도시자연공원(인능산1<시공원>)",
            "도시자연공원(인능산2<시공원>)",
            "도시자연공원(인능산3<시공원>)",
        ],
        "method": "manual_multi_polygon",
        "note": (
            "인능산도시자연공원은 인능산1, 인능산2, " "인능산3 Polygon을 함께 사용"
        ),
    },
    # ========================================================
    # 최종 no_match
    # ========================================================
    7: {
        "type": "no_match",
        "method": "automatic_unmatched",
        "note": ("자동 매칭 단계에서 신뢰할 수 있는 " "Polygon 후보를 찾지 못함"),
    },
    28: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "개웅산근린공원과 어린이공원(개웅)은 "
            "규모와 공원 유형이 달라 별개 공원으로 판단"
        ),
    },
    45: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "도곡목련·도곡까치 어린이공원은 " "도곡근린공원과 별개의 공원으로 판단"
        ),
    },
    63: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("이름 일치도와 공간적 근거가 부족하여 " "신뢰할 수 있는 Polygon 없음"),
    },
    90: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("서울창포원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    93: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("중랑캠핑숲과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    96: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("금천폭포근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    100: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "어린이공원(용두희망)은 약 1.3km 떨어져 있어 " "동일 공원 근거가 부족함"
        ),
    },
    102: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": ("와우근린공원과 어린이공원(와우)은 " "별개의 공원으로 확인"),
    },
    104: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("달맞이근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    111: {
        "type": "no_match",
        "method": "automatic_unmatched",
        "note": ("자동 매칭 단계에서 신뢰할 수 있는 " "Polygon 후보를 찾지 못함"),
    },
    113: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "개화근린공원과 어린이공원(개화)은 "
            "규모와 공원 유형이 달라 별개 공원으로 판단"
        ),
    },
    116: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("구룡산도시자연공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    118: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("향림근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    120: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("광평근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    127: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("문화비축기지와 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    128: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("경춘선숲길과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    129: {
        "type": "no_match",
        "method": "manual_no_match",
        "note": ("마을마당(율현동)은 약 910m 떨어져 있어 " "동일 공원 근거가 부족함"),
    },
    131: {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("서울식물원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
}


# ============================================================
# 데이터 읽기
# ============================================================

auto_matches = pd.read_csv(AUTO_MATCHES_CSV)

polygons = gpd.read_file(SHP_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "자동 매칭 결과:",
    len(auto_matches),
)

print(
    "Polygon:",
    len(polygons),
)

print(
    "Override:",
    len(OVERRIDES),
)


# ============================================================
# Override ID 검증
# ============================================================

auto_park_ids = set(auto_matches["park_id"].astype(int).tolist())

override_ids = set(OVERRIDES.keys())


unknown_override_ids = override_ids - auto_park_ids


if unknown_override_ids:

    raise ValueError(
        "자동 매칭 결과에 존재하지 않는 "
        f"Override park_id: "
        f"{sorted(unknown_override_ids)}"
    )


# ============================================================
# 최종 결과 생성
# ============================================================

results = []


for _, row in auto_matches.iterrows():

    park_id = int(row["park_id"])

    park_name = row["park_name"]

    # ========================================================
    # Override 적용
    # ========================================================

    if park_id in OVERRIDES:

        override = OVERRIDES[park_id]

        override_type = override["type"]

        # ----------------------------------------------------
        # 1. no_match
        # ----------------------------------------------------

        if override_type == "no_match":

            results.append(
                {
                    "park_id": park_id,
                    "park_name": park_name,
                    "match_status": "no_match",
                    "match_method": override["method"],
                    "polygon_count": 0,
                    "polygon_ids": None,
                    "polygon_labels": None,
                    "note": override["note"],
                }
            )

            continue

        # ----------------------------------------------------
        # 2. 자동 1위 후보 사용
        # ----------------------------------------------------

        if override_type == "auto_best":

            polygon_id = row["polygon_id"]

            polygon_label = row["polygon_label"]

            if pd.isna(polygon_id):

                raise ValueError(
                    f"[{park_id}] {park_name}: " "auto_best인데 polygon_id가 없습니다."
                )

            # 실제 정제 Shapefile에도 존재하는지 확인
            selected = polygons[polygons["ID"].astype(str) == str(polygon_id)]

            if selected.empty:

                raise ValueError(
                    f"[{park_id}] {park_name}: "
                    f"Polygon ID {polygon_id}가 "
                    "정제 Shapefile에 없습니다."
                )

            results.append(
                {
                    "park_id": park_id,
                    "park_name": park_name,
                    "match_status": "matched",
                    "match_method": override["method"],
                    "polygon_count": 1,
                    "polygon_ids": str(polygon_id),
                    "polygon_labels": (polygon_label),
                    "note": override["note"],
                }
            )

            continue

        # ----------------------------------------------------
        # 3. LABEL로 여러 Polygon 선택
        # ----------------------------------------------------

        if override_type == "labels":

            labels = override["labels"]

            selected_rows = []

            for label in labels:

                selected = polygons[polygons["LABEL"] == label]

                if selected.empty:

                    raise ValueError(
                        f"[{park_id}] {park_name}: "
                        f"LABEL '{label}'을 "
                        "Shapefile에서 찾을 수 없습니다."
                    )

                if len(selected) > 1:

                    raise ValueError(
                        f"[{park_id}] {park_name}: "
                        f"LABEL '{label}'이 "
                        f"{len(selected)}개 존재합니다."
                    )

                selected_rows.append(selected.iloc[0])

            polygon_ids = [str(selected["ID"]) for selected in selected_rows]

            polygon_labels = [str(selected["LABEL"]) for selected in selected_rows]

            results.append(
                {
                    "park_id": park_id,
                    "park_name": park_name,
                    "match_status": "matched",
                    "match_method": override["method"],
                    "polygon_count": len(polygon_ids),
                    "polygon_ids": "|".join(polygon_ids),
                    "polygon_labels": "|".join(polygon_labels),
                    "note": override["note"],
                }
            )

            continue

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"알 수 없는 Override type "
            f"'{override_type}'"
        )

    # ========================================================
    # Override 없는 공원
    #
    # high인 경우만 자동 확정
    # ========================================================

    if row["status"] == "high":

        results.append(
            {
                "park_id": park_id,
                "park_name": park_name,
                "match_status": "matched",
                "match_method": ("automatic_high"),
                "polygon_count": 1,
                "polygon_ids": str(row["polygon_id"]),
                "polygon_labels": (row["polygon_label"]),
                "note": ("자동 매칭 high"),
            }
        )

        continue

    # --------------------------------------------------------
    # review / unmatched인데 Override가 없다면
    # 빠뜨린 예외가 있다는 의미
    # --------------------------------------------------------

    raise ValueError(
        f"[{park_id}] {park_name}: "
        f"자동 status={row['status']}인데 "
        "Override가 정의되지 않았습니다."
    )


# ============================================================
# DataFrame 생성
# ============================================================

final_matches = pd.DataFrame(results)


final_matches = final_matches.sort_values("park_id").reset_index(drop=True)


# ============================================================
# 검증
# ============================================================

print()
print("=" * 70)
print("검증")
print("=" * 70)


# ------------------------------------------------------------
# 전체 개수
# ------------------------------------------------------------

if len(final_matches) != EXPECTED_PARK_COUNT:

    raise ValueError(
        f"공원 개수가 " f"{EXPECTED_PARK_COUNT}개가 아닙니다: " f"{len(final_matches)}"
    )


# ------------------------------------------------------------
# park_id 중복
# ------------------------------------------------------------

duplicated = final_matches[final_matches["park_id"].duplicated(keep=False)]


if not duplicated.empty:

    raise ValueError("중복 park_id가 존재합니다.")


# ------------------------------------------------------------
# matched 검증
# ------------------------------------------------------------

matched = final_matches[final_matches["match_status"] == "matched"]


invalid_matched = matched[
    matched["polygon_ids"].isna() | (matched["polygon_count"] <= 0)
]


if not invalid_matched.empty:

    print(
        invalid_matched[
            [
                "park_id",
                "park_name",
                "polygon_count",
                "polygon_ids",
            ]
        ].to_string(index=False)
    )

    raise ValueError("matched인데 Polygon 정보가 " "없는 공원이 존재합니다.")


# ------------------------------------------------------------
# no_match 검증
# ------------------------------------------------------------

no_match = final_matches[final_matches["match_status"] == "no_match"]


invalid_no_match = no_match[no_match["polygon_count"] != 0]


if not invalid_no_match.empty:

    raise ValueError("no_match인데 polygon_count가 " "0이 아닌 공원이 존재합니다.")


# ------------------------------------------------------------
# 기존 결과 재현 검증
# ------------------------------------------------------------

matched_count = len(matched)

no_match_count = len(no_match)


if matched_count != EXPECTED_MATCHED_COUNT:

    raise ValueError(
        f"matched가 " f"{EXPECTED_MATCHED_COUNT}개가 아닙니다: " f"{matched_count}"
    )


if no_match_count != EXPECTED_NO_MATCH_COUNT:

    raise ValueError(
        f"no_match가 " f"{EXPECTED_NO_MATCH_COUNT}개가 아닙니다: " f"{no_match_count}"
    )


print(
    "전체 공원:",
    len(final_matches),
)

print(
    "matched:",
    matched_count,
)

print(
    "no_match:",
    no_match_count,
)


# ============================================================
# 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

final_matches.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 결과 출력
# ============================================================

print()
print("=" * 70)
print("최종 매칭 결과")
print("=" * 70)

print(final_matches["match_status"].value_counts().to_string())


print()
print("=" * 70)
print("매칭 방식")
print("=" * 70)

print(final_matches["match_method"].value_counts().to_string())


print()
print("=" * 70)
print("Manual Override")
print("=" * 70)


manual_results = final_matches[final_matches["park_id"].isin(OVERRIDES.keys())]


print(
    manual_results[
        [
            "park_id",
            "park_name",
            "match_status",
            "match_method",
            "polygon_count",
            "polygon_labels",
            "note",
        ]
    ].to_string(index=False)
)


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
