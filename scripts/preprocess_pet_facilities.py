import numpy as np
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = BASE_DIR / "data" / "raw" / "한국문화정보원_전국 반려동물 동반 가능 문화시설 위치 데이터.csv"

OUTPUT_PATH = BASE_DIR / "data" / "processed" / "seoul_pet_facilities.csv"


# 파일 읽기
df = pd.read_csv(
    RAW_PATH,
    encoding="utf-8-sig",
    dtype={
        "운영시간": "string",
        "입장(이용료)가격 정보": "string",
        "애견 동반 추가 요금": "string",
    },
)


# 서울시이면서 반려동물 동반이 가능한 시설만 추출
seoul_df = df[
    (df["시도 명칭"] == "서울특별시")
    & (df["반려동물 동반 가능정보"] == "Y")
].copy()

filtered_count = len(seoul_df)

# 위도·경도가 유한한 숫자이고 정상 범위인지 검증
seoul_df["위도"] = pd.to_numeric(seoul_df["위도"], errors="coerce")
seoul_df["경도"] = pd.to_numeric(seoul_df["경도"], errors="coerce")

valid_coordinates = (
    np.isfinite(seoul_df["위도"])
    & np.isfinite(seoul_df["경도"])
    & seoul_df["위도"].between(-90, 90)
    & seoul_df["경도"].between(-180, 180)
)
invalid_coordinate_count = int((~valid_coordinates).sum())
seoul_df = seoul_df.loc[valid_coordinates]

# 컬럼명 변경
column_mapping = {
    # 시설 기본 정보
    "시설명": "name",
    "카테고리1": "category1",
    "카테고리2": "category2",
    "카테고리3": "category3",

    # 지역 및 주소
    "시도 명칭": "city",
    "시군구 명칭": "district",
    "법정읍면동명칭": "neighborhood",
    "위도": "lat",
    "경도": "lon",
    "도로명주소": "road_address",
    "지번주소": "lot_address",

    # 연락처 및 운영 정보
    "전화번호": "phone",
    "홈페이지": "website",
    "휴무일": "closed_days",
    "운영시간": "opening_hours",
    "주차 가능여부": "parking_available",
    "입장(이용료)가격 정보": "admission_fee",

    # 반려동물 이용 조건
    "반려동물 전용 정보": "pet_exclusive",
    "입장 가능 동물 크기": "allowed_pet_size",
    "반려동물 제한사항": "pet_restrictions",
    "애견 동반 추가 요금": "pet_extra_fee",

    # 시설 환경 및 기타
    "장소(실내) 여부": "indoor",
    "장소(실외)여부": "outdoor",
    "기본 정보_장소설명": "description",
    "최종작성일": "record_updated_at",
}

seoul_df = seoul_df[list(column_mapping)].rename(columns=column_mapping)

# 최신 작성일 기준으로 중복 제거
missing_updated_at = seoul_df["record_updated_at"].isna()
seoul_df["record_updated_at"] = pd.to_datetime(
    seoul_df["record_updated_at"], format="%Y-%m-%d", errors="coerce"
)
date_parse_failure_count = int(
    (~missing_updated_at & seoul_df["record_updated_at"].isna()).sum()
)
before_dedup_count = len(seoul_df)

seoul_df = (
    seoul_df
    .sort_values("record_updated_at", ascending=False)
    .drop_duplicates(subset=["name", "road_address"], keep="first")
    .reset_index(drop=True)
)

# 문자열 데이터 정리
columns = [
    "website",
    "opening_hours",
    "closed_days",
]

seoul_df[columns] = seoul_df[columns].replace("정보없음", pd.NA)

print(f"서울시·반려동물 동반 가능 시설 수: {filtered_count:,}개")
print(f"잘못된 좌표 제거 수: {invalid_coordinate_count:,}개")
print(f"작성일 원본 결측 수 (좌표 검증 후): {missing_updated_at.sum():,}개")
print(f"작성일 파싱 실패 수 (원본 결측 제외): {date_parse_failure_count:,}개")
print(f"중복 제거 수: {before_dedup_count - len(seoul_df):,}개")
print(f"최종 시설 수: {len(seoul_df):,}개")
print(f"최종 컬럼 수: {len(seoul_df.columns)}개")

print("\n[컬럼별 결측값]")
print(seoul_df.isna().sum().sort_values(ascending=False))

print("\n[시설 카테고리]")
print(seoul_df["category3"].value_counts())

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

seoul_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

print(f"전처리 완료: {len(seoul_df):,}개 시설")
print(f"저장 경로: {OUTPUT_PATH}")