from app.utils.park_loader import load_parks

DEFAULT_COLUMNS = [
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


def get_search_parks(
    keyword: str | None = None,
    difficulty: list[str] | None = None,
    district: list[str] | None = None,
    pet_status: list[str] | None = None,
    columns: list[str] | None = None,
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

    # 필터
    if difficulty:
        df = df[df["difficulty"].isin(difficulty)]

    if district:
        df = df[df["district"].isin(district)]

    if pet_status:
        df = df[df["petStatus"].isin(pet_status)]

    # 필요한 컬럼만 선택
    if columns:
        df = df[columns]
    else:
        df = df[DEFAULT_COLUMNS]

    total = len(df)

    # 지도에서는 전체 반환
    return {
        "items": df.to_dict(orient="records"),
        "total": total,
    }
