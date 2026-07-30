from app.utils.park_loader import load_parks


def get_park_detail(park_id: int):
    df = load_parks()

    park = df.loc[df["id"] == park_id]

    if park.empty:
        return None

    return park.iloc[0].to_dict()
