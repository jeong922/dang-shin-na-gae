from fastapi import APIRouter, Query
from typing import Annotated
from app.services.parks import get_parks

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


@router.get("")
def read_parks(
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    keyword: Annotated[str | None, Query()] = None,
    difficulty: Annotated[list[str] | None, Query()] = None,
    district: Annotated[list[str] | None, Query()] = None,
    pet_status: Annotated[list[str] | None, Query()] = None,
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
