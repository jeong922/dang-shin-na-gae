from app.utils.park_loader import load_parks

PARK_MAP_COLUMNS = [
    "id",
    "name",
    "lat",
    "lon",
    "difficulty",
    "avgSlope",
    "elevationDiff",
    "area",
    "district",
    "petStatus",
    "petRestrictedLocations",
    "serviceAnimalAllowed",
]


def get_map_parks():
    df = load_parks()

    df = df[PARK_MAP_COLUMNS]

    result = df.to_dict(orient="records")

    return {
        "items": result,
        "total": len(result),
    }
