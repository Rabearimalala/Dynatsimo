import os
import time
import shutil
import requests

import ee
import geopandas as gpd
import rasterio
import numpy as np

from rasterio.merge import merge
from rasterio.mask import mask
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling
)

from shapely.geometry import box, mapping


# ============================================================
# 1. PARAMÈTRES
# ============================================================

START_YEAR = 2015

# Projet Google Earth Engine
EE_PROJECT = "eehanitriniala"

# ------------------------------------------------------------
# SHAPEFILE AOI
# ------------------------------------------------------------

AOI_SHP = (
    r"C:\Users\Hanitriniala_RH"
    r"\Desktop\Regions 3"
    r"\3_region.shp"
)

# ------------------------------------------------------------
# DOSSIER FINAL
# ------------------------------------------------------------

OUTPUT_DIR = (
    r"C:\Users\Hanitriniala_RH"
    r"\Documents\Projet_test"
    r"\dynatsimo-react"
    r"\NDVI_SENTINEL"
)

# ------------------------------------------------------------
# DOSSIER TEMPORAIRE
# ------------------------------------------------------------

TEMP_DIR = os.path.join(
    OUTPUT_DIR,
    "_temp_tiles"
)

# ------------------------------------------------------------
# RÉSOLUTION
# ------------------------------------------------------------

SCALE = 10

# Projection utilisée pour télécharger les tuiles
DOWNLOAD_CRS = "EPSG:32738"

# Projection finale
FINAL_CRS = "EPSG:4326"

# Taille des tuiles
TILE_SIZE_METERS = 20000

# ------------------------------------------------------------
# TÉLÉCHARGEMENT
# ------------------------------------------------------------

MAX_RETRIES = 5

DOWNLOAD_TIMEOUT = 1800

DOWNLOAD_DELAY = 2

# Délai entre les requêtes Earth Engine
EE_DELAY = 1


# ============================================================
# 2. INITIALISATION EARTH ENGINE
# ============================================================

print("=" * 70)
print("INITIALISATION GOOGLE EARTH ENGINE")
print("=" * 70)

try:

    ee.Initialize(
        project=EE_PROJECT
    )

    print("✓ Earth Engine initialisé avec succès.")
    print(f"✓ Projet : {EE_PROJECT}")

except Exception as e:

    print("✗ Impossible d'initialiser Earth Engine.")
    print(f"Erreur : {e}")
    print()
    print("Essaie :")
    print("earthengine authenticate")
    raise


# ============================================================
# 3. CRÉATION DES DOSSIERS
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)

print()
print("Dossier final :")
print(OUTPUT_DIR)

print()
print("Dossier temporaire :")
print(TEMP_DIR)


# ============================================================
# 4. CHARGEMENT DE L'AOI
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT DE L'AOI")
print("=" * 70)

if not os.path.exists(AOI_SHP):

    raise FileNotFoundError(
        f"Shapefile introuvable :\n{AOI_SHP}"
    )


aoi_gdf = gpd.read_file(
    AOI_SHP
)

print("✓ Shapefile chargé.")
print(f"  Géométries : {len(aoi_gdf)}")
print(f"  CRS : {aoi_gdf.crs}")


# ============================================================
# 5. NETTOYAGE DES GÉOMÉTRIES
# ============================================================

print()
print("Vérification des géométries...")

aoi_gdf = aoi_gdf[
    aoi_gdf.geometry.notna()
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Aucune géométrie valide dans le shapefile."
    )


try:

    aoi_gdf["geometry"] = (
        aoi_gdf.geometry.make_valid()
    )

except Exception:

    aoi_gdf["geometry"] = (
        aoi_gdf.geometry.buffer(0)
    )


aoi_gdf = aoi_gdf[
    ~aoi_gdf.geometry.is_empty
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Toutes les géométries sont vides."
    )


print("✓ Géométries vérifiées.")


# ============================================================
# 6. AOI EN UTM
# ============================================================

print()
print(
    f"Conversion de l'AOI vers {DOWNLOAD_CRS}..."
)

aoi_utm = aoi_gdf.to_crs(
    DOWNLOAD_CRS
)


print(
    f"✓ AOI convertie vers {DOWNLOAD_CRS}."
)


try:

    aoi_union = (
        aoi_utm.geometry.union_all()
    )

except AttributeError:

    aoi_union = (
        aoi_utm.geometry.unary_union
    )


if aoi_union.is_empty:

    raise ValueError(
        "La géométrie globale de l'AOI est vide."
    )


print("✓ AOI globale créée.")


# ============================================================
# 7. AOI POUR EARTH ENGINE
# ============================================================

aoi_wgs84 = aoi_gdf.to_crs(
    "EPSG:4326"
)


try:

    aoi_union_wgs84 = (
        aoi_wgs84.geometry.union_all()
    )

except AttributeError:

    aoi_union_wgs84 = (
        aoi_wgs84.geometry.unary_union
    )


aoi_ee = ee.Geometry(
    mapping(
        aoi_union_wgs84
    )
)


print("✓ AOI prête pour Earth Engine.")


# ============================================================
# 8. COLLECTION SENTINEL-2
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT SENTINEL-2")
print("=" * 70)


sentinel_raw = (
    ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )
    .filterBounds(
        aoi_ee
    )
    .filter(
        ee.Filter.lt(
            "CLOUDY_PIXEL_PERCENTAGE",
            80
        )
    )
)


print(
    "✓ Collection Sentinel-2 chargée."
)


# ============================================================
# 9. RECHERCHE DE LA DERNIÈRE DONNÉE
# ============================================================

print()
print("=" * 70)
print("RECHERCHE DE LA DERNIÈRE DONNÉE SENTINEL-2")
print("=" * 70)


try:

    last_image = (
        sentinel_raw
        .sort(
            "system:time_start",
            False
        )
        .first()
    )

    last_date = last_image.date()

    LAST_YEAR = (
        last_date
        .get("year")
        .getInfo()
    )

    LAST_MONTH = (
        last_date
        .get("month")
        .getInfo()
    )

    LAST_DAY = (
        last_date
        .get("day")
        .getInfo()
    )

except Exception as e:

    print()
    print("⚠ Impossible de récupérer automatiquement")
    print("la dernière date Sentinel-2.")
    print()
    print(f"Erreur : {e}")
    print()

    print(
        "Le script utilise temporairement l'année actuelle."
    )

    LAST_YEAR = 2026
    LAST_MONTH = 12
    LAST_DAY = 31


print()
print("✓ Dernière période utilisée :")
print(
    f"{LAST_DAY:02d}/"
    f"{LAST_MONTH:02d}/"
    f"{LAST_YEAR}"
)


# ============================================================
# 10. VÉRIFICATION DE LA PÉRIODE
# ============================================================

if START_YEAR > LAST_YEAR:

    raise ValueError(
        "START_YEAR est supérieur à LAST_YEAR."
    )


print()
print(
    f"Période : "
    f"{START_YEAR} → "
    f"{LAST_YEAR}-{LAST_MONTH:02d}"
)


# ============================================================
# 11. MASQUE DES NUAGES
# ============================================================

def mask_sentinel2(image):

    qa = image.select(
        "QA60"
    )

    cloud_bit = 1 << 10

    cirrus_bit = 1 << 11

    qa_mask = (
        qa.bitwiseAnd(
            cloud_bit
        ).eq(0)
        .And(
            qa.bitwiseAnd(
                cirrus_bit
            ).eq(0)
        )
    )

    scl = image.select(
        "SCL"
    )

    scl_mask = (
        scl.neq(3)
        .And(
            scl.neq(8)
        )
        .And(
            scl.neq(9)
        )
        .And(
            scl.neq(10)
        )
        .And(
            scl.neq(11)
        )
    )

    return (
        image
        .updateMask(
            qa_mask.And(
                scl_mask
            )
        )
    )


sentinel = (
    sentinel_raw.map(
        mask_sentinel2
    )
)


# ============================================================
# 12. CALCUL NDVI
# ============================================================

def calculate_monthly_ndvi(
    collection
):

    def calculate_ndvi(
        image
    ):

        ndvi = (
            image
            .normalizedDifference(
                [
                    "B8",
                    "B4"
                ]
            )
            .rename(
                "NDVI"
            )
        )

        return ndvi


    return (
        collection
        .map(
            calculate_ndvi
        )
        .mean()
        .toFloat()
    )


# ============================================================
# 13. CRÉATION DES TUILES
# ============================================================

print()
print("=" * 70)
print("CRÉATION DES TUILES")
print("=" * 70)


minx, miny, maxx, maxy = (
    aoi_union.bounds
)


tiles = []

tile_id = 0

x = minx


while x < maxx:

    y = miny

    while y < maxy:

        tile_polygon = box(
            x,
            y,
            min(
                x + TILE_SIZE_METERS,
                maxx
            ),
            min(
                y + TILE_SIZE_METERS,
                maxy
            )
        )

        intersection = (
            tile_polygon.intersection(
                aoi_union
            )
        )

        if (
            not intersection.is_empty
            and intersection.area > 0
        ):

            tile_id += 1

            tiles.append(
                {
                    "id": tile_id,
                    "geometry": intersection
                }
            )

        y += TILE_SIZE_METERS

    x += TILE_SIZE_METERS


print()
print(
    f"✓ Nombre de tuiles : {len(tiles)}"
)


# ============================================================
# 14. FONCTION DE TÉLÉCHARGEMENT
# ============================================================

def download_file(
    url,
    output_file
):

    # --------------------------------------------------------
    # SI LE FICHIER EXISTE DÉJÀ
    # --------------------------------------------------------

    if (
        os.path.exists(output_file)
        and
        os.path.getsize(output_file) > 0
    ):

        print(
            "        ↪ Tuile déjà téléchargée."
        )

        return True


    temp_file = (
        output_file
        + ".part"
    )


    # --------------------------------------------------------
    # SUPPRIMER UN ANCIEN .PART
    # --------------------------------------------------------

    if os.path.exists(temp_file):

        try:

            os.remove(
                temp_file
            )

        except Exception:

            pass


    # --------------------------------------------------------
    # TENTATIVES
    # --------------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            print(
                f"        Téléchargement "
                f"{attempt}/{MAX_RETRIES}..."
            )


            response = requests.get(
                url,
                stream=True,
                timeout=DOWNLOAD_TIMEOUT
            )


            response.raise_for_status()


            with open(
                temp_file,
                "wb"
            ) as f:

                for chunk in response.iter_content(
                    chunk_size=4 * 1024 * 1024
                ):

                    if chunk:

                        f.write(
                            chunk
                        )


            if (
                os.path.exists(temp_file)
                and
                os.path.getsize(temp_file) > 0
            ):

                os.replace(
                    temp_file,
                    output_file
                )


                size_mb = (
                    os.path.getsize(
                        output_file
                    )
                    / 1024
                    / 1024
                )


                print(
                    f"        ✓ "
                    f"{size_mb:.2f} MB"
                )


                return True


        except Exception as e:

            print(
                f"        ⚠ Erreur : {e}"
            )


            if os.path.exists(
                temp_file
            ):

                try:

                    os.remove(
                        temp_file
                    )

                except Exception:

                    pass


            if attempt < MAX_RETRIES:

                print(
                    "        Nouvelle tentative dans 10 secondes..."
                )

                time.sleep(
                    10
                )


    return False


# ============================================================
# 15. FUSION DES TUILES
# ============================================================

def merge_tiles(
    tile_files,
    output_file
):

    print()
    print(
        "    Fusion des tuiles..."
    )


    src_files = []


    temp_mosaic = (
        output_file
        + ".temp_mosaic.tif"
    )


    temp_final = (
        output_file
        + ".temp_final.tif"
    )


    try:

        # ----------------------------------------------------
        # OUVERTURE DES TUILES
        # ----------------------------------------------------

        for file in tile_files:

            if (
                os.path.exists(file)
                and
                os.path.getsize(file) > 0
            ):

                src_files.append(
                    rasterio.open(file)
                )


        if len(src_files) == 0:

            raise RuntimeError(
                "Aucune tuile disponible."
            )


        # ----------------------------------------------------
        # MOSAÏQUE
        # ----------------------------------------------------

        mosaic, transform = merge(
            src_files
        )


        meta = (
            src_files[0]
            .meta
            .copy()
        )


        meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform,
                "compress": "deflate",
                "predictor": 2,
                "tiled": True
            }
        )


        # ----------------------------------------------------
        # FERMETURE
        # ----------------------------------------------------

        for src in src_files:

            src.close()


        src_files = []


        # ----------------------------------------------------
        # ÉCRITURE MOSAÏQUE
        # ----------------------------------------------------

        with rasterio.open(
            temp_mosaic,
            "w",
            **meta
        ) as dst:

            dst.write(
                mosaic
            )


        # ----------------------------------------------------
        # REPROJECTION
        # ----------------------------------------------------

        print(
            "    Reprojection vers EPSG:4326..."
        )


        with rasterio.open(
            temp_mosaic
        ) as src:

            (
                transform_final,
                width_final,
                height_final
            ) = calculate_default_transform(
                src.crs,
                FINAL_CRS,
                src.width,
                src.height,
                *src.bounds
            )


            final_meta = (
                src.meta
                .copy()
            )


            final_meta.update(
                {
                    "driver": "GTiff",
                    "crs": FINAL_CRS,
                    "transform": transform_final,
                    "width": width_final,
                    "height": height_final,
                    "compress": "deflate",
                    "predictor": 2,
                    "tiled": True
                }
            )


            with rasterio.open(
                temp_final,
                "w",
                **final_meta
            ) as dst:

                for band in range(
                    1,
                    src.count + 1
                ):

                    reproject(
                        source=rasterio.band(
                            src,
                            band
                        ),
                        destination=rasterio.band(
                            dst,
                            band
                        ),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform_final,
                        dst_crs=FINAL_CRS,
                        resampling=Resampling.nearest
                    )


        # ----------------------------------------------------
        # DÉCOUPAGE EXACT AOI
        # ----------------------------------------------------

        print(
            "    Découpage exact sur l'AOI..."
        )


        aoi_shapes = [
            mapping(geom)
            for geom in aoi_wgs84.geometry
        ]


        with rasterio.open(
            temp_final
        ) as src:

            clipped, clipped_transform = mask(
                src,
                aoi_shapes,
                crop=True,
                nodata=-9999
            )


            clipped_meta = (
                src.meta
                .copy()
            )


            clipped_meta.update(
                {
                    "driver": "GTiff",
                    "height": clipped.shape[1],
                    "width": clipped.shape[2],
                    "transform": clipped_transform,
                    "crs": FINAL_CRS,
                    "nodata": -9999,
                    "compress": "deflate",
                    "predictor": 2,
                    "tiled": True
                }
            )


        # ----------------------------------------------------
        # ÉCRITURE FICHIER FINAL
        # ----------------------------------------------------

        with rasterio.open(
            output_file,
            "w",
            **clipped_meta
        ) as dst:

            dst.write(
                clipped
            )


        # ----------------------------------------------------
        # VÉRIFICATION
        # ----------------------------------------------------

        if not (
            os.path.exists(output_file)
            and
            os.path.getsize(output_file) > 0
        ):

            raise RuntimeError(
                "Le fichier final n'a pas été créé."
            )


        print(
            "    ✓ GeoTIFF final créé."
        )


        return True


    finally:

        # ----------------------------------------------------
        # FERMETURE
        # ----------------------------------------------------

        for src in src_files:

            try:

                src.close()

            except Exception:

                pass


        # ----------------------------------------------------
        # SUPPRESSION TEMPORAIRE
        # ----------------------------------------------------

        for temp_file in [
            temp_mosaic,
            temp_final
        ]:

            if os.path.exists(
                temp_file
            ):

                try:

                    os.remove(
                        temp_file
                    )

                except Exception:

                    pass


# ============================================================
# 16. STATISTIQUES
# ============================================================

downloaded_tiles = 0

existing_files = 0

successful_months = 0

failed_months = 0


# ============================================================
# 17. TRAITEMENT DES ANNÉES ET DES MOIS
# ============================================================

print()
print("=" * 70)
print("DÉBUT DU TRAITEMENT")
print("=" * 70)


for year in range(
    START_YEAR,
    LAST_YEAR + 1
):

    if year < LAST_YEAR:

        final_month = 12

    else:

        final_month = LAST_MONTH


    print()
    print("#" * 70)
    print(f"ANNÉE {year}")
    print("#" * 70)


    for month in range(
        1,
        final_month + 1
    ):

        month_str = (
            f"{month:02d}"
        )


        period = (
            f"{year}_{month_str}"
        )


        print()
        print("=" * 70)
        print(
            f"NDVI SENTINEL-2 {period}"
        )
        print("=" * 70)


        # ----------------------------------------------------
        # DOSSIER ANNÉE
        # ----------------------------------------------------

        year_dir = os.path.join(
            OUTPUT_DIR,
            str(year)
        )


        os.makedirs(
            year_dir,
            exist_ok=True
        )


        # ----------------------------------------------------
        # FICHIER FINAL
        # ----------------------------------------------------

        final_file = os.path.join(
            year_dir,
            f"NDVI_SENTINEL_{period}.tif"
        )


        # ----------------------------------------------------
        # REPRISE SI FICHIER FINAL EXISTE
        # ----------------------------------------------------

        if (
            os.path.exists(final_file)
            and
            os.path.getsize(final_file) > 0
        ):

            print(
                "✓ Fichier final déjà présent."
            )

            existing_files += 1

            continue


        # ----------------------------------------------------
        # DATES
        # ----------------------------------------------------

        start_date = ee.Date.fromYMD(
            year,
            month,
            1
        )


        end_date = (
            start_date.advance(
                1,
                "month"
            )
        )


        # ----------------------------------------------------
        # COLLECTION DU MOIS
        # ----------------------------------------------------

        monthly_collection = (
            sentinel
            .filterDate(
                start_date,
                end_date
            )
        )


        # ----------------------------------------------------
        # COMPTER LES IMAGES
        # ----------------------------------------------------

        try:

            image_count = (
                monthly_collection
                .size()
                .getInfo()
            )

        except Exception as e:

            print()
            print(
                "✗ Impossible de contacter "
                "Earth Engine."
            )

            print(
                f"Erreur : {e}"
            )

            print(
                "Le mois sera ignoré."
            )

            failed_months += 1

            continue


        print()
        print(
            f"Images disponibles : "
            f"{image_count}"
        )


        if image_count == 0:

            print(
                "⚠ Aucune image pour ce mois."
            )

            failed_months += 1

            continue


        # ----------------------------------------------------
        # CALCUL NDVI
        # ----------------------------------------------------

        try:

            monthly_ndvi = (
                calculate_monthly_ndvi(
                    monthly_collection
                )
                .clip(
                    aoi_ee
                )
            )

        except Exception as e:

            print(
                f"✗ Erreur calcul NDVI : {e}"
            )

            failed_months += 1

            continue


        # ----------------------------------------------------
        # DOSSIER TEMPORAIRE DU MOIS
        # ----------------------------------------------------

        month_temp_dir = os.path.join(
            TEMP_DIR,
            period
        )


        os.makedirs(
            month_temp_dir,
            exist_ok=True
        )


        tile_files = []


        # ====================================================
        # TRAITEMENT DES TUILES
        # ====================================================

        for tile in tiles:

            tile_id = tile["id"]


            print()
            print("-" * 70)
            print(
                f"Tuile {tile_id}/{len(tiles)}"
            )
            print("-" * 70)


            tile_file = os.path.join(
                month_temp_dir,
                f"tile_{tile_id:03d}.tif"
            )


            # ------------------------------------------------
            # REPRISE
            # ------------------------------------------------

            if (
                os.path.exists(tile_file)
                and
                os.path.getsize(tile_file) > 0
            ):

                print(
                    "↪ Tuile déjà téléchargée."
                )

                tile_files.append(
                    tile_file
                )

                continue


            # ------------------------------------------------
            # GÉOMÉTRIE
            # ------------------------------------------------

            try:

                tile_geometry_wgs84 = (
                    gpd.GeoSeries(
                        [tile["geometry"]],
                        crs=DOWNLOAD_CRS
                    )
                    .to_crs(
                        "EPSG:4326"
                    )
                    .iloc[0]
                )


                tile_ee = ee.Geometry(
                    mapping(
                        tile_geometry_wgs84
                    )
                )


            except Exception as e:

                print(
                    f"✗ Erreur géométrie : {e}"
                )

                continue


            # ------------------------------------------------
            # VÉRIFICATION IMAGE
            # ------------------------------------------------

            try:

                tile_count = (
                    monthly_collection
                    .filterBounds(
                        tile_ee
                    )
                    .size()
                    .getInfo()
                )


            except Exception as e:

                print(
                    f"✗ Erreur vérification : {e}"
                )

                continue


            if tile_count == 0:

                print(
                    "↪ Aucune image dans cette tuile."
                )

                continue


            print(
                f"Images dans la tuile : "
                f"{tile_count}"
            )


            # ------------------------------------------------
            # NDVI TUILE
            # ------------------------------------------------

            tile_ndvi = (
                monthly_ndvi
                .clip(
                    tile_ee
                )
            )


            # ------------------------------------------------
            # URL DE TÉLÉCHARGEMENT
            # ------------------------------------------------

            try:

                print(
                    "Génération de l'URL..."
                )


                url = (
                    tile_ndvi
                    .getDownloadURL(
                        {
                            "name": (
                                f"NDVI_"
                                f"{period}_"
                                f"tile_"
                                f"{tile_id:03d}"
                            ),
                            "scale": SCALE,
                            "crs": DOWNLOAD_CRS,
                            "region": tile_ee,
                            "filePerBand": False,
                            "format": "GEO_TIFF"
                        }
                    )
                )


                print(
                    "✓ URL générée."
                )


            except Exception as e:

                print(
                    f"✗ Erreur génération URL : {e}"
                )

                continue


            # ------------------------------------------------
            # TÉLÉCHARGEMENT
            # ------------------------------------------------

            success = download_file(
                url,
                tile_file
            )


            if success:

                tile_files.append(
                    tile_file
                )

                downloaded_tiles += 1

            else:

                print(
                    "✗ Échec téléchargement."
                )


            time.sleep(
                DOWNLOAD_DELAY
            )


        # ====================================================
        # VÉRIFICATION TUILES
        # ====================================================

        print()
        print(
            f"Tuiles disponibles : "
            f"{len(tile_files)}/{len(tiles)}"
        )


        if len(tile_files) == 0:

            print(
                "✗ Aucune tuile disponible."
            )

            failed_months += 1

            continue


        # ====================================================
        # FUSION
        # ====================================================

        try:

            success_merge = merge_tiles(
                tile_files,
                final_file
            )

        except Exception as e:

            print(
                f"✗ Erreur mosaïque : {e}"
            )

            success_merge = False


        # ====================================================
        # SI SUCCÈS
        # ====================================================

        if success_merge:

            if os.path.exists(
                month_temp_dir
            ):

                try:

                    shutil.rmtree(
                        month_temp_dir
                    )

                    print(
                        "✓ Tuiles temporaires supprimées."
                    )

                except Exception as e:

                    print(
                        "⚠ Impossible de supprimer "
                        f"les tuiles : {e}"
                    )


            successful_months += 1


            print()
            print(
                "✓✓✓ MOIS TERMINÉ ✓✓✓"
            )


            print(
                "Fichier final :"
            )


            print(
                final_file
            )


            size_mb = (
                os.path.getsize(
                    final_file
                )
                / 1024
                / 1024
            )


            print(
                f"Taille : "
                f"{size_mb:.2f} MB"
            )


        else:

            failed_months += 1


            print(
                f"✗ Échec du mois {period}."
            )


            print(
                "Les tuiles sont conservées "
                "pour permettre une reprise."
            )


# ============================================================
# 18. NETTOYAGE DES .PART
# ============================================================

print()
print("=" * 70)
print("NETTOYAGE FINAL")
print("=" * 70)


for root, dirs, files in os.walk(
    TEMP_DIR
):

    for file in files:

        if file.endswith(
            ".part"
        ):

            path = os.path.join(
                root,
                file
            )


            try:

                os.remove(
                    path
                )

            except Exception:

                pass


# ============================================================
# 19. SUPPRESSION DES DOSSIERS VIDES
# ============================================================

for root, dirs, files in os.walk(
    TEMP_DIR,
    topdown=False
):

    if (
        not dirs
        and
        not files
    ):

        try:

            os.rmdir(
                root
            )

        except Exception:

            pass


# ============================================================
# 20. RÉSUMÉ
# ============================================================

print()
print("=" * 70)
print("TRAITEMENT SENTINEL-2 TERMINÉ")
print("=" * 70)

print()

print(
    f"✓ Mois terminés : "
    f"{successful_months}"
)

print(
    f"↪ Mois déjà présents : "
    f"{existing_files}"
)

print(
    f"✗ Mois en échec : "
    f"{failed_months}"
)

print(
    f"✓ Tuiles téléchargées : "
    f"{downloaded_tiles}"
)

print()

print(
    f"Période : "
    f"{START_YEAR} → "
    f"{LAST_YEAR}-{LAST_MONTH:02d}"
)

print()

print(
    "Dossier des résultats :"
)

print(
    OUTPUT_DIR
)

print()

print(
    "Format des résultats :"
)

print(
    "YYYY/NDVI_SENTINEL_YYYY_MM.tif"
)

print()

print(
    "Chaque fichier correspond à :"
)

print(
    "1 mois + 1 mosaïque + toute l'AOI"
)

print()

print("=" * 70)
print("FIN DU PROGRAMME")
print("=" * 70)