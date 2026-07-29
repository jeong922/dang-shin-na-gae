from fastapi import APIRouter
from app.services.parks_map_service import get_map_parks

router = APIRouter(
    prefix="/parks",
)


@router.get("/map")
def read_map_parks():
    return get_map_parks()
