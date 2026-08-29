from pathlib import Path

import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent.parent

GEOJSON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"


gdf = gpd.read_file(GEOJSON_PATH)

row = gdf[gdf["park_name"].str.contains("북한산", na=False)]

print(row.drop(columns="geometry").T)
print(row.geometry.geom_type)
