from fastapi import APIRouter, Query
from app.services.parks import get_parks

router = APIRouter(
    prefix="/parks",
)


@router.get("")
def read_parks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
):
    return get_parks(page, page_size, keyword)
