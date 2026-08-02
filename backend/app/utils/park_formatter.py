import json
import re


def safe_value(value, default=None):
    if value is None:
        return default

    if isinstance(value, float):
        if value != value:
            return default

    return value


# ============================================
# 공통
# ============================================


def normalize_text(value: str):
    if not value:
        return ""

    value = str(value)

    value = value.replace("\n", " ")

    # 연속 공백 제거
    value = re.sub(r"\s+", " ", value)

    return value.strip()


# ============================================
# 이용 안내
# ============================================


def split_notice(value):

    if not value:
        return []

    value = normalize_text(value)

    result = re.split(r"[.]+", value)

    return [item.strip() for item in result if item.strip()]


# ============================================
# 시설
# ============================================


FACILITY_CATEGORIES = [
    "기반시설",
    "조경시설",
    "운동시설",
    "교양시설",
    "편익시설",
    "기타시설",
    "편의시설",
]


def parse_facilities(value):

    if not value:
        return []

    value = normalize_text(value)

    category_pattern = "|".join(FACILITY_CATEGORIES)

    pattern = rf"({category_pattern})\s*:"

    matches = list(re.finditer(pattern, value))

    result = []

    for i, match in enumerate(matches):

        category = match.group(1)

        start = match.end()

        end = matches[i + 1].start() if i + 1 < len(matches) else len(value)

        content = value[start:end].strip()

        if content:
            result.append(
                {
                    "category": category,
                    "content": content,
                }
            )

    if not result:
        result.append(
            {
                "category": None,
                "content": value,
            }
        )

    return result


# ============================================
# 식물
# ============================================


def parse_plants(value):

    if not value:
        return []

    value = normalize_text(value)

    result = []

    pattern = re.compile(
        r"([가-힣\s-]{1,20})\s*:\s*" r"(.*?)(?=\s+[가-힣\s-]{1,20}\s*:|$)"
    )

    matches = pattern.findall(value)

    for category, content in matches:

        category = category.strip()

        content = content.strip(" -")

        if category and content:

            result.append(
                {
                    "category": category,
                    "content": content,
                }
            )

    # 콜론 없는 데이터 보존

    if not result:

        result.append(
            {
                "category": None,
                "content": value,
            }
        )

    return result


# ============================================
# JSON 배열
# ============================================


def parse_json_list(value):

    if not value:
        return []

    if isinstance(value, list):
        return value

    try:
        return json.loads(value)

    except Exception:
        return []


# ============================================
# 찾아오는 길
# ============================================


EXTRA_DIRECTION_SECTIONS = [
    "문의전화",
    "주차장",
    "관리기관",
    "운영시간",
    "홈페이지",
]


def clean_direction_content(value):

    if not value:
        return ""

    for keyword in EXTRA_DIRECTION_SECTIONS:

        index = value.find(keyword)

        if index != -1:

            value = value[:index]

    return value.strip()


def merge_walk_with_previous(routes):
    """
    도보가 단독 단계가 아니라
    이전 교통수단의 연결 정보인 경우 병합

    예:
    지하철
    "성수역 4번 출구 300M ("

    도보
    "5분 거리)"

    ->
    지하철
    "성수역 4번 출구 300M (5분 거리)"
    """

    result = []

    for route in routes:

        content = route["content"]

        # 앞뒤 연결 조각
        if (
            route["type"] == "도보"
            and result
            and (content.startswith(")") or content.endswith(")") or len(content) < 20)
        ):

            result[-1]["content"] += " " + content

            continue

        result.append(route)

    return result


def parse_directions(value):

    if not value:
        return []

    value = normalize_text(value)

    result = []

    # 긴 단어 우선
    pattern = re.compile(r"셔틀버스|지하철|자동차|도보|(?<!마을)버스")

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

        start = match.end()

        end = matches[i + 1].start() if i + 1 < len(matches) else len(value)

        content = value[start:end]

        content = clean_direction_content(content)

        content = content.strip(" :")

        if content:

            result.append(
                {
                    "type": route_type,
                    "content": content,
                }
            )

    # 도보 분리 문제 보정
    result = merge_walk_with_previous(result)

    return result


# ============================================
# 전체 변환
# ============================================


def parse_park_detail(row):

    return {
        "facilities": parse_facilities(safe_value(row.get("facilities"))),
        "plants": parse_plants(safe_value(row.get("plants"))),
        "directions": parse_directions(safe_value(row.get("directions"))),
    }
