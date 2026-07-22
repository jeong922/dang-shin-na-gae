from fastapi import APIRouter

router = APIRouter(
    prefix="/parks",
    tags=["Parks"],
)


@router.get("")
def get_parks():
    return {"message": "공원 목록"}
