from pathlib import Path
import json
import re

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent


INPUT_PATH = BASE_DIR / "data" / "features" / "parks_features.csv"


OUTPUT_PATH = BASE_DIR / "data" / "features" / "parks_pet_features.csv"


# 반려동물 관련 키워드
PET_KEYWORDS = [
    "애완동물",
    "반려동물",
    "애완견",
    "반려견",
    "강아지",
]


# 특정 장소 제한 키워드
LOCATION_KEYWORDS = [
    "온실",
    "주제정원",
    "실내",
    "전시관",
    "박물관",
    "생태학습장",
    "놀이터",
    "잔디광장",
]


# 명확한 금지 표현
PROHIBITED_KEYWORDS = [
    "출입금지",
    "출입 불가",
    "출입불가",
    "동행 금지",
    "동행금지",
    "동반 불가",
    "동반불가",
    "들어갈 수 없습니다",
    "들어갈수없습니다",
    "입장 불가",
    "입장불가",
    "허용되지 않습니다",
    "허용되지않습니다",
]


# 자제 표현
RESTRICTED_KEYWORDS = [
    "출입 자제",
    "출입자제",
    "출입을 자제",
    "출입을자제",
    "이용 자제",
    "이용을 자제",
    "자제하여",
]


# 이용 가능 조건
ALLOWED_KEYWORDS = [
    "목줄",
    "배변",
    "배설물",
    "수거",
    "처리",
]


# 예외 동물
SERVICE_ANIMAL_KEYWORDS = [
    "안내견 제외",
    "안내견은 제외",
    "보조견 제외",
]


def normalize_text(text):
    """
    비교용 문자열 정리
    """

    return str(text).replace(" ", "").replace("\n", "").strip()


def split_sentences(text):
    """
    안내문 분리
    """

    sentences = re.split(r"[.\n;。]", str(text))

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def has_pet_keyword(sentence):
    """
    반려동물 관련 문장 여부
    """

    normalized = normalize_text(sentence)

    return any(keyword in normalized for keyword in PET_KEYWORDS)


def extract_pet_sentences(text):
    """
    반려동물 관련 문장 추출
    """

    sentences = split_sentences(text)

    return [sentence for sentence in sentences if has_pet_keyword(sentence)]


def extract_locations(sentence):
    """
    특정 제한 장소 추출
    """

    locations = []

    for location in LOCATION_KEYWORDS:

        if location in sentence:
            locations.append(location)

    return locations


def contains_service_animal_exception(sentence):
    """
    안내견 예외 여부
    """

    normalized = normalize_text(sentence)

    return any(
        normalize_text(keyword) in normalized for keyword in SERVICE_ANIMAL_KEYWORDS
    )


def contains_prohibited_context(sentence):
    """
    전체 금지 여부 판단
    """

    normalized = normalize_text(sentence)

    # 명확한 금지 표현
    if any(normalize_text(keyword) in normalized for keyword in PROHIBITED_KEYWORDS):
        return True

    has_pet = any(keyword in normalized for keyword in PET_KEYWORDS)

    has_action = (
        "출입" in normalized
        or "입장" in normalized
        or "동행" in normalized
        or "동반" in normalized
    )

    has_ban = "금지" in normalized

    # 애완동물 동행 금지 같은 패턴
    if has_pet and has_action and has_ban:
        return True

    return False


def contains_restricted_context(sentence):
    """
    출입 자제 여부
    """

    normalized = normalize_text(sentence)

    return any(normalize_text(keyword) in normalized for keyword in RESTRICTED_KEYWORDS)


def contains_allowed_context(sentence):
    """
    이용 조건 여부
    """

    normalized = normalize_text(sentence)

    return any(normalize_text(keyword) in normalized for keyword in ALLOWED_KEYWORDS)


def classify_pet_status(text):
    """
    반려동물 상태 분석

    반환:
    status
    notices
    restricted_locations
    service_animal_allowed
    """

    pet_sentences = extract_pet_sentences(text)

    if not pet_sentences:

        return ("unknown", [], [], False)

    has_allowed = False
    has_restricted = False
    has_prohibited = False

    restricted_locations = set()

    service_animal_allowed = False

    for sentence in pet_sentences:

        print("\n반려동물 문장:")
        print(sentence)

        locations = extract_locations(sentence)

        if locations:

            print("제한 장소:", locations)

        # 안내견 예외
        if contains_service_animal_exception(sentence):

            service_animal_allowed = True

            print("안내견 예외 발견")

        # 특정 장소 제한
        if locations and contains_prohibited_context(sentence):

            restricted_locations.update(locations)

            print("특정 장소 제한 처리")

            continue

        # 전체 금지
        if contains_prohibited_context(sentence):

            has_prohibited = True

            print("전체 금지 판단")

        elif contains_restricted_context(sentence):

            has_restricted = True

            print("출입 자제 판단")

        elif contains_allowed_context(sentence):

            has_allowed = True

            print("이용 가능 조건 판단")

    # 상태 결정

    if has_prohibited:

        status = "prohibited"

    elif has_restricted:

        status = "restricted"

    else:

        status = "allowed"

    # 특정 장소 제한이 있으면
    # 전체 금지가 아니라 허용으로 조정
    if restricted_locations:

        status = "allowed"

    return (
        status,
        pet_sentences,
        list(restricted_locations),
        service_animal_allowed,
    )


parks = pd.read_csv(INPUT_PATH, keep_default_na=False)


# 기존 컬럼 제거
remove_columns = [
    "pet_status",
    "pet_notice",
    "pet_restricted_locations",
    "service_animal_allowed",
]


parks = parks.drop(
    columns=[column for column in remove_columns if column in parks.columns]
)


statuses = []
notices = []
restricted_locations = []
service_animals = []


for index, row in parks.iterrows():

    print("\n==============================")
    print(f"[{index + 1}/{len(parks)}]", row["name"])

    status, sentences, locations, service_animal = classify_pet_status(
        row.get("notes", "")
    )

    statuses.append(status)

    notices.append(json.dumps(sentences, ensure_ascii=False))

    restricted_locations.append(json.dumps(locations, ensure_ascii=False))

    service_animals.append(service_animal)

    print("결과:", status)


parks["pet_status"] = statuses

parks["pet_notice"] = notices

parks["pet_restricted_locations"] = restricted_locations

parks["service_animal_allowed"] = service_animals


print("\n===== 결과 통계 =====")

print(parks["pet_status"].value_counts())


parks.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")


print("\n반려동물 상태 분석 완료")
