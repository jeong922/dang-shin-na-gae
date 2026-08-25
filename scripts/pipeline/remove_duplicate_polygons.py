from pathlib import Path

import geopandas as gpd
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 원본 Shapefile
SHP_PATH = BASE_DIR / "data" / "seoul_parks" / "seoul_parks.shp"

# 중복 제거된 Shapefile 저장 폴더
OUTPUT_DIR = BASE_DIR / "data" / "seoul_parks" / "deduplicated"

OUTPUT_SHP = OUTPUT_DIR / "seoul_parks_deduplicated.shp"

# 어떤 Polygon을 제거했는지 기록
REMOVED_CSV = BASE_DIR / "data" / "processed" / "removed_duplicate_polygons.csv"


# ============================================================
# 설정
# ============================================================

# 작은 Polygon 기준으로 이 비율 이상 겹치면
# 사실상 동일한 Polygon 후보로 판단
OVERLAP_THRESHOLD = 0.999999

# LABEL까지 동일한 경우에만 자동 제거
REQUIRE_SAME_LABEL = True


# ============================================================
# Union-Find
# ============================================================


class UnionFind:
    """
    중복 관계를 하나의 그룹으로 묶기 위한 자료구조.

    예:
        A ↔ B
        B ↔ C

    라면 A, B, C를 하나의 중복 그룹으로 묶는다.
    """

    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x

        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])

        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        if root_a != root_b:
            self.parent[root_b] = root_a


# ============================================================
# 중복 Polygon 탐색
# ============================================================


def find_duplicate_polygons(polygons):
    """
    Polygon끼리 직접 비교하여 중복 후보를 찾는다.

    중복 조건:
    1. 두 Polygon이 서로 교차
    2. 작은 Polygon 기준 겹침 비율이 기준 이상
    3. REQUIRE_SAME_LABEL=True이면 LABEL도 동일

    반환:
        중복 후보 쌍 DataFrame
    """

    # --------------------------------------------------------
    # 분석용 복사본 생성
    #
    # 원본 geometry는 그대로 두고,
    # 중복 분석할 때만 invalid geometry를 보정한다.
    # --------------------------------------------------------

    analysis_polygons = polygons.copy()

    invalid_mask = ~analysis_polygons.geometry.is_valid

    invalid_count = invalid_mask.sum()

    print(
        "유효하지 않은 Geometry:",
        invalid_count,
    )

    if invalid_count > 0:

        print("중복 분석용 Geometry를 " "buffer(0)으로 보정합니다.")

        analysis_polygons.loc[
            invalid_mask,
            "geometry",
        ] = analysis_polygons.loc[
            invalid_mask
        ].geometry.buffer(0)

    # --------------------------------------------------------
    # Spatial Index
    # --------------------------------------------------------

    spatial_index = analysis_polygons.sindex

    duplicate_rows = []

    checked_pairs = set()

    # --------------------------------------------------------
    # Polygon별 후보 탐색
    # --------------------------------------------------------

    for index_a, polygon_a in analysis_polygons.iterrows():

        geom_a = polygon_a.geometry

        if geom_a is None or geom_a.is_empty:
            continue

        # ----------------------------------------------------
        # Bounding box가 겹치는 Polygon만 후보로 가져옴
        # ----------------------------------------------------

        candidate_indices = spatial_index.query(
            geom_a,
            predicate="intersects",
        )

        for index_b in candidate_indices:

            index_b = int(index_b)

            # 자기 자신 제외
            if index_a == index_b:
                continue

            # ------------------------------------------------
            # A-B를 검사했다면 B-A는 다시 검사하지 않음
            # ------------------------------------------------

            pair = tuple(
                sorted(
                    (
                        int(index_a),
                        index_b,
                    )
                )
            )

            if pair in checked_pairs:
                continue

            checked_pairs.add(pair)

            polygon_b = analysis_polygons.iloc[index_b]

            geom_b = polygon_b.geometry

            if geom_b is None or geom_b.is_empty:
                continue

            # =================================================
            # LABEL 비교
            # =================================================

            label_a = polygon_a.get("LABEL")

            label_b = polygon_b.get("LABEL")

            same_label = label_a == label_b

            if REQUIRE_SAME_LABEL and not same_label:
                continue

            # =================================================
            # 면적
            # =================================================

            area_a = geom_a.area
            area_b = geom_b.area

            smaller_area = min(
                area_a,
                area_b,
            )

            if smaller_area <= 0:
                continue

            # =================================================
            # 교집합 면적
            # =================================================

            intersection = geom_a.intersection(geom_b)

            if intersection.is_empty:
                continue

            intersection_area = intersection.area

            # =================================================
            # 작은 Polygon 기준 겹침 비율
            # =================================================

            overlap_ratio = intersection_area / smaller_area

            # 기준 미달이면 중복 아님
            if overlap_ratio < OVERLAP_THRESHOLD:
                continue

            # =================================================
            # 중복 후보 저장
            # =================================================

            duplicate_rows.append(
                {
                    "index_a": int(index_a),
                    "index_b": index_b,
                    "id_a": polygon_a.get("ID"),
                    "id_b": polygon_b.get("ID"),
                    "label_a": label_a,
                    "label_b": label_b,
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
                    "overlap_ratio": round(
                        overlap_ratio,
                        6,
                    ),
                    "same_label": same_label,
                }
            )

    return pd.DataFrame(duplicate_rows)


# ============================================================
# Shapefile 읽기
# ============================================================

polygons = gpd.read_file(SHP_PATH)

# iloc 위치와 index를 동일하게 만들기 위해
# 처음부터 RangeIndex로 정리한다.
polygons = polygons.reset_index(drop=True)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "원본 Polygon 개수:",
    len(polygons),
)

print(
    "CRS:",
    polygons.crs,
)

print(
    "Geometry 타입:",
    polygons.geometry.geom_type.value_counts().to_dict(),
)


# ============================================================
# 중복 Polygon 직접 탐색
# ============================================================

print()
print("=" * 70)
print("중복 Polygon 탐색")
print("=" * 70)


duplicates = find_duplicate_polygons(polygons)


print()
print(
    "조건을 만족하는 중복 쌍:",
    len(duplicates),
)


# ============================================================
# 중복 후보가 없는 경우
# ============================================================

if duplicates.empty:

    print("중복 Polygon이 없습니다.")

    duplicate_targets = duplicates.copy()

else:

    # --------------------------------------------------------
    # 이미 find_duplicate_polygons에서 조건을 적용했지만,
    # 최종 안전 검증 차원에서 한 번 더 필터링한다.
    # --------------------------------------------------------

    duplicate_targets = duplicates[
        duplicates["overlap_ratio"] >= OVERLAP_THRESHOLD
    ].copy()

    if REQUIRE_SAME_LABEL:

        duplicate_targets = duplicate_targets[
            duplicate_targets["same_label"] == True
        ].copy()


print(
    "자동 제거 대상 중복 쌍:",
    len(duplicate_targets),
)


# ============================================================
# 중복 관계 그룹화
# ============================================================

union_find = UnionFind()


for _, row in duplicate_targets.iterrows():

    index_a = int(row["index_a"])

    index_b = int(row["index_b"])

    union_find.union(
        index_a,
        index_b,
    )


# ============================================================
# 중복 그룹 생성
# ============================================================

groups = {}


for index in union_find.parent:

    root = union_find.find(index)

    groups.setdefault(root, []).append(index)


# 실제 중복 그룹만 유지
groups = {root: sorted(indices) for root, indices in groups.items() if len(indices) > 1}


print(
    "중복 그룹 개수:",
    len(groups),
)


# ============================================================
# 대표 Polygon 결정
# ============================================================
#
# 같은 그룹에서는 원본 Shapefile에서
# 먼저 등장한 Polygon을 대표로 남긴다.
#
# 예:
#
# 35
# 1875
#
# → 35 유지
# → 1875 제거
# ============================================================

remove_indices = set()

removed_rows = []


for group_number, indices in enumerate(
    groups.values(),
    start=1,
):

    representative_index = min(indices)

    representative = polygons.iloc[representative_index]

    for index in indices:

        if index == representative_index:
            continue

        remove_indices.add(index)

        removed = polygons.iloc[index]

        removed_rows.append(
            {
                "duplicate_group": (group_number),
                "kept_index": (representative_index),
                "kept_id": (representative.get("ID")),
                "kept_label": (representative.get("LABEL")),
                "removed_index": (index),
                "removed_id": (removed.get("ID")),
                "removed_label": (removed.get("LABEL")),
            }
        )


# ============================================================
# 제거 예정 목록
# ============================================================

print()
print("=" * 70)
print("제거 예정 Polygon")
print("=" * 70)


if not removed_rows:

    print("제거 대상이 없습니다.")

else:

    removed_df = pd.DataFrame(removed_rows)

    print(
        removed_df[
            [
                "kept_id",
                "kept_label",
                "removed_id",
                "removed_label",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 중복 제거
# ============================================================

deduplicated = polygons.drop(index=list(remove_indices)).copy()


deduplicated = deduplicated.reset_index(drop=True)


# ============================================================
# 결과 검증
# ============================================================

original_count = len(polygons)

removed_count = len(remove_indices)

final_count = len(deduplicated)


print()
print("=" * 70)
print("중복 제거 결과")
print("=" * 70)

print(
    "원본 Polygon:",
    original_count,
)

print(
    "제거 Polygon:",
    removed_count,
)

print(
    "최종 Polygon:",
    final_count,
)

print(
    "계산 확인:",
    original_count - removed_count,
)


if original_count - removed_count != final_count:

    raise ValueError("Polygon 개수 계산이 " "맞지 않습니다.")


# ============================================================
# 현재 데이터셋 재현성 검증
# ============================================================
#
# 서울 공원 Shapefile 기준으로 기존 분석 결과는:
#
# 1888 → 36개 제거 → 1852
#
# 데이터 원본이 변경됐을 경우를 고려하여
# 강제로 에러를 발생시키지는 않고 경고만 출력한다.
# ============================================================

EXPECTED_ORIGINAL_COUNT = 1888
EXPECTED_REMOVED_COUNT = 36
EXPECTED_FINAL_COUNT = 1852


if original_count == EXPECTED_ORIGINAL_COUNT:

    if removed_count != EXPECTED_REMOVED_COUNT or final_count != EXPECTED_FINAL_COUNT:

        print()
        print("[WARNING] 기존 분석 결과와 " "Polygon 개수가 다릅니다.")

        print(
            "기대:",
            f"{EXPECTED_ORIGINAL_COUNT}"
            f" → -{EXPECTED_REMOVED_COUNT}"
            f" → {EXPECTED_FINAL_COUNT}",
        )


# ============================================================
# 출력 폴더 생성
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REMOVED_CSV.parent.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Shapefile 저장
# ============================================================

deduplicated.to_file(
    OUTPUT_SHP,
    driver="ESRI Shapefile",
    encoding="cp949",
)


# ============================================================
# 제거 내역 CSV 저장
# ============================================================

if removed_rows:

    removed_df = pd.DataFrame(removed_rows)

else:

    removed_df = pd.DataFrame(
        columns=[
            "duplicate_group",
            "kept_index",
            "kept_id",
            "kept_label",
            "removed_index",
            "removed_id",
            "removed_label",
        ]
    )


removed_df.to_csv(
    REMOVED_CSV,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 저장 결과
# ============================================================

print()
print("=" * 70)
print("저장 완료")
print("=" * 70)

print(
    "정제 Shapefile:",
    OUTPUT_SHP,
)

print(
    "제거 내역:",
    REMOVED_CSV,
)
