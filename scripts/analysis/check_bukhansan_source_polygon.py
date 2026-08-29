from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SHP_PATH = BASE_DIR / "data" / "seoul_parks" / "seoul_parks.shp"
OSM_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"


# ============================================================
# 서울시 SHP
# ============================================================

seoul = gpd.read_file(SHP_PATH)

seoul_target = seoul[seoul["ID"] == "생활서비스시설_공원_0431"]

print("=" * 70)
print("서울시 SHP")
print("=" * 70)

print(seoul_target.drop(columns="geometry").T)
print(seoul_target.geometry.geom_type)


# ============================================================
# OSM
# ============================================================

osm = gpd.read_file(OSM_PATH)

print("\nOSM columns:", osm.columns.tolist())

osm_target = osm[osm["name"].str.contains("북한산", na=False)]

print("\n" + "=" * 70)
print("OSM")
print("=" * 70)

print(osm_target.drop(columns="geometry").T)
print(osm_target.geometry.geom_type)


# ============================================================
# CRS 통일
# ============================================================

if seoul_target.crs != osm_target.crs:
    osm_target = osm_target.to_crs(seoul_target.crs)


# ============================================================
# 비교 시각화
# ============================================================

ax = seoul_target.plot(
    figsize=(12, 12),
    alpha=0.4,
    edgecolor="black",
)

osm_target.plot(
    ax=ax,
    alpha=0.4,
    edgecolor="black",
)

ax.set_title("북한산 Polygon 비교 - 서울시 SHP / OSM")
ax.set_aspect("equal")

plt.show()
