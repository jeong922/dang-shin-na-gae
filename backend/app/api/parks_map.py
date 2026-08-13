from fastapi import APIRouter, Query
from typing import Annotated
from app.services.parks import get_parks

router = APIRouter(
    prefix="/parks",
)

PARK_MAP_COLUMNS = [
    "id",
    "name",
    "lat",
    "lon",
    "difficulty",
    "avgSlope",
    "elevationDiff",
    "area",
    "district",
    "petStatus",
    "petRestrictedLocations",
    "serviceAnimalAllowed",
]


@router.get(
    "/map",
    summary="공원 위치 정보 조회",
    description="""
지도에 공원 위치를 표시하기 위한 공원 정보를 조회합니다.

지도 영역을 기준으로 조회할 수 있으며,
검색어, 난이도, 자치구, 반려동물 출입 여부를 이용해 공원을 필터링할 수 있습니다.

반환 데이터는 지도 마커 표시와 필터링에 필요한 공원 기본 정보를 포함합니다.
""",
)
def read_map_parks(
    west: float | None = Query(
        None,
        description="지도 영역의 서쪽 경도",
        examples=[126.8],
    ),
    south: float | None = Query(
        None,
        description="지도 영역의 남쪽 위도",
        examples=[37.4],
    ),
    east: float | None = Query(
        None,
        description="지도 영역의 동쪽 경도",
        examples=[127.1],
    ),
    north: float | None = Query(
        None,
        description="지도 영역의 북쪽 위도",
        examples=[37.7],
    ),
    keyword: Annotated[
        str | None,
        Query(description="공원 이름 검색"),
    ] = None,
    difficulty: Annotated[
        list[str] | None,
        Query(description="공원 난이도 필터"),
    ] = None,
    district: Annotated[
        list[str] | None,
        Query(description="자치구 필터"),
    ] = None,
    pet_status: Annotated[
        list[str] | None,
        Query(description="반려동물 출입 여부 필터"),
    ] = None,
):
    bbox = None

    if None not in (west, south, east, north):
        bbox = (west, south, east, north)

    return get_parks(
        keyword=keyword,
        difficulty=difficulty,
        district=district,
        pet_status=pet_status,
        bbox=bbox,
        columns=PARK_MAP_COLUMNS,
    )
