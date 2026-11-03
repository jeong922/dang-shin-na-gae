from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.schemas.facility import FacilityMapResponse, FacilityType
from app.services.facilities import (
    get_map_facilities,
)

router = APIRouter(
    prefix="/facilities",
    tags=["시설"],
)


@router.get(
    "/map",
    summary="공원 주변 시설 지도 조회",
    description="""
공원 좌표를 기준으로 탐색 반경에 포함된 시설을 조회합니다.

시설 카테고리로 필터링할 수 있으며, 지도 표시에 필요한 위치와 직선거리를 제공합니다.
""",
    response_model=FacilityMapResponse,
)
def read_map_facilities(
    park_id: Annotated[
        int,
        Query(
            description="주변 시설 탐색의 기준이 되는 공원 ID",
        ),
    ],
    radius_meters: Annotated[
        float,
        Query(
            gt=0,
            le=10000,
            allow_inf_nan=False,
            description="공원 좌표 기준 탐색 반경(m)",
        ),
    ] = 1000,
    facility_type: Annotated[
        list[FacilityType] | None,
        Query(
            description="시설 유형(복수 선택: Windows는 Ctrl, macOS는 Cmd를 누른 채 클릭)",
        ),
    ] = None,
):
    result = get_map_facilities(
        park_id=park_id,
        radius_meters=radius_meters,
        facility_type=facility_type,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="공원을 찾을 수 없습니다.",
        )

    return result
