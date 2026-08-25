from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

MATCHES_CSV = BASE_DIR / "data" / "processed" / "official_park_matches.csv"


print("=" * 60)
print("전체 상태")
print("=" * 60)

matches = pd.read_csv(MATCHES_CSV)

print(matches["status"].value_counts())


print()
print("=" * 60)
print("검토 필요")
print("=" * 60)

review = matches[matches["status"] == "review"]

print(
    review[
        [
            "park_id",
            "park_name",
            "polygon_id",
            "polygon_label",
            "total_score",
            "name_score",
            "spatial_score",
            "distance_m",
            "candidate_count",
            "second_score",
            "score_margin",
        ]
    ].to_string(index=False)
)


print()
print("=" * 60)
print("매칭 실패")
print("=" * 60)

unmatched = matches[matches["status"] == "unmatched"]

print(
    unmatched[
        [
            "park_id",
            "park_name",
            "polygon_label",
            "total_score",
            "distance_m",
        ]
    ].to_string(index=False)
)
