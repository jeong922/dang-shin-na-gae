from pathlib import Path
import re

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

# ============================================================
# 경로
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

PARKS_CSV = BASE_DIR / "data" / "processed" / "parks.csv"

FINAL_POLYGON_PATH = BASE_DIR / "data" / "processed" / "final_park_polygons.geojson"

SEOUL_SHP_PATH = (
    BASE_DIR / "data" / "seoul_parks" / "deduplicated" / "seoul_parks_deduplicated.shp"
)

OSM_GEOJSON_PATH = BASE_DIR / "data" / "processed" / "seoul_parks_osm.geojson"

CANDIDATES_CSV = BASE_DIR / "data" / "analysis" / "polygon_area_mismatch_candidates.csv"

OUTPUT_DIR = BASE_DIR / "data" / "analysis" / "polygon_mismatch_plots"


# ============================================================
# 설정
# ============================================================

TARGET_PARK_IDS = [
    109,  # 초안산생태공원
    4,  # 서울숲
    126,  # 용마도시자연공원(사가정공원)
    98,  # 발바닥공원
    91,  # 북서울꿈의숲
    79,  # 삼청근린공원
    64,  # 봉은공원
]

# source별 상위 후보 몇 개를 그릴지
TOP_N = 3

# 지도 여백
PADDING_M = 300


# ============================================================
# 파일 존재 확인
# ============================================================

required_files = [
    PARKS_CSV,
    FINAL_POLYGON_PATH,
    SEOUL_SHP_PATH,
    OSM_GEOJSON_PATH,
    CANDIDATES_CSV,
]

for path in required_files:
    if not path.exists():
        raise FileNotFoundError(f"필요한 파일을 찾을 수 없습니다:\n{path}")


# ============================================================
# 데이터 읽기
# ============================================================

parks = pd.read_csv(PARKS_CSV)

final_polygons = gpd.read_file(FINAL_POLYGON_PATH)

seoul_polygons = gpd.read_file(SEOUL_SHP_PATH)

osm_polygons = gpd.read_file(OSM_GEOJSON_PATH)

candidates = pd.read_csv(CANDIDATES_CSV)


print("=" * 70)
print("데이터 정보")
print("=" * 70)

print(
    "공원:",
    len(parks),
)

print(
    "최종 Polygon:",
    len(final_polygons),
)

print(
    "서울시 Polygon:",
    len(seoul_polygons),
)

print(
    "OSM Polygon:",
    len(osm_polygons),
)

print(
    "후보 행:",
    len(candidates),
)


# ============================================================
# CRS 통일
# ============================================================
#
# 거리/지도 표현을 위해 EPSG:5186으로 변환.
# ============================================================

final_m = final_polygons.to_crs("EPSG:5186")

seoul_m = seoul_polygons.to_crs("EPSG:5186")

osm_m = osm_polygons.to_crs("EPSG:5186")


# ============================================================
# 공원 대표 좌표 GeoDataFrame
# ============================================================

park_points = gpd.GeoDataFrame(
    parks.copy(),
    geometry=gpd.points_from_xy(
        parks["lon"],
        parks["lat"],
    ),
    crs="EPSG:4326",
)

park_points_m = park_points.to_crs("EPSG:5186")


# ============================================================
# 후보 데이터 정렬
# ============================================================
#
# 기존 analyze_polygon_area_mismatches.py와 동일하게
#
# 1. name_score 높은 순
# 2. area_difference 낮은 순
# 3. distance_m 낮은 순
#
# 기준으로 다시 정렬한다.
# ============================================================

candidates = candidates.sort_values(
    by=[
        "park_id",
        "candidate_source",
        "name_score",
        "area_difference",
        "distance_m",
    ],
    ascending=[
        True,
        True,
        False,
        True,
        True,
    ],
)


# ============================================================
# 파일명 안전화
# ============================================================


def sanitize_filename(value):
    """
    Windows에서도 사용할 수 있도록
    파일명에 부적절한 문자를 제거한다.
    """

    value = str(value)

    value = re.sub(
        r'[\\/:*?"<>|]',
        "_",
        value,
    )

    value = re.sub(
        r"\s+",
        "_",
        value,
    )

    return value.strip("_")


# ============================================================
# 후보 Polygon 가져오기
# ============================================================


def get_candidate_geometry(
    candidate,
):
    """
    candidate_source와 candidate_id를 이용해
    실제 Polygon geometry를 가져온다.
    """

    source = candidate["candidate_source"]

    candidate_id = str(candidate["candidate_id"])

    if source == "seoul":

        selected = seoul_m[seoul_m["ID"].astype(str) == candidate_id].copy()

    elif source == "osm":

        selected = osm_m[osm_m["osm_id"].astype(str) == candidate_id].copy()

    else:

        raise ValueError(f"알 수 없는 candidate_source: {source}")

    if selected.empty:
        return None

    # 동일 ID가 여러 개라면
    # 첫 번째 객체 사용.
    return selected.iloc[0].geometry


# ============================================================
# 후보 요약 출력
# ============================================================


def print_candidate_summary(
    park_candidates,
    source,
):
    """
    콘솔에서 이미지 후보 번호와
    실제 후보 정보를 같이 확인하기 위한 출력.
    """

    source_candidates = park_candidates[
        park_candidates["candidate_source"] == source
    ].head(TOP_N)

    prefix = "S" if source == "seoul" else "O"

    if source_candidates.empty:

        print(f"[{source}] 후보 없음")

        return

    for index, (_, row) in enumerate(
        source_candidates.iterrows(),
        start=1,
    ):

        print(
            f"{prefix}{index} "
            f"{row['candidate_name']} | "
            f"distance={row['distance_m']:.2f}m | "
            f"area={row['candidate_area_m2']:,.2f}㎡ | "
            f"ratio={row['area_ratio']:.4f} | "
            f"name={row['name_score']:.2f}"
        )


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

for park_id in TARGET_PARK_IDS:

    # --------------------------------------------------------
    # 공원 정보
    # --------------------------------------------------------

    park_row = park_points_m[park_points_m["id"] == park_id]

    if park_row.empty:

        print()
        print(f"[{park_id}] parks.csv에서 찾을 수 없습니다.")

        continue

    if len(park_row) > 1:

        raise ValueError(f"park_id={park_id}가 parks.csv에 " "여러 개 존재합니다.")

    park_row = park_row.iloc[0]

    park_name = park_row["name"]

    park_point = park_row.geometry

    official_area = park_row["area"]

    # --------------------------------------------------------
    # 해당 공원 후보
    # --------------------------------------------------------

    park_candidates = candidates[candidates["park_id"] == park_id].copy()

    print()
    print()
    print("=" * 70)
    print(f"[{park_id}] {park_name}")
    print("=" * 70)

    print(
        "공식 면적:",
        (f"{official_area:,.2f}㎡" if pd.notna(official_area) else "없음"),
    )

    # --------------------------------------------------------
    # 현재 Polygon
    # --------------------------------------------------------

    current = final_m[final_m["park_id"] == park_id].copy()

    if current.empty:

        current_geometry = None

        print("현재 Polygon: 없음")

    else:

        current_geometry = current.iloc[0].geometry

        current_area = current_geometry.area

        print(
            "현재 Polygon:",
            f"{current_area:,.2f}㎡",
        )

    # --------------------------------------------------------
    # 후보 콘솔 출력
    # --------------------------------------------------------

    print()
    print("[서울시 후보]")

    print_candidate_summary(
        park_candidates,
        source="seoul",
    )

    print()
    print("[OSM 후보]")

    print_candidate_summary(
        park_candidates,
        source="osm",
    )

    # ========================================================
    # Figure 생성
    # ========================================================

    fig, ax = plt.subplots(
        figsize=(
            10,
            10,
        )
    )

    # --------------------------------------------------------
    # 현재 Polygon
    # --------------------------------------------------------

    geometries_for_bounds = [park_point]

    if current_geometry is not None:

        gpd.GeoSeries(
            [current_geometry],
            crs="EPSG:5186",
        ).plot(
            ax=ax,
            facecolor="none",
            edgecolor="black",
            linewidth=3,
        )

        geometries_for_bounds.append(current_geometry)

    # --------------------------------------------------------
    # 서울시 후보
    # --------------------------------------------------------

    seoul_candidates = park_candidates[
        park_candidates["candidate_source"] == "seoul"
    ].head(TOP_N)

    for index, (_, candidate) in enumerate(
        seoul_candidates.iterrows(),
        start=1,
    ):

        geometry = get_candidate_geometry(candidate)

        if geometry is None:
            continue

        gpd.GeoSeries(
            [geometry],
            crs="EPSG:5186",
        ).plot(
            ax=ax,
            facecolor="none",
            linestyle="--",
            linewidth=2,
        )

        label_point = geometry.representative_point()

        ax.text(
            label_point.x,
            label_point.y,
            f"S{index}",
            fontsize=11,
            fontweight="bold",
        )

        geometries_for_bounds.append(geometry)

    # --------------------------------------------------------
    # OSM 후보
    # --------------------------------------------------------

    osm_candidates = park_candidates[park_candidates["candidate_source"] == "osm"].head(
        TOP_N
    )

    for index, (_, candidate) in enumerate(
        osm_candidates.iterrows(),
        start=1,
    ):

        geometry = get_candidate_geometry(candidate)

        if geometry is None:
            continue

        gpd.GeoSeries(
            [geometry],
            crs="EPSG:5186",
        ).plot(
            ax=ax,
            facecolor="none",
            linestyle=":",
            linewidth=2,
        )

        label_point = geometry.representative_point()

        ax.text(
            label_point.x,
            label_point.y,
            f"O{index}",
            fontsize=11,
            fontweight="bold",
        )

        geometries_for_bounds.append(geometry)

    # --------------------------------------------------------
    # 공원 대표 좌표
    # --------------------------------------------------------

    ax.scatter(
        park_point.x,
        park_point.y,
        s=100,
        marker="x",
        linewidths=3,
        zorder=10,
    )

    ax.text(
        park_point.x,
        park_point.y,
        " PARK",
        fontsize=10,
        fontweight="bold",
        verticalalignment="bottom",
    )

    # ========================================================
    # 지도 범위 결정
    # ========================================================

    bounds_series = gpd.GeoSeries(
        geometries_for_bounds,
        crs="EPSG:5186",
    )

    min_x, min_y, max_x, max_y = bounds_series.total_bounds

    width = max_x - min_x

    height = max_y - min_y

    # 지나치게 작은 범위 방지
    padding = max(
        PADDING_M,
        width * 0.1,
        height * 0.1,
    )

    ax.set_xlim(
        min_x - padding,
        max_x + padding,
    )

    ax.set_ylim(
        min_y - padding,
        max_y + padding,
    )

    # ========================================================
    # 그래프 정보
    # ========================================================

    title = (
        f"[{park_id}] {park_name}\n" f"공식 면적: " f"{official_area:,.0f}㎡"
        if pd.notna(official_area)
        else f"[{park_id}] {park_name}"
    )

    ax.set_title(
        title,
        fontsize=14,
    )

    ax.set_aspect("equal")

    ax.set_xlabel("EPSG:5186 X")

    ax.set_ylabel("EPSG:5186 Y")

    # ========================================================
    # 설명
    # ========================================================

    info_lines = [
        "검은 실선: 현재 Polygon",
        "S1~S3: 서울시 후보",
        "O1~O3: OSM 후보",
        "X: parks.csv 대표 좌표",
    ]

    ax.text(
        0.02,
        0.02,
        "\n".join(info_lines),
        transform=ax.transAxes,
        fontsize=9,
        verticalalignment="bottom",
        bbox={
            "boxstyle": "round",
            "alpha": 0.8,
        },
    )

    # ========================================================
    # 저장
    # ========================================================

    filename = f"{park_id:03d}_" f"{sanitize_filename(park_name)}.png"

    output_path = OUTPUT_DIR / filename

    plt.tight_layout()

    fig.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
    )

    plt.close(fig)

    print()
    print(
        "저장:",
        output_path,
    )


# ============================================================
# 완료
# ============================================================

print()
print()
print("=" * 70)
print("시각화 완료")
print("=" * 70)

print(
    "저장 폴더:",
    OUTPUT_DIR,
)
