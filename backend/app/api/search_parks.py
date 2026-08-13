from fastapi import APIRouter, Query
from typing import Annotated

from app.schemas.park import ParkSearchResponse
from app.services.search import get_search_parks

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
    "/search",
    summary="공원 검색",
    description="공원 이름과 난이도, 자치구, 반려동물 출입 여부를 기준으로 공원을 검색합니다.",
    response_model=ParkSearchResponse,
)
def read_search_parks(
    keyword: Annotated[
        str | None,
        Query(
            description="공원 이름 검색어",
        ),
    ] = None,
    difficulty: Annotated[
        list[str] | None,
        Query(
            description="난이도 필터",
        ),
    ] = None,
    district: Annotated[
        list[str] | None,
        Query(
            description="자치구 필터",
        ),
    ] = None,
    pet_status: Annotated[
        list[str] | None,
        Query(
            description="반려동물 출입 여부 필터",
        ),
    ] = None,
):
    return get_search_parks(
        keyword=keyword,
        difficulty=difficulty,
        district=district,
        pet_status=pet_status,
        columns=PARK_MAP_COLUMNS,
    )
