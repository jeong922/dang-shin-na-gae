from fastapi import APIRouter, Query
from typing import Annotated
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


@router.get("/search")
def read_search_parks(
    keyword: Annotated[str | None, Query()] = None,
    difficulty: Annotated[list[str] | None, Query()] = None,
    district: Annotated[list[str] | None, Query()] = None,
    pet_status: Annotated[list[str] | None, Query()] = None,
):
    return get_search_parks(
        keyword=keyword,
        difficulty=difficulty,
        district=district,
        pet_status=pet_status,
        columns=PARK_MAP_COLUMNS,
    )
