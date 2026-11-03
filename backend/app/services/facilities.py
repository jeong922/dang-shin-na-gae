import pandas as pd

from app.schemas.facility import FacilityType
from app.utils.facility_loader import load_facilities
from app.utils.geo import haversine_distance
from app.utils.park_loader import load_parks

MAP_COLUMNS = [
    "facility_id",
    "name",
    "facility_type",
    "lat",
    "lon",
    "distance_meters",
    "allowed_pet_size",
    "pet_restrictions",
    "indoor",
    "outdoor",
    "opening_hours",
]


def format_facility(row):
    # 결측값을 JSON null로 변환하고 camelCase 변환하여 리턴
    result = {}

    for key, value in row.items():
        parts = key.split("_")
        column = parts[0] + "".join(part.title() for part in parts[1:])
        result[column] = None if pd.isna(value) else value

    return result


def nearby_facilities(
    park_id: int,
    radius_meters: float,
    facility_type: list[FacilityType] | None = None,
):
    # 기준 공원 조회
    parks = load_parks()
    park = parks.loc[parks["id"] == park_id]

    if park.empty:
        return None

    park = park.iloc[0]
    df = load_facilities()

    # 카테고리 필터
    if facility_type:
        df = df.loc[df["facility_type"].isin(facility_type)]

    df = df.copy()

    # 공원 경계가 아닌 대표 좌표를 기준으로 시설까지의 직선거리 계산
    df["distance_meters"] = haversine_distance(
        origin_lat=float(park["lat"]),
        origin_lon=float(park["lon"]),
        target_lats=df["lat"].to_numpy(dtype=float),
        target_lons=df["lon"].to_numpy(dtype=float),
    )

    # 탐색 반경 내 시설 필터링
    nearby_df = df.loc[df["distance_meters"] <= radius_meters]

    # 거리순 정렬 (동일 거리일 경우 시설 ID순)
    return nearby_df.sort_values(["distance_meters", "facility_id"])


def get_map_facilities(
    park_id: int,
    radius_meters: float,
    facility_type: list[FacilityType] | None = None,
):
    df = nearby_facilities(
        park_id=park_id,
        radius_meters=radius_meters,
        facility_type=facility_type,
    )

    if df is None:
        return None

    return {
        "items": [format_facility(row) for row in df[MAP_COLUMNS].to_dict("records")],
        "total": len(df),
    }
