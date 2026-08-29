from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent

FINAL_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

OSM_PROTECTED_PATH = (
    BASE_DIR
    / "data"
    / "osm"
    / "south-korea-latest-free.shp"
    / "gis_osm_protected_areas_a_free_1.shp"
)


# ============================================================
# 1. 데이터 읽기
# ============================================================

final_gdf = gpd.read_file(FINAL_GEOJSON_PATH)
osm_gdf = gpd.read_file(OSM_PROTECTED_PATH)


# ============================================================
# 2. 북한산 Polygon 추출
# ============================================================

current_bukhansan = final_gdf[final_gdf["park_name"] == "북한산국립공원"].copy()


# osm_id를 숫자로 변환
osm_gdf["osm_id_numeric"] = pd.to_numeric(
    osm_gdf["osm_id"],
    errors="coerce",
)

osm_bukhansan = osm_gdf[osm_gdf["osm_id_numeric"] == 17336247].copy()


# ============================================================
# 3. 데이터 확인
# ============================================================

print("=" * 70)
print("OSM ID 확인")
print("=" * 70)

print("원본 osm_id dtype:", osm_gdf["osm_id"].dtype)

print(
    osm_gdf.loc[
        osm_gdf["fclass"] == "national_park",
        ["osm_id", "osm_id_numeric", "fclass"],
    ].to_string(index=False)
)

print()
print("현재 북한산 Polygon 개수:", len(current_bukhansan))
print("OSM 북한산 Polygon 개수:", len(osm_bukhansan))


# 데이터가 없으면 여기서 중단
if current_bukhansan.empty:
    raise ValueError("현재 북한산 Polygon을 찾지 못했습니다.")

if osm_bukhansan.empty:
    raise ValueError("OSM osm_id=17336247 Polygon을 찾지 못했습니다.")


# ============================================================
# 4. CRS 통일
# ============================================================

current_bukhansan = current_bukhansan.to_crs(epsg=4326)
osm_bukhansan = osm_bukhansan.to_crs(epsg=4326)


# ============================================================
# 5. Bounds 비교
# ============================================================

print()
print("=" * 70)
print("Bounds 비교")
print("=" * 70)

print("현재 Polygon:", current_bukhansan.total_bounds)
print("OSM Polygon :", osm_bukhansan.total_bounds)

print()
print("현재 Geometry:", current_bukhansan.geometry.geom_type.tolist())
print("OSM Geometry :", osm_bukhansan.geometry.geom_type.tolist())


# ============================================================
# 6. 시각화
# ============================================================

fig, ax = plt.subplots(figsize=(10, 10))

current_bukhansan.plot(
    ax=ax,
    alpha=0.5,
    edgecolor="black",
)

osm_bukhansan.plot(
    ax=ax,
    alpha=0.5,
    edgecolor="black",
)

ax.set_title("Bukhansan Polygon Comparison")

plt.show()
