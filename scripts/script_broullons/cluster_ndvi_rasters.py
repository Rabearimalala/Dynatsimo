"""
Clustering NDVI depuis les GeoTIFF annuels produits par download_ndvi_satellites.py.

Traitement Python equivalent a la logique R:
  1. NDVI moyen mensuel 2000-2011.
  2. Standardisation.
  3. PCA sur echantillon.
  4. CAH Ward en 5 clusters.
  5. Reordonnancement des clusters par NDVI moyen croissant.
  6. Random Forest.
  7. Projection sur 2000-2011 et 2012-derniere annee disponible.

Sorties par satellite:
  AHC_RF_Clusters/LANDSAT/Clusters_2000_2011_REFERENCE.tif
  AHC_RF_Clusters/LANDSAT/Clusters_2012_YYYY_PROJECTED.tif
  AHC_RF_Clusters/LANDSAT/Dendrogramme_CAH_5clusters.png

Installation des dependances manquantes si besoin:
  pip install scikit-learn scipy

Lancement:
  python cluster_ndvi_rasters.py

Pour un seul satellite:
  python cluster_ndvi_rasters.py --satellites landsat
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import rasterio
    from rasterio.windows import Window
except ImportError as exc:
    raise SystemExit(
        "Dependances raster manquantes. Installez-les avec:\n"
        "  pip install numpy pandas rasterio matplotlib"
    ) from exc

try:
    from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
    from sklearn.decomposition import PCA
    from sklearn.ensemble import RandomForestClassifier
except ImportError:
    dendrogram = None
    fcluster = None
    linkage = None
    PCA = None
    RandomForestClassifier = None


INPUT_DIR = Path(__file__).resolve().parents[1] / "ndvi_geotiff"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "public" / "data" / "clusters"

NODATA_IN = -9999.0
NODATA_CLUSTER = 0
RANDOM_SEED = 123

DEFAULT_REFERENCE_START = 2000
DEFAULT_REFERENCE_END = 2011
DEFAULT_PROJECTION_START = 2012


@dataclass(frozen=True)
class SatelliteConfig:
    key: str
    folder: str
    filename_prefix: str


SATELLITES = {
    "landsat": SatelliteConfig("landsat", "LANDSAT", "NDVI_LANDSAT_MONTHLY"),
    "modis": SatelliteConfig("modis", "MODIS", "NDVI_MODIS_MONTHLY"),
    "sentinel2": SatelliteConfig("sentinel2", "SENTINEL2", "NDVI_SENTINEL2_MONTHLY"),
}


def ensure_ml_dependencies() -> None:
    if any(item is None for item in (dendrogram, fcluster, linkage, PCA, RandomForestClassifier)):
        raise SystemExit(
            "Dependances PCA/CAH/RF manquantes. Installez-les avec:\n"
            "  pip install scikit-learn scipy"
        )


@dataclass(frozen=True)
class RasterGroup:
    paths: dict[int, Path]
    profile: dict
    height: int
    width: int
    block_windows: list[tuple[int, Window]]


def find_year_files(input_dir: Path, satellite: SatelliteConfig) -> dict[int, Path]:
    satellite_dir = input_dir / satellite.folder
    files: dict[int, Path] = {}
    for path in satellite_dir.glob(f"{satellite.filename_prefix}_*.tif"):
        try:
            year = int(path.stem.rsplit("_", 1)[1])
        except ValueError:
            continue
        files[year] = path
    return dict(sorted(files.items()))


def open_group(paths: dict[int, Path]) -> RasterGroup:
    if not paths:
        raise FileNotFoundError("Aucun GeoTIFF trouve pour ce satellite.")

    first_path = next(iter(paths.values()))
    with rasterio.open(first_path) as src:
        if src.count < 12:
            raise ValueError(f"{first_path} doit contenir au moins 12 bandes mensuelles.")
        profile = src.profile.copy()
        height = src.height
        width = src.width
        transform = src.transform
        crs = src.crs
        block_windows = list(src.block_windows(1))

    for path in paths.values():
        with rasterio.open(path) as src:
            if src.height != height or src.width != width:
                raise ValueError(f"Dimensions incompatibles: {path}")
            if src.transform != transform or src.crs != crs:
                raise ValueError(f"Projection/grille incompatible: {path}")
            if src.count < 12:
                raise ValueError(f"{path} doit contenir au moins 12 bandes mensuelles.")

    return RasterGroup(paths, profile, height, width, block_windows)


def selected_year_paths(group: RasterGroup, years: Iterable[int]) -> dict[int, Path]:
    return {year: group.paths[year] for year in years if year in group.paths}


def select_year_range(
    group: RasterGroup,
    start_year: int,
    end_year: int | None,
) -> dict[int, Path]:
    if not group.paths:
        return {}
    available_end = max(group.paths)
    final_year = available_end if end_year is None else min(end_year, available_end)
    if final_year < start_year:
        return {}
    return selected_year_paths(group, range(start_year, final_year + 1))


def period_label(paths: dict[int, Path]) -> str:
    return f"{min(paths)}_{max(paths)}"


def read_period_mean(paths: dict[int, Path], window: Window) -> tuple[np.ndarray, np.ndarray]:
    rows = int(window.height)
    cols = int(window.width)
    sums = np.zeros((12, rows, cols), dtype=np.float64)
    counts = np.zeros((12, rows, cols), dtype=np.uint16)

    for path in paths.values():
        with rasterio.open(path) as src:
            data = src.read(indexes=list(range(1, 13)), window=window, masked=True)
            data = data.astype(np.float64).filled(np.nan)
            data[data <= NODATA_IN + 1] = np.nan
            valid = np.isfinite(data)
            sums += np.nan_to_num(data, nan=0.0)
            counts += valid

    means = np.full((12, rows, cols), np.nan, dtype=np.float32)
    np.divide(sums, counts, out=means, where=counts > 0)
    valid_pixels = np.all(counts > 0, axis=0) & np.all(np.isfinite(means), axis=0)
    return means, valid_pixels


def iter_pixel_profiles(
    group: RasterGroup,
    paths: dict[int, Path],
) -> Iterable[tuple[Window, np.ndarray, np.ndarray]]:
    for _, window in group.block_windows:
        means, valid_pixels = read_period_mean(paths, window)
        profiles = np.moveaxis(means, 0, -1).reshape(-1, 12)
        valid_flat = valid_pixels.reshape(-1)
        yield window, profiles, valid_flat


def compute_scaler(group: RasterGroup, paths: dict[int, Path]) -> tuple[np.ndarray, np.ndarray]:
    sums = np.zeros(12, dtype=np.float64)
    sums_sq = np.zeros(12, dtype=np.float64)
    n = 0

    for _, profiles, valid in iter_pixel_profiles(group, paths):
        values = profiles[valid]
        if values.size == 0:
            continue
        sums += values.sum(axis=0)
        sums_sq += np.square(values).sum(axis=0)
        n += values.shape[0]

    if n == 0:
        raise ValueError("Aucun pixel valide pour calculer la standardisation.")

    mean = sums / n
    variance = np.maximum((sums_sq / n) - np.square(mean), 1e-12)
    std = np.sqrt(variance)
    return mean.astype(np.float32), std.astype(np.float32)


def standardize(values: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return ((values - mean) / std).astype(np.float32)


def sample_profiles(
    group: RasterGroup,
    paths: dict[int, Path],
    mean: np.ndarray,
    std: np.ndarray,
    sample_size: int,
    seed: int,
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    reservoir: list[np.ndarray] = []
    seen = 0

    for _, profiles, valid in iter_pixel_profiles(group, paths):
        values = profiles[valid]
        if values.size == 0:
            continue
        values = standardize(values, mean, std)

        for row in values:
            seen += 1
            if len(reservoir) < sample_size:
                reservoir.append(row.copy())
            else:
                j = rng.integers(0, seen)
                if j < sample_size:
                    reservoir[j] = row.copy()

    if not reservoir:
        raise ValueError("Aucun pixel valide pour l'echantillon.")
    return np.vstack(reservoir).astype(np.float32)


def reorder_clusters_by_ndvi(labels: np.ndarray, sample: np.ndarray) -> np.ndarray:
    raw_clusters = np.unique(labels)
    means = {cluster: sample[labels == cluster].mean() for cluster in raw_clusters}
    ordered = sorted(raw_clusters, key=lambda cluster: means[cluster])
    mapping = {cluster: rank + 1 for rank, cluster in enumerate(ordered)}
    return np.array([mapping[label] for label in labels], dtype=np.uint8)


def train_model(
    sample: np.ndarray,
    n_components: int,
    n_clusters: int,
    n_trees: int,
    seed: int,
) -> tuple[Any, np.ndarray]:
    ensure_ml_dependencies()
    pca = PCA(n_components=n_components, random_state=seed)
    coords = pca.fit_transform(sample)
    z = linkage(coords, method="ward")
    raw_labels = fcluster(z, t=n_clusters, criterion="maxclust")
    ordered_labels = reorder_clusters_by_ndvi(raw_labels, sample)

    model = RandomForestClassifier(
        n_estimators=n_trees,
        max_features=max(1, math.floor(math.sqrt(sample.shape[1]))),
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(sample, ordered_labels)
    return model, z


def write_cluster_raster(
    group: RasterGroup,
    paths: dict[int, Path],
    output_file: Path,
    model: Any,
    mean: np.ndarray,
    std: np.ndarray,
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    profile = group.profile.copy()
    profile.update(count=1, dtype="uint8", nodata=NODATA_CLUSTER, compress="lzw")

    with rasterio.open(output_file, "w", **profile) as dst:
        for window, profiles, valid in iter_pixel_profiles(group, paths):
            rows = int(window.height)
            cols = int(window.width)
            out = np.full(rows * cols, NODATA_CLUSTER, dtype=np.uint8)
            if np.any(valid):
                values = standardize(profiles[valid], mean, std)
                out[valid] = model.predict(values).astype(np.uint8)
            dst.write(out.reshape(rows, cols), 1, window=window)


def export_csv_points(
    group: RasterGroup,
    cluster_file: Path,
    output_csv: Path,
) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    parts = []
    pixel_id = 1
    with rasterio.open(cluster_file) as src:
        for _, window in group.block_windows:
            data = src.read(1, window=window)
            valid = data != NODATA_CLUSTER
            if not np.any(valid):
                continue
            rows, cols = np.where(valid)
            absolute_rows = rows + int(window.row_off)
            absolute_cols = cols + int(window.col_off)
            xs, ys = rasterio.transform.xy(src.transform, absolute_rows, absolute_cols)
            n = len(rows)
            parts.append(
                pd.DataFrame(
                    {
                        "id": np.arange(pixel_id, pixel_id + n, dtype=np.int64),
                        "longitude": xs,
                        "latitude": ys,
                        "Cluster": data[rows, cols],
                    }
                )
            )
            pixel_id += n

    if parts:
        pd.concat(parts, ignore_index=True).to_csv(output_csv, index=False)


def write_dendrogram(
    z: np.ndarray,
    output_file: Path,
    n_clusters: int,
    reference_label: str,
) -> None:
    ensure_ml_dependencies()
    output_file.parent.mkdir(parents=True, exist_ok=True)
    cluster_colors = ["#2c7fb8", "#fdae61", "#a1d99b", "#31a354", "#00441b"]

    fig, ax = plt.subplots(figsize=(10.67, 6.67), dpi=150)
    dendrogram(z, no_labels=True, color_threshold=0, above_threshold_color="#333333", ax=ax)
    ax.set_title(
        "Dendrogramme CAH - Decoupage en 5 clusters\n"
        f"NDVI moyen mensuel {reference_label.replace('_', '-')}"
    )
    ax.set_xlabel("")
    ax.set_ylabel("Distance Ward")

    handles = [
        plt.Line2D([0], [0], color=cluster_colors[i], lw=2, label=str(i + 1))
        for i in range(n_clusters)
    ]
    ax.legend(handles=handles, loc="upper right", frameon=False)
    fig.tight_layout()
    fig.savefig(output_file)
    plt.close(fig)


def export_transparent_png(tif_path: Path, png_path: Path) -> list[list[float]] | None:
    """
    Lit un fichier GeoTIFF cluster et génère une image PNG transparente.
    Retourne les coordonnées [[latMin, lngMin], [latMax, lngMax]] (bounds Leaflet).
    """
    try:
        from PIL import Image
        with rasterio.open(tif_path) as src:
            data = src.read(1)
            bounds = src.bounds # (left, bottom, right, top)
            # Leaflet s'attend à [[bottom, left], [top, right]]
            latlon_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
            
            # Définition de la palette de couleurs RGBA (Forêt dense, Forêt dégradée, Fourré, Cultures, Sol nu)
            colors = {
                0: (0, 0, 0, 0),         # transparent
                1: (6, 95, 70, 255),     # vert foncé (#065f46)
                2: (16, 185, 129, 255),  # vert moyen (#10b981)
                3: (161, 217, 155, 255), # vert clair (#a1d99b)
                4: (245, 158, 11, 255),  # jaune/orange (#f59e0b)
                5: (180, 83, 9, 255),    # brun (#b45309)
            }
            
            height, width = data.shape
            rgba = np.zeros((height, width, 4), dtype=np.uint8)
            for val, color in colors.items():
                rgba[data == val] = color
                
            img = Image.fromarray(rgba, "RGBA")
            png_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(png_path, "PNG")
            print(f"Export PNG OK -> {png_path}")
            return latlon_bounds
    except Exception as e:
        print(f"Erreur lors de la conversion PNG : {e}")
        return None


def update_metadata_entry(metadata_file: Path, key: str, entry: dict) -> None:
    metadata = {}
    if metadata_file.exists():
        try:
            metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    metadata[key] = entry
    try:
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        print(f"Metadata mise a jour pour {key} dans {metadata_file}")
    except Exception as e:
        print(f"Erreur mise a jour metadata: {e}")


def process_satellite(
    satellite: SatelliteConfig,
    args: argparse.Namespace,
) -> None:
    ensure_ml_dependencies()
    input_dir = Path(args.input_dir).resolve()
    output_root = Path(args.output_dir).resolve()
    files = find_year_files(input_dir, satellite)
    group = open_group(files)

    early_paths = select_year_range(group, args.reference_start, args.reference_end)
    late_paths = select_year_range(group, args.projection_start, args.projection_end)
    if not early_paths:
        raise FileNotFoundError(
            f"{satellite.folder}: aucun raster pour "
            f"{args.reference_start}-{args.reference_end}."
        )
    if not late_paths:
        projection_end = args.projection_end or max(group.paths)
        raise FileNotFoundError(
            f"{satellite.folder}: aucun raster pour "
            f"{args.projection_start}-{projection_end}."
        )

    output_dir = output_root / satellite.folder
    reference_label = period_label(early_paths)
    projection_label = period_label(late_paths)
    print(f"\n=== {satellite.folder} ===")
    print(f"Annees reference: {min(early_paths)}-{max(early_paths)} ({len(early_paths)} fichier(s))")
    print(f"Annees projection: {min(late_paths)}-{max(late_paths)} ({len(late_paths)} fichier(s))")

    print(f"Standardisation {min(early_paths)}-{max(early_paths)}...")
    early_mean, early_std = compute_scaler(group, early_paths)
    print(f"Standardisation {min(late_paths)}-{max(late_paths)}...")
    late_mean, late_std = compute_scaler(group, late_paths)

    print("Echantillonnage PCA + CAH...")
    sample = sample_profiles(
        group,
        early_paths,
        early_mean,
        early_std,
        sample_size=args.sample_size,
        seed=args.seed,
    )

    print(f"Entrainement PCA + CAH + Random Forest sur {sample.shape[0]} pixels...")
    model, linkage_matrix = train_model(
        sample=sample,
        n_components=args.pca_components,
        n_clusters=args.clusters,
        n_trees=args.trees,
        seed=args.seed,
    )

    ref_tif = output_dir / f"Clusters_{reference_label}_REFERENCE.tif"
    proj_tif = output_dir / f"Clusters_{projection_label}_PROJECTED.tif"
    print(f"Projection reference -> {ref_tif}")
    write_cluster_raster(group, early_paths, ref_tif, model, early_mean, early_std)
    print(f"Projection periode recente -> {proj_tif}")
    write_cluster_raster(group, late_paths, proj_tif, model, late_mean, late_std)

    dendro_png = output_dir / "Dendrogramme_CAH_5clusters.png"
    print(f"Dendrogramme -> {dendro_png}")
    write_dendrogram(linkage_matrix, dendro_png, args.clusters, reference_label)

    if args.export_csv:
        print("Export CSV des clusters...")
        export_csv_points(group, ref_tif, output_dir / f"Clusters_{reference_label}_REFERENCE.csv")
        export_csv_points(group, proj_tif, output_dir / f"Clusters_{projection_label}_PROJECTED.csv")

    # Génération des images PNG transparentes colorées et métadonnées pour affichage web
    print("Generation des PNG transparents et mise a jour des metadonnees...")
    ref_png = output_dir / f"Clusters_{reference_label}_REFERENCE.png"
    proj_png = output_dir / f"Clusters_{projection_label}_PROJECTED.png"

    ref_bounds = export_transparent_png(ref_tif, ref_png)
    proj_bounds = export_transparent_png(proj_tif, proj_png)

    metadata_file = output_root / "metadata.json"
    
    if ref_bounds:
        ref_entry = {
            "bounds": ref_bounds,
            "label": reference_label.replace("_", "-"),
            "png": f"/data/clusters/{satellite.folder}/{ref_png.name}"
        }
        update_metadata_entry(metadata_file, f"{satellite.key}_reference", ref_entry)

    if proj_bounds:
        proj_entry = {
            "bounds": proj_bounds,
            "label": projection_label.replace("_", "-"),
            "png": f"/data/clusters/{satellite.folder}/{proj_png.name}"
        }
        update_metadata_entry(metadata_file, f"{satellite.key}_projected", proj_entry)



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PCA + CAH + Random Forest sur les rasters NDVI annuels."
    )
    parser.add_argument("--input-dir", default=str(INPUT_DIR), help="Dossier NDVI_GeoTIFF.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Dossier de sortie.")
    parser.add_argument(
        "--satellites",
        nargs="+",
        choices=["all", *SATELLITES.keys()],
        default=["all"],
        help="Satellites a traiter.",
    )
    parser.add_argument("--clusters", type=int, default=5, help="Nombre de clusters CAH.")
    parser.add_argument("--sample-size", type=int, default=12000, help="Taille echantillon.")
    parser.add_argument("--pca-components", type=int, default=5, help="Composantes PCA.")
    parser.add_argument("--trees", type=int, default=300, help="Nombre d'arbres Random Forest.")
    parser.add_argument("--seed", type=int, default=RANDOM_SEED, help="Graine aleatoire.")
    parser.add_argument(
        "--reference-start",
        type=int,
        default=DEFAULT_REFERENCE_START,
        help="Premiere annee de la periode de reference.",
    )
    parser.add_argument(
        "--reference-end",
        type=int,
        default=DEFAULT_REFERENCE_END,
        help="Derniere annee de la periode de reference.",
    )
    parser.add_argument(
        "--projection-start",
        type=int,
        default=DEFAULT_PROJECTION_START,
        help="Premiere annee de la periode a projeter.",
    )
    parser.add_argument(
        "--projection-end",
        type=int,
        default=None,
        help="Derniere annee a projeter. Par defaut: derniere annee raster disponible.",
    )
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Exporter aussi id/longitude/latitude/Cluster en CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    selected = args.satellites
    if "all" in selected:
        selected = list(SATELLITES.keys())

    for key in selected:
        process_satellite(SATELLITES[key], args)

    print("\nPCA + CAH + RF termines. Rasters de clusters prets.")


if __name__ == "__main__":
    main()
