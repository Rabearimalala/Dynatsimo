from __future__ import annotations

import os
os.environ.pop("PROJ_LIB", None)
os.environ.pop("PROJ_DATA", None)
os.environ.pop("GDAL_DATA", None)

import argparse
import json
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

try:
    import ee
except ImportError as exc:
    raise SystemExit(
        "Module Earth Engine manquant. Installez-le avec:\n"
        "  pip install earthengine-api"
    ) from exc

try:
    import geemap
except ImportError:
    geemap = None

AOI_SHP = Path(r"C:\Users\Hanitriniala_RH\Desktop\Regions 3\3_region.shp")
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "ndvi_geotiff"
DEFAULT_EE_PROJECT = "eehanitriniala"

CRS = "EPSG:4326"
NODATA = -9999


@dataclass(frozen=True)
class SatelliteConfig:
    name: str
    folder: str
    filename_prefix: str
    start_year: int
    scale: int
    collection_builder: Callable[[ee.Geometry], ee.ImageCollection]
    yearly_image_builder: Callable[[ee.ImageCollection, int], ee.Image]
    monthly_image_builder: Callable[[ee.ImageCollection, int, int], ee.Image]


def get_project(project: str | None = None) -> str | None:
    project = (
        project
        or os.getenv("EE_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("CLOUDSDK_CORE_PROJECT")
        or DEFAULT_EE_PROJECT
    )
    return project.strip() if project and project.strip() else None


def initialize_with_project(project: str | None) -> None:
    if project:
        ee.Initialize(project=project)
    else:
        ee.Initialize()


def ask_project_id() -> str:
    print(
        "\nEarth Engine demande un projet Google Cloud / Earth Engine.\n"
        "Exemple: mon-projet-gee-123456\n"
        "Vous pouvez aussi le passer directement avec:\n"
        "  python download_ndvi_satellites.py --project VOTRE_PROJECT_ID\n"
    )
    project = input("Entrez votre Project ID Earth Engine / Google Cloud: ").strip()
    if not project:
        raise SystemExit("Projet obligatoire. Relancez avec --project VOTRE_PROJECT_ID.")
    return project


def init_earth_engine(project: str | None = None) -> None:
    """Initialise Earth Engine; lance l'authentification si necessaire."""
    project = get_project(project)
    try:
        initialize_with_project(project)
    except Exception as exc:
        if "no project found" in str(exc).lower():
            initialize_with_project(ask_project_id())
            return

        ee.Authenticate()
        try:
            initialize_with_project(project)
        except Exception as second_exc:
            if "no project found" in str(second_exc).lower():
                initialize_with_project(ask_project_id())
                return
            raise


def load_aoi(shapefile: Path) -> ee.FeatureCollection:
    if not shapefile.exists():
        raise FileNotFoundError(f"Shapefile introuvable: {shapefile}")

    required = [".shp", ".shx", ".dbf", ".prj"]
    missing = [suffix for suffix in required if not shapefile.with_suffix(suffix).exists()]
    if missing:
        raise FileNotFoundError(
            "Fichiers shapefile manquants: "
            + ", ".join(str(shapefile.with_suffix(suffix)) for suffix in missing)
        )

    if geemap is not None:
        try:
            ee_aoi = geemap.shp_to_ee(str(shapefile))
            if ee_aoi is not None:
                return ee_aoi
            print("Conversion geemap echouee; tentative avec geopandas.")
        except Exception as exc:
            print(f"Conversion geemap echouee ({exc}); tentative avec geopandas.")

    try:
        import geopandas as gpd
    except ImportError as exc:
        raise SystemExit(
            "geemap ou geopandas est necessaire pour lire le shapefile.\n"
            "Installez geemap avec: pip install geemap"
        ) from exc

    gdf = gpd.read_file(shapefile)
    if gdf.empty:
        raise ValueError(f"Le shapefile ne contient aucune geometrie: {shapefile}")
    if gdf.crs is None:
        raise ValueError("Le shapefile n'a pas de projection (.prj/CRS).")
    gdf = gdf.to_crs("EPSG:4326")
    if hasattr(gdf.geometry, "make_valid"):
        gdf["geometry"] = gdf.geometry.make_valid()
    else:
        gdf["geometry"] = gdf.geometry.buffer(0)
    gdf = gdf[~gdf.geometry.is_empty & gdf.geometry.notna()]
    if gdf.empty:
        raise ValueError("Toutes les geometries du shapefile sont vides ou invalides.")
    if hasattr(gdf.geometry, "union_all"):
        geometry = gdf.geometry.union_all()
    else:
        geometry = gdf.geometry.unary_union
    return ee.FeatureCollection([ee.Feature(ee.Geometry(geometry.__geo_interface__))])


def _scale_l2(img: ee.Image) -> ee.Image:
    scaled = img.select("SR_B.*").multiply(0.0000275).add(-0.2)
    return img.addBands(scaled, None, True)


def _ndvi_from_bands(red_band: str, nir_band: str) -> Callable[[ee.Image], ee.Image]:
    def _to_ndvi(img: ee.Image) -> ee.Image:
        img = _scale_l2(img)
        ndvi = img.normalizedDifference([nir_band, red_band])
        return ndvi.rename("NDVI").copyProperties(img, ["system:time_start"])

    return _to_ndvi


def build_landsat_collection(aoi: ee.Geometry) -> ee.ImageCollection:
    # Landsat 5/7: rouge = SR_B3, PIR = SR_B4. Landsat 8/9: rouge = SR_B4, PIR = SR_B5.
    # IMPORTANT: on separe les deux familles de capteurs AVANT de calculer le NDVI,
    # au lieu d'utiliser ee.Algorithms.If(...) image par image. Le If() forcait Earth
    # Engine a construire les DEUX branches pour chacune des ~150 images de la
    # collection, ce qui gonflait enormement le graphe de calcul et declenchait
    # "User memory limit exceeded" lors des telechargements locaux.
    l57 = (
        ee.ImageCollection("LANDSAT/LT05/C02/T1_L2")
        .merge(ee.ImageCollection("LANDSAT/LE07/C02/T1_L2"))
        .filterBounds(aoi)
        .filter(ee.Filter.lt("CLOUD_COVER", 40))
        .map(_ndvi_from_bands("SR_B3", "SR_B4"))
    )
    l89 = (
        ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
        .merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"))
        .filterBounds(aoi)
        .filter(ee.Filter.lt("CLOUD_COVER", 40))
        .map(_ndvi_from_bands("SR_B4", "SR_B5"))
    )
    return l57.merge(l89)


def build_modis_collection(aoi: ee.Geometry) -> ee.ImageCollection:
    return (
        ee.ImageCollection("MODIS/061/MOD13Q1")
        .filterBounds(aoi)
        .select("NDVI")
    )


def build_sentinel2_collection(aoi: ee.Geometry) -> ee.ImageCollection:
    return (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(aoi)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
        .select(["B4", "B8"])
    )


def monthly_stack(
    collection: ee.ImageCollection,
    year: int,
    monthly_reducer: Callable[[ee.ImageCollection], ee.Image],
) -> ee.Image:
    monthly_images = []

    for month in range(1, 13):
        start = ee.Date.fromYMD(year, month, 1)
        end = start.advance(1, "month")
        month_collection = collection.filterDate(start, end)
        band_name = f"{year}_{month:02d}"

        monthly = ee.Image(
            ee.Algorithms.If(
                month_collection.size().gt(0),
                monthly_reducer(month_collection).rename(band_name),
                ee.Image.constant(NODATA).rename(band_name),
            )
        )
        monthly_images.append(monthly.toFloat())

    return ee.Image.cat(monthly_images).toFloat()


def monthly_image(
    collection: ee.ImageCollection,
    year: int,
    month: int,
    monthly_reducer: Callable[[ee.ImageCollection], ee.Image],
) -> ee.Image:
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, "month")
    month_collection = collection.filterDate(start, end)
    band_name = f"{year}_{month:02d}"
    image = ee.Image(
        ee.Algorithms.If(
            month_collection.size().gt(0),
            monthly_reducer(month_collection).rename(band_name),
            ee.Image.constant(NODATA).rename(band_name),
        )
    )
    return image.toFloat()


def landsat_yearly_image(collection: ee.ImageCollection, year: int) -> ee.Image:
    return monthly_stack(collection, year, lambda monthly: monthly.mean())


def landsat_monthly_image(collection: ee.ImageCollection, year: int, month: int) -> ee.Image:
    return monthly_image(collection, year, month, lambda monthly: monthly.mean())


def modis_yearly_image(collection: ee.ImageCollection, year: int) -> ee.Image:
    return monthly_stack(collection, year, lambda monthly: monthly.mean().multiply(0.0001))


def modis_monthly_image(collection: ee.ImageCollection, year: int, month: int) -> ee.Image:
    return monthly_image(collection, year, month, lambda monthly: monthly.mean().multiply(0.0001))


def sentinel2_yearly_image(collection: ee.ImageCollection, year: int) -> ee.Image:
    return monthly_stack(
        collection,
        year,
        lambda monthly: monthly.median().normalizedDifference(["B8", "B4"]),
    )


def sentinel2_monthly_image(collection: ee.ImageCollection, year: int, month: int) -> ee.Image:
    return monthly_image(
        collection,
        year,
        month,
        lambda monthly: monthly.median().normalizedDifference(["B8", "B4"]),
    )


SATELLITES = {
    "landsat": SatelliteConfig(
        name="LANDSAT",
        folder="LANDSAT",
        filename_prefix="NDVI_LANDSAT_MONTHLY",
        start_year=2000,
        scale=30,
        collection_builder=build_landsat_collection,
        yearly_image_builder=landsat_yearly_image,
        monthly_image_builder=landsat_monthly_image,
    ),
    "modis": SatelliteConfig(
        name="MODIS",
        folder="MODIS",
        filename_prefix="NDVI_MODIS_MONTHLY",
        start_year=2000,
        scale=250,
        collection_builder=build_modis_collection,
        yearly_image_builder=modis_yearly_image,
        monthly_image_builder=modis_monthly_image,
    ),
    "sentinel2": SatelliteConfig(
        name="SENTINEL2",
        folder="SENTINEL2",
        filename_prefix="NDVI_SENTINEL2_MONTHLY",
        start_year=2015,
        scale=10,
        collection_builder=build_sentinel2_collection,
        yearly_image_builder=sentinel2_yearly_image,
        monthly_image_builder=sentinel2_monthly_image,
    ),
}


def load_state(state_file: Path) -> dict[str, int]:
    if not state_file.exists():
        return {}
    return json.loads(state_file.read_text(encoding="utf-8"))


def save_state(state_file: Path, state: dict[str, int]) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")


def annual_count(collection: ee.ImageCollection, year: int) -> int:
    start = ee.Date.fromYMD(year, 1, 1)
    end = start.advance(1, "year")
    return int(collection.filterDate(start, end).size().getInfo())


def monthly_count(collection: ee.ImageCollection, year: int, month: int) -> int:
    start = ee.Date.fromYMD(year, month, 1)
    end = start.advance(1, "month")
    return int(collection.filterDate(start, end).size().getInfo())


def should_download(
    output_file: Path,
    state: dict[str, int],
    state_key: str,
    image_count: int,
    year: int,
    current_year: int,
    overwrite: bool,
    refresh_current_year: bool,
) -> bool:
    if overwrite:
        return True
    if not output_file.exists():
        return True
    if refresh_current_year and year == current_year:
        return state.get(state_key) != image_count
    return False


def export_or_download_image(
    satellite: SatelliteConfig,
    aoi: ee.FeatureCollection,
    image: ee.Image,
    output_file: Path,
    export_mode: str,
    drive_folder: str,
    description: str,
    file_name_prefix: str,
) -> None:
    image = image.clip(aoi.geometry()).unmask(NODATA).toFloat()

    if export_mode == "drive":
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder=drive_folder,
            fileNamePrefix=file_name_prefix,
            region=aoi.geometry(),
            scale=satellite.scale,
            crs=CRS,
            maxPixels=1e13,
            fileFormat="GeoTIFF",
        )
        task.start()
        print(f"{description}: export Google Drive lance -> dossier {drive_folder}")
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if geemap is not None:
        geemap.download_ee_image(
            image=image,
            filename=str(output_file),
            region=aoi.geometry(),
            scale=satellite.scale,
            crs=CRS,
            dtype="float32",
            overwrite=True,
            num_threads=4,
            unmask_value=NODATA,
        )
        return

    try:
        import requests
    except ImportError as exc:
        raise SystemExit(
            "requests est necessaire pour le telechargement local sans geemap.\n"
            "Installez geemap avec: pip install geemap"
        ) from exc

    params = {
        "name": output_file.stem,
        "scale": satellite.scale,
        "crs": CRS,
        "region": aoi.geometry(),
        "filePerBand": False,
        "format": "GEO_TIFF",
    }
    url = image.getDownloadURL(params)
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()
        with output_file.open("wb") as file_obj:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    file_obj.write(chunk)


def merge_monthly_bands_to_geotiff(
    monthly_files: list[tuple[str, Path]],
    output_file: Path,
) -> None:
    """Empile plusieurs GeoTIFF mono-bande (un par mois) en un seul GeoTIFF
    multi-bandes, sans jamais demander a Earth Engine de calculer les 12 mois
    en une seule requete (c'est ce qui provoquait "User memory limit exceeded")."""
    try:
        import rasterio
    except ImportError as exc:
        raise SystemExit(
            "rasterio est necessaire pour assembler les bandes mensuelles en local.\n"
            "Installez-le avec: pip install rasterio"
        ) from exc

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(monthly_files[0][1]) as src0:
        profile = src0.profile

    profile.update(count=len(monthly_files), dtype="float32", nodata=NODATA)

    with rasterio.open(output_file, "w", **profile) as dst:
        for index, (band_name, file_path) in enumerate(monthly_files, start=1):
            with rasterio.open(file_path) as src:
                dst.write(src.read(1).astype("float32"), index)
            dst.set_band_description(index, band_name)


def download_year_local(
    satellite: SatelliteConfig,
    collection: ee.ImageCollection,
    aoi: ee.FeatureCollection,
    year: int,
    output_file: Path,
) -> None:
    """Telecharge l'annee en 12 requetes mensuelles legeres (une bande chacune)
    puis les assemble localement, au lieu d'une seule requete lourde a 12 bandes.
    Cela evite de depasser la limite de memoire interactive d'Earth Engine."""
    with tempfile.TemporaryDirectory(prefix=f"ndvi_{satellite.folder}_{year}_") as tmp_dir:
        tmp_path = Path(tmp_dir)
        monthly_entries: list[tuple[str, Path]] = []

        for month in range(1, 13):
            band_name = f"{year}_{month:02d}"
            tmp_file = tmp_path / f"{satellite.filename_prefix}_{year}_{month:02d}.tif"
            image = satellite.monthly_image_builder(collection, year, month)

            export_or_download_image(
                satellite=satellite,
                aoi=aoi,
                image=image,
                output_file=tmp_file,
                export_mode="local",
                drive_folder="",
                description=f"{satellite.filename_prefix}_{year}_{month:02d}",
                file_name_prefix=f"{satellite.filename_prefix}_{year}_{month:02d}",
            )
            monthly_entries.append((band_name, tmp_file))
            print(f"  {satellite.name} {year}-{month:02d}: bande telechargee.")

        merge_monthly_bands_to_geotiff(monthly_entries, output_file)


def download_year(
    satellite: SatelliteConfig,
    collection: ee.ImageCollection,
    aoi: ee.FeatureCollection,
    year: int,
    output_file: Path,
    export_mode: str,
    drive_folder_prefix: str,
) -> None:
    if export_mode == "drive":
        # Le backend d'export batch de Drive gere sans probleme le calcul complet
        # a 12 bandes en une seule tache: pas besoin de le decouper.
        image = satellite.yearly_image_builder(collection, year)
        export_or_download_image(
            satellite=satellite,
            aoi=aoi,
            image=image,
            output_file=output_file,
            export_mode=export_mode,
            drive_folder=f"{drive_folder_prefix}_{satellite.folder}",
            description=f"{satellite.filename_prefix}_{year}",
            file_name_prefix=f"{satellite.filename_prefix}_{year}",
        )
        return

    download_year_local(satellite, collection, aoi, year, output_file)


def download_month(
    satellite: SatelliteConfig,
    collection: ee.ImageCollection,
    aoi: ee.FeatureCollection,
    year: int,
    month: int,
    output_file: Path,
    export_mode: str,
    drive_folder_prefix: str,
) -> None:
    image = satellite.monthly_image_builder(collection, year, month)
    file_name = f"{satellite.filename_prefix}_{year}_{month:02d}"
    export_or_download_image(
        satellite=satellite,
        aoi=aoi,
        image=image,
        output_file=output_file,
        export_mode=export_mode,
        drive_folder=f"{drive_folder_prefix}_{satellite.folder}_{year}",
        description=file_name,
        file_name_prefix=file_name,
    )


def run_once(args: argparse.Namespace, aoi: ee.FeatureCollection) -> None:
    current_year = datetime.now().year
    end_year = args.end_year or current_year
    output_dir = Path(args.output_dir).resolve()
    state_file = output_dir / "download_state.json"
    state = load_state(state_file)

    selected = args.satellites
    if "all" in selected:
        selected = list(SATELLITES.keys())

    for key in selected:
        satellite = SATELLITES[key]
        satellite_dir = output_dir / satellite.folder
        collection = satellite.collection_builder(aoi.geometry())

        first_year = max(satellite.start_year, args.start_year or satellite.start_year)
        last_year = max(first_year, end_year)

        print(f"\n=== {satellite.name}: {first_year}-{last_year} ===")

        for year in range(first_year, last_year + 1):
            if args.temporal_mode == "annual":
                count = annual_count(collection, year)
                if count == 0:
                    print(f"{satellite.name} {year}: aucune image, ignore.")
                    continue

                output_file = satellite_dir / f"{satellite.filename_prefix}_{year}.tif"
                state_key = f"{satellite.name}_{year}"

                if not should_download(
                    output_file=output_file,
                    state=state,
                    state_key=state_key,
                    image_count=count,
                    year=year,
                    current_year=current_year,
                    overwrite=args.overwrite,
                    refresh_current_year=args.refresh_current_year,
                ):
                    print(f"{satellite.name} {year}: deja telecharge.")
                    continue

                action = "export" if args.export_mode == "drive" else "telechargement"
                print(f"{satellite.name} {year}: {action} de {count} image(s) source...")
                try:
                    download_year(
                        satellite,
                        collection,
                        aoi,
                        year,
                        output_file,
                        args.export_mode,
                        args.drive_folder_prefix,
                    )
                except ee.ee_exception.EEException as exc:
                    if "memory limit" in str(exc).lower():
                        print(
                            f"{satellite.name} {year}: ECHEC - limite de memoire Earth Engine "
                            "depassee. Reessayez avec --temporal-mode monthly ou "
                            "--export-mode drive pour cette annee."
                        )
                        continue
                    raise
                state[state_key] = count
                save_state(state_file, state)
                if args.export_mode == "local":
                    print(f"{satellite.name} {year}: OK -> {output_file}")
                continue

            for month in range(1, 13):
                count = monthly_count(collection, year, month)
                if count == 0:
                    print(f"{satellite.name} {year}-{month:02d}: aucune image, ignore.")
                    continue

                output_file = (
                    satellite_dir
                    / f"{year}"
                    / f"{satellite.filename_prefix}_{year}_{month:02d}.tif"
                )
                state_key = f"{satellite.name}_monthly_{year}_{month:02d}"

                if not should_download(
                    output_file=output_file,
                    state=state,
                    state_key=state_key,
                    image_count=count,
                    year=year,
                    current_year=current_year,
                    overwrite=args.overwrite,
                    refresh_current_year=args.refresh_current_year,
                ):
                    print(f"{satellite.name} {year}-{month:02d}: deja telecharge.")
                    continue

                action = "export" if args.export_mode == "drive" else "telechargement"
                print(
                    f"{satellite.name} {year}-{month:02d}: "
                    f"{action} de {count} image(s) source..."
                )
                try:
                    download_month(
                        satellite,
                        collection,
                        aoi,
                        year,
                        month,
                        output_file,
                        args.export_mode,
                        args.drive_folder_prefix,
                    )
                except ee.ee_exception.EEException as exc:
                    if "memory limit" in str(exc).lower():
                        print(
                            f"{satellite.name} {year}-{month:02d}: ECHEC - limite de memoire "
                            "Earth Engine depassee. Reessayez avec --export-mode drive pour "
                            "cette periode."
                        )
                        continue
                    raise
                state[state_key] = count
                save_state(state_file, state)
                if args.export_mode == "local":
                    print(f"{satellite.name} {year}-{month:02d}: OK -> {output_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Telecharger des GeoTIFF NDVI Landsat, MODIS et Sentinel-2."
    )
    parser.add_argument(
        "--aoi",
        default=str(AOI_SHP),
        help="Chemin du shapefile de la zone d'etude.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Dossier racine des GeoTIFF de sortie.",
    )
    parser.add_argument(
        "--satellites",
        nargs="+",
        choices=["all", *SATELLITES.keys()],
        default=["all"],
        help="Satellites a traiter.",
    )
    parser.add_argument("--start-year", type=int, default=None, help="Annee de debut globale.")
    parser.add_argument(
        "--end-year",
        type=int,
        default=None,
        help="Annee de fin. Par defaut: annee courante.",
    )
    parser.add_argument(
        "--project",
        default=None,
        help="ID du projet Google Cloud Earth Engine si votre compte l'exige.",
    )
    parser.add_argument(
        "--export-mode",
        choices=["local", "drive"],
        default="local",
        help="local telecharge des GeoTIFF sur ce PC; drive lance des exports Google Drive.",
    )
    parser.add_argument(
        "--temporal-mode",
        choices=["annual", "monthly"],
        default="annual",
        help=(
            "annual cree 1 GeoTIFF par satellite/annee avec 12 bandes; "
            "monthly cree 1 GeoTIFF par satellite/annee/mois."
        ),
    )
    parser.add_argument(
        "--drive-folder-prefix",
        default="NDVI_GeoTIFF",
        help="Prefixe des dossiers Google Drive en mode --export-mode drive.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Retelecharger meme si le GeoTIFF existe deja.",
    )
    parser.add_argument(
        "--no-refresh-current-year",
        dest="refresh_current_year",
        action="store_false",
        help="Ne pas rafraichir l'annee courante si de nouvelles images apparaissent.",
    )
    parser.set_defaults(refresh_current_year=True)
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Mode surveillance: relance la verification en boucle.",
    )
    parser.add_argument(
        "--check-every-minutes",
        type=int,
        default=360,
        help="Intervalle de verification en mode --watch.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_earth_engine(args.project)

    aoi_path = Path(args.aoi)
    aoi = load_aoi(aoi_path)
    print(f"Zone d'etude: {aoi_path}")
    print(f"Dossier de sortie: {Path(args.output_dir).resolve()}")
    if geemap is None and args.export_mode == "local":
        print(
            "Info: geemap n'est pas installe. Le script utilisera le telechargement "
            "direct Earth Engine, qui peut etre limite pour les tres gros GeoTIFF."
        )

    while True:
        run_once(args, aoi)
        if not args.watch:
            break

        wait_seconds = max(1, args.check_every_minutes) * 60
        print(f"\nSurveillance active. Nouvelle verification dans {args.check_every_minutes} min.")
        time.sleep(wait_seconds)


if __name__ == "__main__":
    main()
