from app.utils.park_loader import load_parks

from app.utils.park_formatter import (
    parse_facilities,
    parse_plants,
    parse_directions,
    split_notice,
    parse_json_list,
)


def get_park_detail(park_id: int):

    df = load_parks()

    park = df.loc[df["id"] == park_id]

    if park.empty:
        return None

    park = park.iloc[0]

    return {
        "id": int(park["id"]),
        "name": park["name"],
        "description": park.get("description", ""),
        "location": {
            "lat": float(park["lat"]),
            "lon": float(park["lon"]),
            "district": park["district"],
            "address": park.get("address", ""),
        },
        "information": {
            "area": float(park["area"]),
            "openedAt": park.get("openedAt", ""),
            "facilities": parse_facilities(park.get("facilities")),
            "plants": parse_plants(park.get("plants")),
        },
        "difficulty": {
            "level": park["difficulty"],
            "avgSlope": float(park["avgSlope"]),
            "elevationDiff": float(park["elevationDiff"]),
        },
        "pet": {
            "status": park["petStatus"],
            "notices": parse_json_list(park.get("petNotice")),
            "restrictedLocations": parse_json_list(park.get("petRestrictedLocations")),
            "serviceAnimalAllowed": bool(park["serviceAnimalAllowed"]),
        },
        "notices": split_notice(park.get("notes")),
        "directions": parse_directions(park.get("directions")),
        "contact": {
            "department": park.get("department", ""),
            "phone": park.get("phone", ""),
            "url": park.get("url", ""),
        },
        "images": {
            "image": park.get("image", ""),
            "map": park.get("mapImage", ""),
        },
    }
