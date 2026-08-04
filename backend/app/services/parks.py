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


def get_parks(
    page: int | None = None,
    page_size: int | None = None,
    keyword: str | None = None,
    difficulty: str | None = None,
    district: str | None = None,
    pet_status: str | None = None,
    bbox: tuple[float, float, float, float] | None = None,
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

    # 지도 영역
    if bbox:
        west, south, east, north = bbox

        df = df[
            (df["lon"] >= west)
            & (df["lon"] <= east)
            & (df["lat"] >= south)
            & (df["lat"] <= north)
        ]

    # 필터
    if difficulty:
        df = df[df["difficulty"] == difficulty]

    if district:
        df = df[df["district"] == district]

    if pet_status:
        df = df[df["petStatus"] == pet_status]

    # 필요한 컬럼만 선택
    if columns:
        df = df[columns]
    else:
        df = df[DEFAULT_COLUMNS]

    total = len(df)

    # 페이지네이션 (목록에서만 사용)
    if page is not None and page_size is not None:
        start = (page - 1) * page_size
        end = start + page_size

        items = df.iloc[start:end].to_dict(orient="records")

        return {
            "items": items,
            "page": page,
            "pageSize": page_size,
            "total": total,
            "totalPages": (total + page_size - 1) // page_size,
        }

    # 지도에서는 전체 반환
    return {
        "items": df.to_dict(orient="records"),
        "total": total,
    }
