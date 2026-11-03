import numpy as np


def haversine_distance(
    origin_lat: float,
    origin_lon: float,
    target_lats: np.ndarray,
    target_lons: np.ndarray,
) -> np.ndarray:

    # 위도·경도를 라디안으로 변환
    origin_lat = np.radians(origin_lat)
    origin_lon = np.radians(origin_lon)

    target_lats = np.radians(target_lats)
    target_lons = np.radians(target_lons)

    # 위도·경도 차이 계산
    lat_diff = target_lats - origin_lat
    lon_diff = target_lons - origin_lon

    # Haversine 공식의 중간값 계산
    latitude_term = np.sin(lat_diff / 2) ** 2
    longitude_term = (
        np.cos(origin_lat) * np.cos(target_lats) * np.sin(lon_diff / 2) ** 2
    )

    haversine_value = latitude_term + longitude_term

    # 부동소수점 오차로 중간값이 이론적 범위인 0~1을 벗어나지 않도록 보정
    haversine_value = np.clip(haversine_value, 0, 1)

    # 지구 중심에서 두 지점을 바라본 각도(라디안) 계산
    central_angle = 2 * np.arcsin(np.sqrt(haversine_value))

    # 지구 평균 반지름(m)
    earth_radius_meters = 6371008.8

    # 지구 반지름과 중심각을 곱해 지표면상의 최단거리(m) 반환
    return earth_radius_meters * central_angle
