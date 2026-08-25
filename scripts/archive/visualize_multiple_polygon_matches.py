from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

CLASSIFIED_CSV = BASE_DIR / "data" / "processed" / "classified_review_matches.csv"

REVIEW_CANDIDATES_CSV = (
    BASE_DIR / "data" / "processed" / "review_candidate_analysis.csv"
)

SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "multiple_polygon_plots"


# ============================================================
# 설정
# ============================================================

# 공원별 상위 몇 개 후보 Polygon을 보여줄 것인지
TOP_N = 5

# 지도 주변 여백 (meter)
PADDING_M = 500


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

classified = pd.read_csv(CLASSIFIED_CSV)

candidates = pd.read_csv(REVIEW_CANDIDATES_CSV)

polygons = gpd.read_file(SHP_PATH)


# ============================================================
# multiple_polygons 대상 추출
# ============================================================

multiple = classified[classified["classification"] == "multiple_polygons"].copy()


print("=" * 70)
print("multiple_polygons 분석")
print("=" * 70)

print(
    "대상 공원 개수:",
    len(multiple),
)

print()

print(
    multiple[
        [
            "park_id",
            "park_name",
        ]
    ].to_string(index=False)
)


# ============================================================
# 공원 Point 생성
# ============================================================

park_points = gpd.GeoDataFrame(
    parks.copy(),
    geometry=gpd.points_from_xy(
        parks["lon"],
        parks["lat"],
    ),
    crs="EPSG:4326",
)


# ============================================================
# Polygon CRS로 변환
# ============================================================

park_points = park_points.to_crs(polygons.crs)


# ============================================================
# 출력 폴더 생성
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# 공원별 시각화
# ============================================================

for _, match in multiple.iterrows():

    park_id = match["park_id"]
    park_name = match["park_name"]

    print()
    print("=" * 70)
    print(f"처리 시작: park_id={park_id}, park_name={park_name}")
    print("=" * 70)

    # --------------------------------------------------------
    # 공원 Point
    # --------------------------------------------------------

    park_row = park_points[park_points["id"] == park_id]

    if park_row.empty:
        print(f"[WARNING] {park_name}: " "공원 Point를 찾을 수 없습니다.")
        continue

    print("공원 Point 확인 완료")

    park_point = park_row.iloc[0].geometry

    # --------------------------------------------------------
    # 해당 공원의 후보
    # --------------------------------------------------------

    park_candidates = candidates[candidates["park_id"] == park_id].copy()

    park_candidates = park_candidates.sort_values("rank").head(TOP_N)

    print(f"후보 Polygon 개수: " f"{len(park_candidates)}")

    if park_candidates.empty:
        print(f"[WARNING] {park_name}: " "후보가 없습니다.")
        continue

    # --------------------------------------------------------
    # 후보 Polygon 인덱스
    # --------------------------------------------------------

    candidate_indices = park_candidates["polygon_index"].astype(int).tolist()

    # --------------------------------------------------------
    # 후보 Polygon 추출
    #
    # review_candidate_analysis.csv의 polygon_index는
    # deduplicated Shapefile의 iloc 기준 인덱스
    # --------------------------------------------------------

    candidate_polygons = polygons.iloc[candidate_indices].copy()

    # rank 정보 추가
    candidate_polygons["rank"] = park_candidates["rank"].astype(int).to_numpy()

    candidate_polygons["candidate_label"] = park_candidates["polygon_label"].to_numpy()

    candidate_polygons["total_score"] = park_candidates["total_score"].to_numpy()

    candidate_polygons["distance_m"] = park_candidates["distance_m"].to_numpy()

    # ========================================================
    # 그래프
    # ========================================================

    fig, ax = plt.subplots(figsize=(10, 10))

    # --------------------------------------------------------
    # 주변 Polygon 표시
    # --------------------------------------------------------

    search_area = park_point.buffer(PADDING_M)

    nearby = polygons[polygons.intersects(search_area)]

    nearby.plot(
        ax=ax,
        facecolor="none",
        edgecolor="lightgray",
        linewidth=0.7,
    )

    # --------------------------------------------------------
    # 후보 Polygon 표시
    # --------------------------------------------------------

    candidate_polygons.plot(
        ax=ax,
        alpha=0.35,
        edgecolor="black",
        linewidth=2,
    )

    # --------------------------------------------------------
    # 공원 대표 Point 표시
    # --------------------------------------------------------

    ax.scatter(
        park_point.x,
        park_point.y,
        s=100,
        marker="x",
        zorder=10,
    )

    # --------------------------------------------------------
    # 후보 번호 표시
    # --------------------------------------------------------

    for _, polygon in candidate_polygons.iterrows():

        representative_point = polygon.geometry.representative_point()

        ax.text(
            representative_point.x,
            representative_point.y,
            str(polygon["rank"]),
            fontsize=12,
            fontweight="bold",
            ha="center",
            va="center",
        )

    # --------------------------------------------------------
    # 화면 범위
    # --------------------------------------------------------

    combined = candidate_polygons.geometry.union_all()

    bounds = combined.bounds

    min_x = min(
        bounds[0],
        park_point.x,
    )

    min_y = min(
        bounds[1],
        park_point.y,
    )

    max_x = max(
        bounds[2],
        park_point.x,
    )

    max_y = max(
        bounds[3],
        park_point.y,
    )

    ax.set_xlim(
        min_x - PADDING_M,
        max_x + PADDING_M,
    )

    ax.set_ylim(
        min_y - PADDING_M,
        max_y + PADDING_M,
    )

    # --------------------------------------------------------
    # 제목
    # --------------------------------------------------------

    ax.set_title(
        f"{park_name} - Polygon candidates",
        fontsize=15,
    )

    ax.set_aspect("equal")

    # ========================================================
    # 후보 정보 텍스트
    # ========================================================

    info_lines = []

    for _, row in park_candidates.iterrows():

        info_lines.append(
            f'{int(row["rank"])}. '
            f'{row["polygon_label"]} | '
            f'score={row["total_score"]:.2f} | '
            f'distance={row["distance_m"]:.2f}m'
        )

    info_text = "\n".join(info_lines)

    fig.text(
        0.02,
        0.02,
        info_text,
        fontsize=9,
        verticalalignment="bottom",
    )

    # --------------------------------------------------------
    # 축 제거
    # --------------------------------------------------------

    ax.set_axis_off()

    # --------------------------------------------------------
    # 파일명 안전하게 생성
    # --------------------------------------------------------

    safe_name = (
        str(park_name)
        .replace("/", "_")
        .replace("\\", "_")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
    )

    output_path = OUTPUT_DIR / f"{park_id}_{safe_name}.png"

    # --------------------------------------------------------
    # 저장
    # --------------------------------------------------------

    plt.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    print()
    print("=" * 70)

    print(f"[{park_id}] {park_name}")

    print("-" * 70)

    print(
        park_candidates[
            [
                "rank",
                "polygon_id",
                "polygon_label",
                "total_score",
                "name_score",
                "spatial_score",
                "distance_m",
                "point_inside",
            ]
        ].to_string(index=False)
    )

    print()
    print(
        "그래프 저장:",
        output_path,
    )

    plt.close(fig)


print()
print("=" * 70)
print("시각화 완료")
print("=" * 70)

print(
    "저장 폴더:",
    OUTPUT_DIR,
)
