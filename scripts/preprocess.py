from pathlib import Path

import pandas as pd
import re

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw" / "서울시 주요 공원현황.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "parks.csv"

# 데이터 불러오기
parks = pd.read_csv(RAW_PATH, encoding="cp949")


# 사용할 컬럼 선택
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

parks = parks[target_columns]

# 컬럼명 변경
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


def parse_area(value):

    if pd.isna(value):
        return None

    value = str(value)

    match = re.search(r"[\d,]+(?:\.\d+)?", value)

    if match is None:
        return None

    return float(match.group().replace(",", ""))


def extract_district(address):
    if not address:
        return ""

    for part in str(address).split():
        if part.endswith("구"):
            return part

    return ""


# 결측치 처리
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

# 지역 정보 보정
parks["district"] = parks.apply(
    lambda row: (
        row["district"] if row["district"] else extract_district(row["address"])
    ),
    axis=1,
)


# 면적 숫자 변환

parks["area"] = parks["area"].apply(parse_area)


# 좌표 숫자 변환

parks["lat"] = pd.to_numeric(parks["lat"], errors="coerce")

parks["lon"] = pd.to_numeric(parks["lon"], errors="coerce")


# 사용할 수 없는 데이터 제거

missing_area = parks[parks["area"].isna()]

print("면적 정보 없음:")
print(missing_area["name"].tolist())

parks = parks.dropna(subset=["lat", "lon", "area"]).reset_index(drop=True)


# 저장
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

parks.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print("=" * 50)
print("전처리 완료")
print(f"공원 수 : {len(parks)}")
print(f"저장 위치 : {OUTPUT_PATH}")
print("=" * 50)
