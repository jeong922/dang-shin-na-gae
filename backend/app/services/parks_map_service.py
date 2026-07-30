from app.utils.park_loader import load_parks

PARK_LIST_COLUMNS = [
    "id",
    "name",
    "lat",
    "lon",
    "difficulty",
    "avgSlope",
    "elevationDiff",
    "area",
    "district",
]


def get_map_parks():
    df = load_parks()

    df = df[PARK_LIST_COLUMNS]

    result = df.to_dict(orient="records")

    return {
        "items": result,
        "total": len(result),
    }
