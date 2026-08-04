from fastapi import APIRouter, Query
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
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    difficulty: str | None = Query(None),
    district: str | None = Query(None),
    pet_status: str | None = Query(None),
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
