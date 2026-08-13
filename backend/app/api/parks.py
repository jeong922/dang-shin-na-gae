from fastapi import APIRouter, Query

from typing import Annotated
from app.services.parks import get_parks
from app.schemas.park import ParkListResponse

router = APIRouter(
    prefix="/parks",
)

PARK_LIST_COLUMNS = [
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
]


@router.get(
    "",
    summary="공원 목록 조회",
    description="""
공원 목록을 조회합니다.

페이지 번호와 페이지 크기를 이용한 페이지네이션을 지원하며,
공원 이름 검색과 난이도, 자치구, 반려동물 출입 여부를 기준으로
공원 목록을 필터링할 수 있습니다.
""",
    response_model=ParkListResponse,
)
def read_parks(
    page: Annotated[
        int,
        Query(
            ge=1,
            description="조회할 페이지 번호",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="페이지당 공원 수",
        ),
    ] = 20,
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
    return get_parks(
        page=page,
        page_size=page_size,
        keyword=keyword,
        difficulty=difficulty,
        district=district,
        pet_status=pet_status,
        columns=PARK_LIST_COLUMNS,
    )
