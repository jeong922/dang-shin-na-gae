from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# match_park_polygons.py 결과
AUTO_MATCHES_CSV = BASE_DIR / "data" / "processed" / "official_park_matches.csv"

# 중복 제거된 서울시 Polygon
SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

# 최종 매칭 결과
OUTPUT_CSV = BASE_DIR / "data" / "processed" / "park_polygon_matches_final.csv"


# ============================================================
# 수동 Override
# ============================================================
#
# 중요:
# park_id가 아니라 park_name을 기준으로 관리한다.
#
# 서울시 원본 데이터의 연번(id)은
# 공원이 추가/삭제되면 변경될 수 있기 때문이다.
#
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
#     서울시 Shapefile에서는 신뢰할 수 있는 Polygon을
#     확정하지 않음
#
# ============================================================

OVERRIDES = {
    # ========================================================
    # 자동 1위 후보를 수동 검증 후 확정
    # ========================================================
    "보라매공원": {
        "type": "auto_best",
        "method": "manual_single_polygon",
        "note": ("보라매공원 후보 2개가 약 97% 겹쳐 " "자동 1위 Polygon을 대표로 사용"),
    },
    "허준공원": {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("허준공원은 구암근린공원의 다른 명칭으로 " "확인하여 Polygon 매칭"),
    },
    "삼일근린공원": {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("삼일근린공원과 근린공원(3.1)은 " "명칭 표기 차이로 판단"),
    },
    "북서울꿈의숲": {
        "type": "auto_best",
        "method": "manual_alias",
        "note": ("북서울꿈의숲은 오동근린공원 영역과 " "대응하는 것으로 판단"),
    },
    "문화예술공원": {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": (
            "문화예술공원은 시민의숲 관리구역 일부로 확인되어 "
            "시민의숲 상위 Polygon 사용"
        ),
    },
    "아차산공원": {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("아차산공원은 용마 도시자연공원 계열 " "Polygon을 상위 영역으로 사용"),
    },
    "허브천문공원": {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("허브천문공원은 일자산 도시자연공원 " "내부 시설로 판단"),
    },
    "서일대뒷산공원": {
        "type": "auto_best",
        "method": "manual_parent_polygon",
        "note": ("서일대뒷산공원은 용마 도시자연공원 " "내부 영역으로 판단"),
    },
    "북한산국립공원": {
        "type": "auto_best",
        "method": "manual_likely_match",
        "note": (
            "북한산 이름이 강하게 일치하고 " "대규모 도시자연공원 Polygon으로 판단"
        ),
    },
    "수락산도시자연공원": {
        "type": "auto_best",
        "method": "manual_likely_match",
        "note": (
            "수락산 이름이 강하게 일치하고 " "대규모 도시자연공원 Polygon으로 판단"
        ),
    },
    # ========================================================
    # 하나의 공원에 여러 Polygon 사용
    # ========================================================
    "인능산도시자연공원": {
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
    "진관근린공원(구파발폭포)": {
        "type": "no_match",
        "method": "automatic_unmatched",
        "note": ("자동 매칭 단계에서 신뢰할 수 있는 " "Polygon 후보를 찾지 못함"),
    },
    "개웅산근린공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "개웅산근린공원과 어린이공원(개웅)은 "
            "규모와 공원 유형이 달라 별개 공원으로 판단"
        ),
    },
    "답십리근린공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": (
            "자동 후보인 마을마당(탄천)은 이름이 일치하지 않고 "
            "대표 좌표에서도 약 457m 떨어져 있어 "
            "신뢰할 수 있는 Polygon으로 확정하지 않음"
        ),
    },
    "도곡근린공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "도곡목련·도곡까치 어린이공원은 " "도곡근린공원과 별개의 공원으로 판단"
        ),
    },
    "온수도시자연공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("이름 일치도와 공간적 근거가 부족하여 " "신뢰할 수 있는 Polygon 없음"),
    },
    "서울창포원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("서울창포원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "중랑캠핑숲": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("중랑캠핑숲과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "금천폭포근린공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("금천폭포근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "용두근린공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "어린이공원(용두희망)은 약 1.3km 떨어져 있어 " "동일 공원 근거가 부족함"
        ),
    },
    "와우근린공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": ("와우근린공원과 어린이공원(와우)은 " "별개의 공원으로 확인"),
    },
    "달맞이근린공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("달맞이근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "서오능도시자연공원": {
        "type": "no_match",
        "method": "automatic_unmatched",
        "note": ("자동 매칭 단계에서 신뢰할 수 있는 " "Polygon 후보를 찾지 못함"),
    },
    "개화근린공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": (
            "개화근린공원과 어린이공원(개화)은 "
            "규모와 공원 유형이 달라 별개 공원으로 판단"
        ),
    },
    "구룡산도시자연공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("구룡산도시자연공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "향림근린공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("향림근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "광평근린공원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("광평근린공원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "문화비축기지": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("문화비축기지와 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    "경춘선숲길": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("경춘선숲길과 신뢰할 수 있게 대응되는 " "서울시 Polygon을 찾지 못함"),
    },
    "율현공원": {
        "type": "no_match",
        "method": "manual_no_match",
        "note": ("마을마당(율현동)은 약 910m 떨어져 있어 " "동일 공원 근거가 부족함"),
    },
    "서울식물원": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": ("서울식물원과 신뢰할 수 있게 대응되는 " "Polygon을 찾지 못함"),
    },
    # --------------------------------------------------------
    # 최신 데이터 신규 공원
    # --------------------------------------------------------
    "경의선숲길": {
        "type": "no_match",
        "method": "manual_no_reliable_match",
        "note": (
            "자동 후보인 근린공원(궁동)은 이름이 일치하지 않고 "
            "경의선숲길과 동일 공원이라는 근거가 없어 "
            "서울시 Polygon을 확정하지 않음"
        ),
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

print("자동 매칭 결과:", len(auto_matches))
print("Polygon:", len(polygons))
print("Override:", len(OVERRIDES))


# ============================================================
# 기본 데이터 검증
# ============================================================

required_columns = {
    "park_id",
    "park_name",
    "polygon_id",
    "polygon_label",
    "status",
}

missing_columns = required_columns - set(auto_matches.columns)


if missing_columns:

    raise ValueError(
        "official_park_matches.csv에 필요한 컬럼이 없습니다: "
        f"{sorted(missing_columns)}"
    )


# ------------------------------------------------------------
# park_id 중복 검사
# ------------------------------------------------------------

duplicated_ids = auto_matches[auto_matches["park_id"].duplicated(keep=False)]


if not duplicated_ids.empty:

    print(
        duplicated_ids[
            [
                "park_id",
                "park_name",
            ]
        ].to_string(index=False)
    )

    raise ValueError("official_park_matches.csv에 중복 park_id가 존재합니다.")


# ------------------------------------------------------------
# park_name 중복 검사
#
# 현재 Override가 이름 기준이므로
# 동일 이름이 여러 개라면 안전하게 중단한다.
# ------------------------------------------------------------

duplicated_names = auto_matches[auto_matches["park_name"].duplicated(keep=False)]


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
        "이름 기반 Override를 안전하게 적용할 수 없습니다."
    )


# ============================================================
# Override 이름 검증
# ============================================================

auto_park_names = set(auto_matches["park_name"].astype(str).tolist())

override_names = set(OVERRIDES.keys())


unknown_override_names = override_names - auto_park_names


if unknown_override_names:

    raise ValueError(
        "자동 매칭 결과에 존재하지 않는 "
        "Override 공원명: "
        f"{sorted(unknown_override_names)}"
    )


# ============================================================
# 최종 결과 생성
# ============================================================

results = []


for _, row in auto_matches.iterrows():

    park_id = int(row["park_id"])

    park_name = str(row["park_name"])

    # ========================================================
    # Override 적용
    # ========================================================

    if park_name in OVERRIDES:

        override = OVERRIDES[park_name]

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
                    "polygon_labels": polygon_label,
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

        # ----------------------------------------------------
        # 알 수 없는 Override
        # ----------------------------------------------------

        raise ValueError(
            f"[{park_id}] {park_name}: "
            f"알 수 없는 Override type "
            f"'{override_type}'"
        )

    # ========================================================
    # Override 없는 공원
    #
    # 자동 매칭 결과가 high인 경우만 자동 확정한다.
    # ========================================================

    if row["status"] == "high":

        polygon_id = row["polygon_id"]

        polygon_label = row["polygon_label"]

        if pd.isna(polygon_id):

            raise ValueError(
                f"[{park_id}] {park_name}: " "status=high인데 polygon_id가 없습니다."
            )

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
                "match_method": "automatic_high",
                "polygon_count": 1,
                "polygon_ids": str(polygon_id),
                "polygon_labels": polygon_label,
                "note": "자동 매칭 high",
            }
        )

        continue

    # --------------------------------------------------------
    # review / unmatched인데 Override가 없다면
    # 새로운 검토 대상이 생겼다는 의미
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
# 전체 공원이 한 번씩 처리됐는지 확인
#
# 숫자 130 / 132를 하드코딩하지 않고
# official_park_matches.csv와 직접 비교한다.
# ------------------------------------------------------------

if len(final_matches) != len(auto_matches):

    raise ValueError(
        "최종 매칭 공원 수가 자동 매칭 결과와 다릅니다: "
        f"{len(final_matches)} / {len(auto_matches)}"
    )


# ------------------------------------------------------------
# park_id 집합 동일 여부
# ------------------------------------------------------------

auto_ids = set(auto_matches["park_id"].astype(int).tolist())

final_ids = set(final_matches["park_id"].astype(int).tolist())


if auto_ids != final_ids:

    missing_ids = sorted(auto_ids - final_ids)

    extra_ids = sorted(final_ids - auto_ids)

    raise ValueError(
        "최종 결과의 park_id 구성이 다릅니다.\n"
        f"누락: {missing_ids}\n"
        f"추가: {extra_ids}"
    )


# ------------------------------------------------------------
# park_id 중복
# ------------------------------------------------------------

duplicated = final_matches[final_matches["park_id"].duplicated(keep=False)]


if not duplicated.empty:

    print(
        duplicated[
            [
                "park_id",
                "park_name",
            ]
        ].to_string(index=False)
    )

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

    print(
        invalid_no_match[
            [
                "park_id",
                "park_name",
                "polygon_count",
            ]
        ].to_string(index=False)
    )

    raise ValueError("no_match인데 polygon_count가 " "0이 아닌 공원이 존재합니다.")


# ------------------------------------------------------------
# 상태 개수 출력
#
# 이전 코드처럼 matched=111 / no_match=19를
# 고정값으로 검사하지 않는다.
#
# 공원 원본이 갱신되면 이 숫자 자체가 달라질 수 있다.
# ------------------------------------------------------------

matched_count = len(matched)

no_match_count = len(no_match)


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


# ============================================================
# Manual Override 결과
# ============================================================

print()
print("=" * 70)
print("Manual Override")
print("=" * 70)


manual_results = final_matches[final_matches["park_name"].isin(OVERRIDES.keys())]


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


# ============================================================
# no_match 목록
# ============================================================

print()
print("=" * 70)
print("최종 no_match")
print("=" * 70)


if no_match.empty:

    print("없음")

else:

    print(
        no_match[
            [
                "park_id",
                "park_name",
                "match_method",
                "note",
            ]
        ].to_string(index=False)
    )


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(OUTPUT_CSV)
