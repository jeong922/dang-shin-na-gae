from fastapi import APIRouter, Query
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


@router.get("/map")
def read_map_parks(
    west: float | None = Query(None),
    south: float | None = Query(None),
    east: float | None = Query(None),
    north: float | None = Query(None),
    keyword: str | None = Query(None),
    difficulty: str | None = Query(None),
    district: str | None = Query(None),
    pet_status: str | None = Query(None),
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
