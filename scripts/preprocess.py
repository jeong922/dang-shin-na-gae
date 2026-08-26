from pathlib import Path
import re

import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw" / "서울시 주요 공원현황.csv"

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "parks.csv"


# ============================================================
# 면적 수동 보정
# ============================================================
#
# 원본의 '면적' 컬럼이 비정형이거나
# 자동 파싱 결과를 신뢰할 수 없는 경우에만 사용한다.
#
# 반드시 공식 자료 등으로 실제 면적을 확인한 뒤 추가한다.
#
# 예:
#
# AREA_OVERRIDES = {
#     "진관근린공원(구파발폭포)": 983791.0,
# }
#
# ============================================================

AREA_OVERRIDES = {
    "진관근린공원(구파발폭포)": 983791.0,
}


# ============================================================
# 데이터 불러오기
# ============================================================

parks = pd.read_csv(
    RAW_PATH,
    encoding="cp949",
)


# ============================================================
# 사용할 컬럼 선택
# ============================================================

target_columns = [
    "연번",
    "공원명",
    "공원개요",
    "면적",
    "개원일",
    "주요시설",
    "주요식물",
    "안내도",
    "오시는길",
    "이용시참고사항",
    "이미지",
    "지역",
    "공원주소",
    "관리부서",
    "전화번호",
    "X좌표(WGS84)",
    "Y좌표(WGS84)",
    "바로가기",
]

parks = parks[target_columns].copy()


# ============================================================
# 컬럼명 변경
# ============================================================

parks = parks.rename(
    columns={
        "연번": "id",
        "공원명": "name",
        "공원개요": "description",
        "면적": "area",
        "개원일": "opened_at",
        "주요시설": "facilities",
        "주요식물": "plants",
        "안내도": "map_image",
        "오시는길": "directions",
        "이용시참고사항": "notes",
        "이미지": "image",
        "지역": "district",
        "공원주소": "address",
        "관리부서": "department",
        "전화번호": "phone",
        "X좌표(WGS84)": "lon",
        "Y좌표(WGS84)": "lat",
        "바로가기": "url",
    }
)


# ============================================================
# 면적 파싱
# ============================================================


def parse_area(value):
    """
    면적 문자열에서 첫 번째 숫자를 추출한다.

    예:
        "480,994㎡"
            -> 480994.0

        "2896887㎡"
            -> 2896887.0

    주의:
        원본 면적 컬럼이 비정형 텍스트인 경우
        첫 번째 숫자가 실제 공원 면적이 아닐 수 있다.

        이런 경우 AREA_OVERRIDES를 통해 별도로 보정한다.
    """

    if pd.isna(value):
        return None

    value = str(value)

    match = re.search(
        r"[\d,]+(?:\.\d+)?",
        value,
    )

    if match is None:
        return None

    return float(
        match.group().replace(
            ",",
            "",
        )
    )


# ============================================================
# 면적 문자열에 포함된 숫자 개수 계산
# ============================================================


def count_numbers(value):
    """
    원본 면적 문자열에 숫자가 몇 개 포함되어 있는지 계산한다.

    숫자가 여러 개 존재한다면 단순 parse_area()로
    처리하기 어려운 비정형 데이터일 가능성이 있다.
    """

    if pd.isna(value):
        return 0

    numbers = re.findall(
        r"[\d,]+(?:\.\d+)?",
        str(value),
    )

    return len(numbers)


# ============================================================
# 주소에서 자치구 추출
# ============================================================


def extract_district(address):
    """
    주소 문자열에서 '구'로 끝나는 값을 찾아
    자치구 이름으로 사용한다.
    """

    if not address:
        return ""

    for part in str(address).split():

        if part.endswith("구"):
            return part

    return ""


# ============================================================
# 결측치 처리
# ============================================================

text_columns = [
    "description",
    "facilities",
    "plants",
    "map_image",
    "directions",
    "notes",
    "district",
    "image",
    "url",
]


parks[text_columns] = parks[text_columns].fillna("")


# ============================================================
# 지역 정보 보정
# ============================================================

parks["district"] = parks.apply(
    lambda row: (
        row["district"] if row["district"] else extract_district(row["address"])
    ),
    axis=1,
)


# ============================================================
# 원본 면적 데이터 검사
# ============================================================
#
# parse_area()를 실행하기 전에 검사해야 한다.
#
# 숫자가 여러 개 들어 있는 경우
# 첫 번째 숫자를 공원 면적으로 사용하는 것이
# 잘못될 가능성이 있기 때문이다.
# ============================================================

parks["_area_number_count"] = parks["area"].apply(count_numbers)


suspicious_area = parks[parks["_area_number_count"] > 1].copy()


print()
print("=" * 70)
print("면적 확인 필요")
print("=" * 70)


if suspicious_area.empty:

    print("숫자가 여러 개 포함된 면적 데이터가 없습니다.")

else:

    print(
        "확인 대상:",
        len(suspicious_area),
    )

    print()

    print(
        suspicious_area[
            [
                "id",
                "name",
                "area",
                "_area_number_count",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 면적 숫자 변환
# ============================================================

parks["area"] = parks["area"].apply(parse_area)


# ============================================================
# 면적 수동 보정
# ============================================================

print()
print("=" * 70)
print("면적 수동 보정")
print("=" * 70)


if not AREA_OVERRIDES:

    print("적용할 수동 보정이 없습니다.")

else:

    for (
        park_name,
        override_area,
    ) in AREA_OVERRIDES.items():

        mask = parks["name"] == park_name

        # ----------------------------------------------------
        # 대상 존재 여부 확인
        # ----------------------------------------------------

        if not mask.any():

            raise ValueError("면적 보정 대상 공원을 " f"찾을 수 없습니다: {park_name}")

        # ----------------------------------------------------
        # 동일 이름 중복 검사
        # ----------------------------------------------------

        if mask.sum() > 1:

            raise ValueError(
                f"동일한 이름의 공원이 여러 개 존재합니다: " f"{park_name}"
            )

        old_area = parks.loc[
            mask,
            "area",
        ].iloc[0]

        # ----------------------------------------------------
        # 면적 교체
        # ----------------------------------------------------

        parks.loc[
            mask,
            "area",
        ] = override_area

        print(
            f"[면적 보정] "
            f"{park_name}: "
            f"{old_area:,.2f}㎡ "
            f"-> "
            f"{override_area:,.2f}㎡"
        )


# ============================================================
# 좌표 숫자 변환
# ============================================================

parks["lat"] = pd.to_numeric(
    parks["lat"],
    errors="coerce",
)


parks["lon"] = pd.to_numeric(
    parks["lon"],
    errors="coerce",
)


# ============================================================
# 사용할 수 없는 데이터 확인
# ============================================================

missing_area = parks[parks["area"].isna()]


print()
print("=" * 70)
print("면적 정보 없음")
print("=" * 70)


if missing_area.empty:

    print("없음")

else:

    print(
        missing_area[
            [
                "id",
                "name",
            ]
        ].to_string(index=False)
    )


# ------------------------------------------------------------
# 좌표 정보 없음
# ------------------------------------------------------------

missing_coordinates = parks[
    parks[
        [
            "lat",
            "lon",
        ]
    ]
    .isna()
    .any(axis=1)
]


print()
print("=" * 70)
print("좌표 정보 없음")
print("=" * 70)


if missing_coordinates.empty:

    print("없음")

else:

    print(
        missing_coordinates[
            [
                "id",
                "name",
                "lat",
                "lon",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 사용할 수 없는 데이터 제거
# ============================================================

before_count = len(parks)


parks = parks.dropna(
    subset=[
        "lat",
        "lon",
    ]
).copy()


parks = parks.reset_index(drop=True)


removed_count = before_count - len(parks)


# ============================================================
# 분석용 임시 컬럼 제거
# ============================================================

parks = parks.drop(columns=["_area_number_count"])


# ============================================================
# 저장
# ============================================================

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True,
)


parks.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 최종 결과
# ============================================================

print()
print("=" * 70)
print("전처리 완료")
print("=" * 70)

print(
    "원본 공원:",
    before_count,
)

print(
    "제거 공원:",
    removed_count,
)

print(
    "최종 공원:",
    len(parks),
)

print(
    "저장 위치:",
    OUTPUT_PATH,
)

print("=" * 70)
