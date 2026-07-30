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
    "petStatus",
]


def get_parks(page: int = 1, page_size: int = 20):
    df = load_parks()

    df = df[PARK_LIST_COLUMNS]

    total = len(df)

    start = (page - 1) * page_size
    end = start + page_size

    items = df.iloc[start:end].to_dict(
        orient="records",
    )

    return {
        "items": items,
        "page": page,
        "pageSize": page_size,
        "total": total,
        "totalPages": (total + page_size - 1) // page_size,
    }
