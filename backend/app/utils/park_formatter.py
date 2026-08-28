import json
import math
import re
from numbers import Real

# ============================================================
# 공통
# ============================================================


def safe_value(value, default=None):
    """
    None / NaN 값을 안전하게 처리한다.
    """

    if value is None:
        return default

    if isinstance(value, Real):
        try:
            if math.isnan(value):
                return default
        except TypeError:
            pass

    return value


def normalize_text(value):
    """
    줄바꿈과 불필요한 연속 공백을 제거한다.
    """

    value = safe_value(value)

    if value is None:
        return ""

    value = str(value)

    value = value.replace("\r", " ")
    value = value.replace("\n", " ")

    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================================
# 공통 카테고리 파싱
# ============================================================


def make_flexible_pattern(text):
    """
    글자 사이에 공백이 있어도 인식할 수 있는 정규식 생성.

    예:
        조경시설
        조 경 시 설

    둘 다 같은 카테고리로 인식한다.
    """

    return r"\s*".join(re.escape(char) for char in text)


def build_category_pattern(categories):
    """
    카테고리 목록을 기준으로 섹션 구분 정규식을 만든다.

    긴 이름을 먼저 검사해서
    '문화예술시설'보다 '예술시설' 같은 짧은 문자열이
    먼저 매칭되는 문제를 방지한다.
    """

    sorted_categories = sorted(
        categories,
        key=len,
        reverse=True,
    )

    category_patterns = [
        make_flexible_pattern(category) for category in sorted_categories
    ]

    return re.compile(rf"({'|'.join(category_patterns)})\s*:")


def normalize_category(category):
    """
    '조 경 시 설' → '조경시설'
    """

    return re.sub(
        r"\s+",
        "",
        category,
    )


def parse_labeled_sections(
    value,
    categories,
    pattern,
):
    """
    '카테고리 : 내용 카테고리 : 내용 ...'
    형태의 비정형 문자열을 파싱한다.

    카테고리를 찾지 못하면 원문 전체를 보존한다.
    """

    value = normalize_text(value)

    if not value:
        return []

    matches = list(pattern.finditer(value))

    # 카테고리 구조 자체가 없는 데이터
    #
    # 예:
    # "폭포 야외무대"
    #
    # 원문을 버리지 않고 그대로 반환한다.
    if not matches:
        return [
            {
                "category": None,
                "content": value,
            }
        ]

    result = []

    # 첫 카테고리 앞에 텍스트가 존재하면 보존
    prefix = value[: matches[0].start()].strip(" -·")

    if prefix:
        result.append(
            {
                "category": None,
                "content": prefix,
            }
        )

    for i, match in enumerate(matches):
        category = normalize_category(match.group(1))

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(value)

        content = value[start:end].strip(" -·")

        if not content:
            continue

        result.append(
            {
                "category": category,
                "content": content,
            }
        )

    return result


# ============================================================
# 시설
# ============================================================


# parks_difficulty.csv에 실제 존재하는 시설 분류를 반영.
#
# 기존:
# 기반/조경/운동/교양/편익/기타/편의
#
# 실제 데이터에는
# 관리시설, 휴양시설, 유희시설,
# 문화예술시설, 생태시설, 체험시설 등이 추가로 존재한다.
FACILITY_CATEGORIES = [
    "문화예술시설",
    "기반시설",
    "조경시설",
    "운동시설",
    "교양시설",
    "편익시설",
    "기타시설",
    "편의시설",
    "관리시설",
    "휴양시설",
    "유희시설",
    "생태시설",
    "체험시설",
    "건축시설",
    "체육시설",
    "수경시설",
    # 실제 데이터에 존재하는 별도 구분
    "건축물",
    "상징광장",
    "열린숲",
]


FACILITY_PATTERN = build_category_pattern(FACILITY_CATEGORIES)


def parse_facilities(value):
    return parse_labeled_sections(
        value=value,
        categories=FACILITY_CATEGORIES,
        pattern=FACILITY_PATTERN,
    )


# ============================================================
# 식물
# ============================================================


# 실제 parks_difficulty.csv에서 확인되는 식물 분류.
#
# 기존처럼 "[가-힣 ]{1,20} :" 식으로 아무 문구나
# 카테고리로 잡으면 지나치게 넓게 매칭될 수 있으므로
# 실제 카테고리를 명시적으로 관리한다.
PLANT_CATEGORIES = [
    "천연기념물",
    "특산식물",
    "희귀식물",
    "수목식재",
    "지피식물",
    "보유식물",
    "지피초화류",
    "목본류",
    "교목류",
    "관목류",
    "수생식물",
    "키큰나무",
    "키작은나무",
    "초화류",
    "식물원",
    "수목",
    "초화",
    "관목",
    "교목",
    "동물",
    "붓꽃",
    "잔디",
    "목본",
    "초본",
]


PLANT_PATTERN = build_category_pattern(PLANT_CATEGORIES)


def parse_plants(value):
    return parse_labeled_sections(
        value=value,
        categories=PLANT_CATEGORIES,
        pattern=PLANT_PATTERN,
    )


# ============================================================
# 이용 안내
# ============================================================


NOTICE_HEADERS = [
    "일반사항",
    "이용시 참고사항",
]


NOTICE_SENTENCE_ENDINGS = [
    "이용합니다",
    "이용합시다",
    "이용해주세요",
    "이용해 주세요",
    "이용하세요",
    "금지합니다",
    "제한합니다",
    "보호합니다",
    "자제합니다",
    "않습니다",
    "없습니다",
    "있습니다",
    "가능합니다",
    "바랍니다",
    "해주세요",
    "해 주세요",
    "주십시오",
    "하십시오",
    "마세요",
]


def clean_notice_header(value):
    """
    리스트 첫 항목에 붙어 있는
    '일반사항', '이용시 참고사항' 등의 제목 제거.
    """

    value = value.strip()

    for header in NOTICE_HEADERS:
        if value.startswith(header):
            value = value[len(header) :].strip()

    return value


def split_notice(value):
    """
    이용 안내 문자열을 리스트로 변환한다.

    기존의 re.split(r"[.]+", value)는
    아래 값도 잘못 자를 수 있었다.

        0.73km
        2014.
        http://example.com

    따라서:
    1. 실제 문장 종료 표현
    2. 문장 사이의 마침표
    3. 명확한 bullet

    위주로만 분리한다.
    """

    value = normalize_text(value)

    if not value:
        return []

    # "주세요 . 다음 문장"
    # 같은 형태 정리
    value = re.sub(
        r"\s+\.",
        ".",
        value,
    )

    separator = "\u241e"

    # --------------------------------------------------------
    # 1. 한국어 문장 종결 표현
    # --------------------------------------------------------

    for ending in sorted(
        NOTICE_SENTENCE_ENDINGS,
        key=len,
        reverse=True,
    ):
        value = re.sub(
            rf"({re.escape(ending)})[.]?\s+" rf"(?=[가-힣A-Za-z0-9○※ㅇ])",
            rf"\1{separator}",
            value,
        )

    # --------------------------------------------------------
    # 2. 일반적인 문장 끝의 마침표
    #
    # 마침표 뒤에 공백 + 다음 문장이 있는 경우에만
    # 문장 구분으로 사용한다.
    #
    # 따라서:
    # 0.73
    # example.com
    #
    # 등은 유지된다.
    # --------------------------------------------------------

    value = re.sub(
        r"\.(?=\s+[가-힣A-Za-z0-9○※ㅇ])",
        separator,
        value,
    )

    # --------------------------------------------------------
    # 3. 명확한 bullet
    # --------------------------------------------------------

    value = re.sub(
        r"\s+(?=[○※])",
        separator,
        value,
    )

    value = re.sub(
        r"\s+-\s+(?=[가-힣A-Za-z0-9])",
        separator,
        value,
    )

    result = []

    for item in value.split(separator):
        item = item.strip(" .-·")

        if not item:
            continue

        item = clean_notice_header(item)

        if item:
            result.append(item)

    return result


# ============================================================
# JSON 배열
# ============================================================


def parse_json_list(value):
    value = safe_value(value)

    if value is None:
        return []

    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return []

    value = value.strip()

    if not value:
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except (json.JSONDecodeError, TypeError):
        return []


# ============================================================
# 찾아오는 길
# ============================================================


EXTRA_DIRECTION_SECTIONS = [
    "문의전화",
    "문의처",
    "주차장",
    "관리기관",
    "운영시간",
    "홈페이지",
]


def clean_direction_content(value):
    value = normalize_text(value)

    if not value:
        return ""

    # 가장 먼저 등장하는 부가 정보 위치까지만 사용
    indices = []

    for keyword in EXTRA_DIRECTION_SECTIONS:
        index = value.find(keyword)

        if index != -1:
            indices.append(index)

    if indices:
        value = value[: min(indices)]

    return value.strip()


def merge_walk_with_previous(routes):
    """
    도보가 독립 이동수단이 아니라
    앞 문장의 시간 표현으로 잘못 분리된 경우 병합.

    예:
        지하철
        성수역 4번 출구 300M (

        도보
        5분 거리)

    ->
        지하철
        성수역 4번 출구 300M (5분 거리)
    """

    result = []

    for route in routes:
        route_type = route["type"]
        content = route["content"]

        if (
            route_type == "도보"
            and result
            and (content.startswith(")") or content.endswith(")") or len(content) < 20)
        ):
            result[-1]["content"] += " " + content

            continue

        result.append(route)

    return result


def parse_directions(value):
    value = normalize_text(value)

    if not value:
        return []

    result = []

    # '마을버스' 안의 '버스'를 별도 버스로 잡지 않도록 처리.
    #
    # 승용차 역시 directions 데이터에 많이 존재하므로
    # 자동차와 동일한 이동수단으로 취급한다.
    pattern = re.compile(
        r"셔틀버스" r"|지하철" r"|자동차" r"|승용차" r"|도보" r"|(?<!마을)버스"
    )

    matches = list(pattern.finditer(value))

    if not matches:
        return [
            {
                "type": "기타",
                "content": value,
            }
        ]

    for i, match in enumerate(matches):
        route_type = match.group(0)

        # API에서는 자동차로 통일
        if route_type == "승용차":
            route_type = "자동차"

        start = match.end()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(value)

        content = value[start:end]

        content = clean_direction_content(content)

        content = content.strip(" :")

        if not content:
            continue

        result.append(
            {
                "type": route_type,
                "content": content,
            }
        )

    return merge_walk_with_previous(result)


# ============================================================
# 전체 변환
# ============================================================


def parse_park_detail(row):
    return {
        "facilities": parse_facilities(safe_value(row.get("facilities"))),
        "plants": parse_plants(safe_value(row.get("plants"))),
        "notices": split_notice(safe_value(row.get("notes"))),
        "directions": parse_directions(safe_value(row.get("directions"))),
    }
