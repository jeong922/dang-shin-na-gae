from pathlib import Path

import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 기존 데이터 업데이트 전에 백업해둔 parks.csv
OLD_PARKS_CSV = BASE_DIR / "data" / "processed" / "parks_old.csv"

# 최신 데이터로 다시 전처리한 parks.csv
NEW_PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

OUTPUT_CSV = BASE_DIR / "data" / "analysis" / "park_id_changes.csv"


# ============================================================
# 데이터 읽기
# ============================================================

old_parks = pd.read_csv(OLD_PARKS_CSV)
new_parks = pd.read_csv(NEW_PARKS_CSV)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print("기존 공원:", len(old_parks))
print("최신 공원:", len(new_parks))


# ============================================================
# 필요한 컬럼 확인
# ============================================================

required_columns = {"id", "name"}

for label, dataframe in [
    ("기존 데이터", old_parks),
    ("최신 데이터", new_parks),
]:
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{label}에 필요한 컬럼이 없습니다: " f"{sorted(missing_columns)}"
        )


# ============================================================
# 공원명 중복 확인
# ============================================================
#
# 이번 비교는 name을 기준으로 하기 때문에
# 동일한 이름의 공원이 여러 개 있으면 정확한 비교가 어렵다.
# ============================================================

for label, dataframe in [
    ("기존 데이터", old_parks),
    ("최신 데이터", new_parks),
]:
    duplicated_names = dataframe[dataframe["name"].duplicated(keep=False)].sort_values(
        "name"
    )

    if not duplicated_names.empty:
        print()
        print("=" * 70)
        print(f"{label} 공원명 중복")
        print("=" * 70)

        print(duplicated_names[["id", "name"]].to_string(index=False))

        raise ValueError(f"{label}에 동일한 공원명이 여러 개 존재합니다.")


# ============================================================
# 비교용 데이터 생성
# ============================================================

old_info = old_parks[["id", "name"]].rename(
    columns={
        "id": "old_id",
    }
)

new_info = new_parks[["id", "name"]].rename(
    columns={
        "id": "new_id",
    }
)


# ============================================================
# 공원명 기준 병합
# ============================================================
#
# outer join을 사용해서
#
# - 기존/최신 모두 존재
# - 기존에만 존재
# - 최신에만 존재
#
# 를 모두 확인한다.
# ============================================================

comparison = old_info.merge(
    new_info,
    on="name",
    how="outer",
    indicator=True,
)


# ============================================================
# 상태 분류
# ============================================================


def classify_status(row):
    # 기존에는 있었지만 최신 데이터에서는 사라짐
    if row["_merge"] == "left_only":
        return "removed"

    # 최신 데이터에 새롭게 추가됨
    if row["_merge"] == "right_only":
        return "added"

    # 양쪽 모두 존재하며 ID도 동일
    if row["old_id"] == row["new_id"]:
        return "unchanged"

    # 양쪽 모두 존재하지만 ID가 변경됨
    return "id_changed"


comparison["status"] = comparison.apply(
    classify_status,
    axis=1,
)


# merge 상태 컬럼은 더 이상 필요 없음
comparison = comparison.drop(columns=["_merge"])


# ============================================================
# ID 변화량
# ============================================================
#
# 예:
#
# old_id = 10
# new_id = 9
#
# → id_diff = -1
#
# 추가/삭제된 공원은 비교할 ID가 없으므로 NaN.
# ============================================================

comparison["id_diff"] = comparison["new_id"] - comparison["old_id"]


# ============================================================
# 컬럼 순서 정리
# ============================================================

comparison = comparison[
    [
        "name",
        "old_id",
        "new_id",
        "id_diff",
        "status",
    ]
]


# ============================================================
# 보기 좋게 정렬
# ============================================================
#
# 기존 ID가 있는 공원은 old_id 기준.
# 새롭게 추가된 공원은 뒤쪽에 표시한다.
# ============================================================

comparison = comparison.sort_values(
    by=["old_id", "new_id"],
    na_position="last",
).reset_index(drop=True)


# ============================================================
# 결과 요약
# ============================================================

print()
print("=" * 70)
print("ID 비교 결과")
print("=" * 70)

print(comparison["status"].value_counts().to_string())


# ============================================================
# ID 변경 공원
# ============================================================

id_changed = comparison[comparison["status"] == "id_changed"]

print()
print("=" * 70)
print("ID 변경 공원")
print("=" * 70)

print("개수:", len(id_changed))

if id_changed.empty:
    print("없음")
else:
    print()
    print(
        id_changed[
            [
                "name",
                "old_id",
                "new_id",
                "id_diff",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 삭제된 공원
# ============================================================

removed = comparison[comparison["status"] == "removed"]

print()
print("=" * 70)
print("삭제된 공원")
print("=" * 70)

if removed.empty:
    print("없음")
else:
    print(
        removed[
            [
                "name",
                "old_id",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 추가된 공원
# ============================================================

added = comparison[comparison["status"] == "added"]

print()
print("=" * 70)
print("추가된 공원")
print("=" * 70)

if added.empty:
    print("없음")
else:
    print(
        added[
            [
                "name",
                "new_id",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 결과 저장
# ============================================================

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)

comparison.to_csv(
    OUTPUT_CSV,
    index=False,
    encoding="utf-8-sig",
)


print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print("ID 비교 결과:", OUTPUT_CSV)
