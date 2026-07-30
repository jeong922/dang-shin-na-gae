from fastapi import APIRouter, HTTPException

from app.services.park import get_park_detail

router = APIRouter(
    prefix="/parks",
)


@router.get("/{park_id}")
def read_park_detail(
    park_id: int,
):
    park = get_park_detail(park_id)

    if not park:
        raise HTTPException(
            status_code=404,
            detail="공원을 찾을 수 없습니다.",
        )

    return park
