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


def get_parks(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    difficulty: str | None = None,
    district: str | None = None,
    pet_status: str | None = None,
):
    df = load_parks()

    # 검색
    if keyword:
        df = df[
            df["name"].str.contains(
                keyword,
                case=False,
                na=False,
            )
        ]

    if difficulty:
        df = df[df["difficulty"] == difficulty]

    if district:
        df = df[df["district"] == district]

    if pet_status:
        df = df[df["petStatus"] == pet_status]

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
