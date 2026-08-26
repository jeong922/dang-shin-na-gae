from pathlib import Path
import re
from difflib import SequenceMatcher

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

VALIDATION_CSV = BASE_DIR / "data" / "analysis" / "park_polygon_area_validation.csv"

SEOUL_SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"

OUTPUT_CSV = BASE_DIR / "data" / "analysis" / "polygon_area_mismatch_candidates.csv"


# ============================================================
# 설정
# ============================================================

# parks.csv의 대표 좌표를 기준으로
# 주변 몇 m까지 Polygon 후보를 찾을지
SEARCH_DISTANCE_M = 1500

# 각 데이터 소스에서 출력할 최대 후보 개수
TOP_N = 10


# ============================================================
# 분석 대상
# ============================================================
#
# 현재 면적 검증 결과에서 실제 Polygon을
# 다시 찾아볼 가치가 있는 공원들.
#
# 이미 OSM replacement로 수정한
# 9, 108, 119는 제외했다.
#
# manual_parent_polygon은 별도로 관리하므로 제외.
# 북한산국립공원은 원본 면적 자체가 특이하므로 제외.
#
# 서울숲은 strong_mismatch는 아니지만
# 현재 Polygon이 공식 면적의 약 절반이므로 함께 확인한다.
# ============================================================

TARGET_PARK_IDS = [
    4,  # 서울숲
    26,  # 감로천생태공원(관악산)
    64,  # 봉은공원
    79,  # 삼청근린공원
    91,  # 북서울꿈의숲
    95,  # 금천체육공원(관악산)
    97,  # 만수천공원(관악산)
    98,  # 발바닥공원
    109,  # 초안산생태공원
    126,  # 용마도시자연공원(사가정공원)
]


# ============================================================
# 이름 정규화
# ============================================================


def normalize_name(value):
    """
    공원 이름 비교를 위한 단순 정규화.

    예:
        근린공원(서울숲)
        서울숲

    괄호 문자와 공백 등을 제거하여 이름 비교에 사용한다.
    """

    if pd.isna(value):
        return ""

    value = str(value).lower()

    # 괄호 안의 내용은 유지하고 괄호 문자만 제거한다.
    #
    # 예:
    # 근린공원(서울숲)
    # -> 근린공원서울숲
    value = re.sub(
        r"[()<>[\]{}]",
        "",
        value,
    )

    # 공백 제거
    value = re.sub(
        r"\s+",
        "",
        value,
    )

    return value


# ============================================================
# 공원 유형 관련 단어 제거
# ============================================================


def simplify_park_name(value):
    """
    공원 종류를 나타내는 일반적인 단어를 제거하여
    핵심 이름 비교에 사용한다.

    예:
        감로천생태공원(관악산)
        -> 감로천관악산

        근린공원(서울숲)
        -> 서울숲
    """

    value = normalize_name(value)

    removable_words = [
        "도시자연공원",
        "근린공원",
        "생태공원",
        "어린이공원",
        "문화공원",
        "체육공원",
        "강변공원",
        "역사공원",
        "수변공원",
        "기타공원",
        "공원",
    ]

    for word in removable_words:
        value = value.replace(
            word,
            "",
        )

    return value


# ============================================================
# 이름 유사도
# ============================================================


def calculate_name_score(
    park_name,
    candidate_name,
):
    """
    0 ~ 100 범위의 이름 유사도 계산.

    정확한 자동 매칭 판정용이 아니라
    후보 정렬을 돕기 위한 참고 점수다.
    """

    park = simplify_park_name(park_name)

    candidate = simplify_park_name(candidate_name)

    if not park or not candidate:
        return 0.0

    # 완전히 동일
    if park == candidate:
        return 100.0

    # 한쪽 이름이 다른 쪽에 포함
    if park in candidate or candidate in park:
        return 90.0

    return round(
        SequenceMatcher(
            None,
            park,
            candidate,
        ).ratio()
        * 100,
        2,
    )


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

validation = pd.read_csv(VALIDATION_CSV)

seoul_polygons = gpd.read_file(SEOUL_SHP_PATH)

osm_polygons = gpd.read_file(OSM_GEOJSON_PATH)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "공원 데이터:",
    len(parks),
)

print(
    "면적 검증 데이터:",
    len(validation),
)

print(
    "서울시 Polygon:",
    len(seoul_polygons),
)

print(
    "OSM Polygon:",
    len(osm_polygons),
)


# ============================================================
# 필수 컬럼 확인
# ============================================================

required_park_columns = {
    "id",
    "name",
    "lat",
    "lon",
    "area",
}

missing_park_columns = required_park_columns - set(parks.columns)

if missing_park_columns:
    raise ValueError(
        "parks.csv에 필요한 컬럼이 없습니다: " f"{sorted(missing_park_columns)}"
    )


required_validation_columns = {
    "park_id",
    "park_name",
    "official_area_m2",
    "polygon_area_m2",
    "area_ratio",
    "area_status",
}

missing_validation_columns = required_validation_columns - set(validation.columns)

if missing_validation_columns:
    raise ValueError(
        "park_polygon_area_validation.csv에 "
        "필요한 컬럼이 없습니다: "
        f"{sorted(missing_validation_columns)}"
    )


# ============================================================
# 분석 대상 추출
# ============================================================

targets = validation[validation["park_id"].isin(TARGET_PARK_IDS)].copy()


print()
print("=" * 70)
print("분석 대상")
print("=" * 70)

print(
    "공원 개수:",
    len(targets),
)

print()

print(
    targets[
        [
            "park_id",
            "park_name",
            "official_area_m2",
            "polygon_area_m2",
            "area_ratio",
            "area_status",
        ]
    ].to_string(index=False)
)


# ============================================================
# 분석 대상 누락 검사
# ============================================================

found_target_ids = set(targets["park_id"].astype(int))

missing_target_ids = set(TARGET_PARK_IDS) - found_target_ids

if missing_target_ids:

    print()
    print(
        "[주의] validation 데이터에서 " "찾지 못한 park_id:",
        sorted(missing_target_ids),
    )


# ============================================================
# CRS 통일
# ============================================================
#
# 거리와 면적을 meter 단위로 계산하기 위해
# EPSG:5186 사용.
# ============================================================

seoul_m = seoul_polygons.to_crs("EPSG:5186")

osm_m = osm_polygons.to_crs("EPSG:5186")


# ============================================================
# 공원 좌표 GeoDataFrame 생성
# ============================================================
#
# 기존 코드에서는 현재 최종 Polygon의
# representative_point()를 사용했다.
#
# 그러나 현재 Polygon 자체가 잘못 매칭된 경우
# 그 위치를 기준으로 후보를 찾는 것도 영향을 받을 수 있다.
#
# 따라서 이번 분석에서는 parks.csv의
# 원본 lat / lon을 검색 기준으로 사용한다.
# ============================================================

park_points = gpd.GeoDataFrame(
    parks.copy(),
    geometry=gpd.points_from_xy(
        parks["lon"],
        parks["lat"],
    ),
    crs="EPSG:4326",
)

park_points_m = park_points.to_crs("EPSG:5186")


# ============================================================
# 후보 이름 컬럼
# ============================================================


def get_candidate_name_column(
    polygons,
    source,
):
    """
    데이터 소스별 후보 이름 컬럼을 반환한다.
    """

    if source == "seoul":

        if "LABEL" not in polygons.columns:
            raise ValueError("서울시 Shapefile에 " "LABEL 컬럼이 없습니다.")

        return "LABEL"

    if source == "osm":

        if "name" not in polygons.columns:
            raise ValueError("OSM 데이터에 " "name 컬럼이 없습니다.")

        return "name"

    raise ValueError(f"알 수 없는 source: {source}")


# ============================================================
# 후보 생성
# ============================================================


def find_candidates(
    park_id,
    park_name,
    official_area,
    park_point,
    polygons,
    source,
):
    """
    parks.csv의 대표 좌표를 기준으로
    주변 Polygon 후보를 찾는다.

    후보마다 다음 값을 계산한다.

    - 이름
    - 대표 좌표와 Polygon 사이 거리
    - Polygon 면적
    - 공식 면적 대비 비율
    - 공식 면적과의 차이
    - 이름 유사도

    이 함수는 후보를 자동 확정하지 않는다.
    사람이 검토하기 위한 후보 생성 용도다.
    """

    candidates = polygons.copy()

    # --------------------------------------------------------
    # 대표 좌표와 Polygon 사이 거리
    # --------------------------------------------------------
    #
    # Point가 Polygon 내부에 있으면 distance = 0
    #
    # Polygon 밖에 있으면 가장 가까운 경계까지의
    # 거리가 계산된다.
    # --------------------------------------------------------

    candidates["distance_m"] = candidates.geometry.distance(park_point)

    candidates = candidates[candidates["distance_m"] <= SEARCH_DISTANCE_M].copy()

    if candidates.empty:
        return candidates

    # --------------------------------------------------------
    # Polygon 면적
    # --------------------------------------------------------

    candidates["candidate_area_m2"] = candidates.geometry.area

    # --------------------------------------------------------
    # 공식 면적 대비 비율
    # --------------------------------------------------------

    if pd.notna(official_area) and official_area > 0:

        candidates["area_ratio"] = candidates["candidate_area_m2"] / official_area

        candidates["area_difference"] = (candidates["area_ratio"] - 1).abs()

    else:

        candidates["area_ratio"] = float("nan")

        candidates["area_difference"] = float("inf")

    # --------------------------------------------------------
    # 후보 이름
    # --------------------------------------------------------

    name_column = get_candidate_name_column(
        polygons=candidates,
        source=source,
    )

    # --------------------------------------------------------
    # 이름 유사도
    # --------------------------------------------------------

    candidates["name_score"] = candidates[name_column].apply(
        lambda candidate_name: calculate_name_score(
            park_name,
            candidate_name,
        )
    )

    # --------------------------------------------------------
    # 출처
    # --------------------------------------------------------

    candidates["candidate_source"] = source

    # --------------------------------------------------------
    # 공원 정보
    # --------------------------------------------------------

    candidates["park_id"] = park_id

    candidates["park_name"] = park_name

    candidates["official_area_m2"] = official_area

    # --------------------------------------------------------
    # 정렬
    # --------------------------------------------------------
    #
    # 이름 유사도
    #     ↓
    # 면적 차이
    #     ↓
    # 거리
    #
    # 순서로 후보를 정렬한다.
    #
    # 자동 선택이 아니라 사람이 검토하기 위한
    # 우선순위일 뿐이다.
    # --------------------------------------------------------

    candidates = candidates.sort_values(
        by=[
            "name_score",
            "area_difference",
            "distance_m",
        ],
        ascending=[
            False,
            True,
            True,
        ],
    )

    return candidates.head(TOP_N).copy()


# ============================================================
# 후보 출력
# ============================================================


def print_candidates(
    candidates,
    source,
):

    if candidates.empty:

        print("후보 없음")

        return

    if source == "seoul":

        columns = [
            "ID",
            "LABEL",
            "name_score",
            "distance_m",
            "candidate_area_m2",
            "area_ratio",
        ]

    else:

        columns = [
            "osm_id",
            "name",
            "fclass",
            "name_score",
            "distance_m",
            "candidate_area_m2",
            "area_ratio",
        ]

    # 실제 데이터에 존재하는 컬럼만 출력
    columns = [column for column in columns if column in candidates.columns]

    output = candidates[columns].copy()

    # --------------------------------------------------------
    # 출력용 반올림
    # --------------------------------------------------------

    for column in [
        "distance_m",
        "candidate_area_m2",
    ]:

        if column in output.columns:

            output[column] = output[column].round(2)

    if "area_ratio" in output.columns:

        output["area_ratio"] = output["area_ratio"].round(4)

    if "name_score" in output.columns:

        output["name_score"] = output["name_score"].round(2)

    print(output.to_string(index=False))


# ============================================================
# CSV 저장용 후보 정리
# ============================================================


def prepare_candidates_for_output(
    candidates,
    source,
):

    if candidates.empty:
        return pd.DataFrame()

    if source == "seoul":

        candidate_id_column = "ID" if "ID" in candidates.columns else None

        candidate_name_column = "LABEL"

    else:

        candidate_id_column = "osm_id" if "osm_id" in candidates.columns else None

        candidate_name_column = "name"

    output = pd.DataFrame()

    output["park_id"] = candidates["park_id"]

    output["park_name"] = candidates["park_name"]

    output["official_area_m2"] = candidates["official_area_m2"]

    output["candidate_source"] = source

    if candidate_id_column:

        output["candidate_id"] = candidates[candidate_id_column].astype(str)

    else:

        output["candidate_id"] = ""

    output["candidate_name"] = candidates[candidate_name_column]

    output["name_score"] = candidates["name_score"]

    output["distance_m"] = candidates["distance_m"]

    output["candidate_area_m2"] = candidates["candidate_area_m2"]

    output["area_ratio"] = candidates["area_ratio"]

    output["area_difference"] = candidates["area_difference"]

    # OSM 유형 정보
    if source == "osm" and "fclass" in candidates.columns:

        output["fclass"] = candidates["fclass"].values

    else:

        output["fclass"] = ""

    return output


# ============================================================
# 공원별 분석
# ============================================================

all_candidate_results = []


for _, target in targets.iterrows():

    park_id = int(target["park_id"])

    park_name = target["park_name"]

    official_area = target["official_area_m2"]

    # --------------------------------------------------------
    # parks.csv의 대표 좌표 찾기
    # --------------------------------------------------------

    park_point_row = park_points_m[park_points_m["id"] == park_id]

    print()
    print()
    print("=" * 70)
    print(f"[{park_id}] {park_name}")
    print("=" * 70)

    if park_point_row.empty:

        print("parks.csv에서 해당 공원을 " "찾을 수 없습니다.")

        continue

    if len(park_point_row) > 1:

        raise ValueError(f"parks.csv에 park_id={park_id}가 " "여러 개 존재합니다.")

    park_point_row = park_point_row.iloc[0]

    park_point = park_point_row.geometry

    # --------------------------------------------------------
    # 기본 정보 출력
    # --------------------------------------------------------

    print(
        "대표 좌표:",
        f"{park_point_row['lat']}, " f"{park_point_row['lon']}",
    )

    print(
        "공식 면적:",
        f"{official_area:,.2f}㎡",
    )

    print(
        "현재 Polygon 면적:",
        f"{target['polygon_area_m2']:,.2f}㎡",
    )

    print(
        "현재 면적 비율:",
        f"{target['area_ratio']:.4f}",
    )

    # ========================================================
    # 서울시 후보
    # ========================================================

    print()
    print("-" * 70)
    print("서울시 Shapefile 후보")
    print("-" * 70)

    seoul_candidates = find_candidates(
        park_id=park_id,
        park_name=park_name,
        official_area=official_area,
        park_point=park_point,
        polygons=seoul_m,
        source="seoul",
    )

    print_candidates(
        seoul_candidates,
        source="seoul",
    )

    seoul_output = prepare_candidates_for_output(
        seoul_candidates,
        source="seoul",
    )

    if not seoul_output.empty:

        all_candidate_results.append(seoul_output)

    # ========================================================
    # OSM 후보
    # ========================================================

    print()
    print("-" * 70)
    print("OSM 후보")
    print("-" * 70)

    osm_candidates = find_candidates(
        park_id=park_id,
        park_name=park_name,
        official_area=official_area,
        park_point=park_point,
        polygons=osm_m,
        source="osm",
    )

    print_candidates(
        osm_candidates,
        source="osm",
    )

    osm_output = prepare_candidates_for_output(
        osm_candidates,
        source="osm",
    )

    if not osm_output.empty:

        all_candidate_results.append(osm_output)


# ============================================================
# 전체 후보 CSV 저장
# ============================================================

print()
print()
print("=" * 70)
print("후보 CSV 저장")
print("=" * 70)


if all_candidate_results:

    result = pd.concat(
        all_candidate_results,
        ignore_index=True,
    )

    # --------------------------------------------------------
    # 출력용 반올림
    # --------------------------------------------------------

    result["name_score"] = result["name_score"].round(2)

    result["distance_m"] = result["distance_m"].round(2)

    result["candidate_area_m2"] = result["candidate_area_m2"].round(2)

    result["area_ratio"] = result["area_ratio"].round(4)

    result["area_difference"] = result["area_difference"].round(4)

    # --------------------------------------------------------
    # 저장
    # --------------------------------------------------------

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_CSV,
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "후보 행:",
        len(result),
    )

    print(
        "저장 위치:",
        OUTPUT_CSV,
    )

else:

    print("저장할 후보가 없습니다.")


# ============================================================
# 완료
# ============================================================

print()
print("=" * 70)
print("분석 완료")
print("=" * 70)
