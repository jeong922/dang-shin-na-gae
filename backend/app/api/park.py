from fastapi import APIRouter, HTTPException, Path

from app.schemas.error import ErrorResponse
from app.schemas.park import ParkDetailResponse
from app.services.park import get_park_detail

router = APIRouter(
    prefix="/parks",
)


@router.get(
    "/{park_id}",
    summary="공원 상세 정보 조회",
    description="""
공원 ID를 기준으로 특정 공원의 상세 정보를 조회합니다.

공원의 기본 정보뿐만 아니라 위치, 시설, 식물,
난이도, 반려동물 출입 정보, 이용 안내, 연락처 및 이미지 정보를 제공합니다.
""",
    response_model=ParkDetailResponse,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "공원을 찾을 수 없습니다.",
        },
    },
)
def read_park_detail(
    park_id: int = Path(
        description="조회할 공원의 ID",
        examples=[1],
    ),
):
    park = get_park_detail(park_id)

    if not park:
        raise HTTPException(
            status_code=404,
            detail="공원을 찾을 수 없습니다.",
        )

    return park
