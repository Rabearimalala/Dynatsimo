# ============================================================
# DOWNLOAD NDVI LANDSAT MONTHLY
# VERSION AVEC TUILES TEMPORAIRES + MOSAÏQUE AUTOMATIQUE
# ============================================================

import os
import time
import math
import shutil
import requests
import ee
import geopandas as gpd
import rasterio

from rasterio.merge import merge
from rasterio.warp import calculate_default_transform, reproject, Resampling
from shapely.geometry import box


# ============================================================
# 1. PARAMÈTRES
# ============================================================

START_YEAR = 2000

# IMPORTANT :
# Pas de END_YEAR.
# Le script détecte automatiquement la dernière image disponible.


# ============================================================
# PROJET EARTH ENGINE
# ============================================================

EE_PROJECT = "eehanitriniala"


# ============================================================
# SHAPEFILE AOI
# ============================================================

AOI_SHP = (
    r"C:\Users\Hanitriniala_RH"
    r"\Desktop\Regions 3"
    r"\3_region.shp"
)


# ============================================================
# DOSSIER DE SORTIE
# ============================================================

OUTPUT_DIR = (
    r"C:\Users\Hanitriniala_RH"
    r"\Documents\Projet_test"
    r"\dynatsimo-react"
    r"\NDVI_LANDSAT"
)


# ============================================================
# PARAMÈTRES LANDSAT
# ============================================================

# Landsat = 30 mètres
SCALE = 30

# Projection finale
CRS = "EPSG:4326"

# Nombre de tentatives
MAX_RETRIES = 3

# Pause entre téléchargements
DOWNLOAD_PAUSE = 1

# Taille maximale approximative d'un morceau
# On utilise une taille prudente pour éviter
# la limite de 48 MB de getDownloadURL().
#
# 0.10 degré ≈ 11 km
# À 30 m, cela reste raisonnable.
TILE_SIZE_DEG = 0.08

# Compression GeoTIFF finale
COMPRESSION = "lzw"


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
    print(
        f"✓ Projet Earth Engine : "
        f"{EE_PROJECT}"
    )

except Exception as e:

    print()
    print("✗ Impossible d'initialiser Earth Engine.")
    print()
    print(e)
    print()
    print("Si nécessaire :")
    print("earthengine authenticate")
    print()

    raise


# ============================================================
# 3. DOSSIERS
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

TEMP_DIR = os.path.join(
    OUTPUT_DIR,
    "_TEMP_TILES"
)

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)

print()
print("Dossier de sortie :")
print(OUTPUT_DIR)


# ============================================================
# 4. CHARGEMENT AOI
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

print(
    f"  Nombre de géométries : "
    f"{len(aoi_gdf)}"
)

print(
    f"  CRS actuel : "
    f"{aoi_gdf.crs}"
)


# ============================================================
# 5. VÉRIFICATION CRS
# ============================================================

if aoi_gdf.crs is None:

    raise ValueError(
        "Le shapefile ne possède pas de CRS."
    )


# ============================================================
# 6. NETTOYAGE DES GÉOMÉTRIES
# ============================================================

print()
print("Vérification des géométries...")

aoi_gdf = aoi_gdf[
    aoi_gdf.geometry.notna()
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Aucune géométrie valide."
    )


try:

    aoi_gdf["geometry"] = (
        aoi_gdf.geometry.make_valid()
    )

except Exception:

    print(
        "⚠ Impossible d'utiliser make_valid()."
    )


# Supprimer les géométries vides

aoi_gdf = aoi_gdf[
    ~aoi_gdf.geometry.is_empty
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Toutes les géométries sont vides."
    )


print(
    "✓ Géométries vérifiées."
)


# ============================================================
# 7. EPSG 4326
# ============================================================

print()
print(
    "Conversion de l'AOI en EPSG:4326..."
)

aoi_gdf = aoi_gdf.to_crs(
    "EPSG:4326"
)

print(
    "✓ AOI convertie en EPSG:4326."
)


# ============================================================
# 8. UNION
# ============================================================

print()
print(
    "Préparation de la géométrie globale..."
)

try:

    aoi_geometry_shapely = (
        aoi_gdf.geometry.union_all()
    )

except AttributeError:

    aoi_geometry_shapely = (
        aoi_gdf.geometry.unary_union
    )


if aoi_geometry_shapely.is_empty:

    raise ValueError(
        "La géométrie de l'AOI est vide."
    )


print(
    "✓ Géométrie globale créée."
)


# ============================================================
# 9. CONVERSION EARTH ENGINE
# ============================================================

print()
print(
    "Conversion vers Earth Engine..."
)

aoi_geojson = (
    gpd.GeoSeries(
        [aoi_geometry_shapely],
        crs="EPSG:4326"
    ).__geo_interface__
)

aoi = ee.FeatureCollection(
    aoi_geojson
)

aoi_geometry = aoi.geometry()

print(
    "✓ AOI prête pour Earth Engine."
)


# ============================================================
# 10. BOUNDING BOX
# ============================================================

minx, miny, maxx, maxy = (
    aoi_geometry_shapely.bounds
)

print()
print("Emprise AOI :")

print(
    f"  Longitude : {minx:.6f} → {maxx:.6f}"
)

print(
    f"  Latitude  : {miny:.6f} → {maxy:.6f}"
)


# ============================================================
# 11. CRÉATION DES TUILES
# ============================================================

print()
print("=" * 70)
print("CRÉATION DES TUILES DE TÉLÉCHARGEMENT")
print("=" * 70)


def create_tiles():

    tiles = []

    x = minx

    while x < maxx:

        y = miny

        while y < maxy:

            tile = box(
                x,
                y,
                min(
                    x + TILE_SIZE_DEG,
                    maxx
                ),
                min(
                    y + TILE_SIZE_DEG,
                    maxy
                )
            )

            # Ne garder que les tuiles
            # intersectant réellement l'AOI

            if tile.intersects(
                aoi_geometry_shapely
            ):

                tiles.append(tile)

            y += TILE_SIZE_DEG

        x += TILE_SIZE_DEG

    return tiles


tiles = create_tiles()


print()
print(
    f"✓ Nombre de tuiles nécessaires : "
    f"{len(tiles)}"
)


# ============================================================
# 12. CONVERSION TILE → EE
# ============================================================

def shapely_to_ee_geometry(
    geometry
):

    geojson = (
        gpd.GeoSeries(
            [geometry],
            crs="EPSG:4326"
        ).__geo_interface__
    )

    return ee.Geometry(
        geojson["features"][0]["geometry"]
    )


# ============================================================
# 13. COLLECTIONS LANDSAT
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT DES COLLECTIONS LANDSAT")
print("=" * 70)


landsat7 = (
    ee.ImageCollection(
        "LANDSAT/LE07/C02/T1_L2"
    )
    .filterBounds(
        aoi_geometry
    )
)


landsat8 = (
    ee.ImageCollection(
        "LANDSAT/LC08/C02/T1_L2"
    )
    .filterBounds(
        aoi_geometry
    )
)


landsat9 = (
    ee.ImageCollection(
        "LANDSAT/LC09/C02/T1_L2"
    )
    .filterBounds(
        aoi_geometry
    )
)


print("✓ Landsat 7 chargé.")
print("✓ Landsat 8 chargé.")
print("✓ Landsat 9 chargé.")


# ============================================================
# 14. MASQUE CLOUD
# ============================================================

def mask_landsat(
    image
):

    qa = image.select(
        "QA_PIXEL"
    )

    dilated_cloud = 1 << 1
    cloud = 1 << 3
    cloud_shadow = 1 << 4
    snow = 1 << 5

    mask = (
        qa.bitwiseAnd(
            dilated_cloud
        ).eq(0)
        .And(
            qa.bitwiseAnd(
                cloud
            ).eq(0)
        )
        .And(
            qa.bitwiseAnd(
                cloud_shadow
            ).eq(0)
        )
        .And(
            qa.bitwiseAnd(
                snow
            ).eq(0)
        )
    )

    return image.updateMask(
        mask
    )


# ============================================================
# 15. NDVI LANDSAT 7
# ============================================================

def ndvi_landsat7(
    image
):

    image = mask_landsat(
        image
    )

    red = (
        image
        .select("SR_B3")
        .multiply(0.0000275)
        .add(-0.2)
    )

    nir = (
        image
        .select("SR_B4")
        .multiply(0.0000275)
        .add(-0.2)
    )

    ndvi = (
        nir.subtract(red)
        .divide(
            nir.add(red)
        )
        .rename("NDVI")
    )

    return ndvi.copyProperties(
        image,
        ["system:time_start"]
    )


# ============================================================
# 16. NDVI LANDSAT 8
# ============================================================

def ndvi_landsat8(
    image
):

    image = mask_landsat(
        image
    )

    red = (
        image
        .select("SR_B4")
        .multiply(0.0000275)
        .add(-0.2)
    )

    nir = (
        image
        .select("SR_B5")
        .multiply(0.0000275)
        .add(-0.2)
    )

    ndvi = (
        nir.subtract(red)
        .divide(
            nir.add(red)
        )
        .rename("NDVI")
    )

    return ndvi.copyProperties(
        image,
        ["system:time_start"]
    )


# ============================================================
# 17. NDVI LANDSAT 9
# ============================================================

def ndvi_landsat9(
    image
):

    image = mask_landsat(
        image
    )

    red = (
        image
        .select("SR_B4")
        .multiply(0.0000275)
        .add(-0.2)
    )

    nir = (
        image
        .select("SR_B5")
        .multiply(0.0000275)
        .add(-0.2)
    )

    ndvi = (
        nir.subtract(red)
        .divide(
            nir.add(red)
        )
        .rename("NDVI")
    )

    return ndvi.copyProperties(
        image,
        ["system:time_start"]
    )


# ============================================================
# 18. CRÉATION NDVI
# ============================================================

landsat7_ndvi = (
    landsat7
    .map(
        ndvi_landsat7
    )
)

landsat8_ndvi = (
    landsat8
    .map(
        ndvi_landsat8
    )
)

landsat9_ndvi = (
    landsat9
    .map(
        ndvi_landsat9
    )
)


# Fusion

landsat_ndvi = (
    landsat7_ndvi
    .merge(
        landsat8_ndvi
    )
    .merge(
        landsat9_ndvi
    )
    .filterBounds(
        aoi_geometry
    )
)


print()
print(
    "✓ Collections NDVI fusionnées."
)


# ============================================================
# 19. RECHERCHE DERNIÈRE IMAGE
# ============================================================

print()
print("=" * 70)
print("RECHERCHE DE LA DERNIÈRE DONNÉE LANDSAT")
print("=" * 70)


latest_image = (
    landsat_ndvi
    .sort(
        "system:time_start",
        False
    )
    .first()
)


latest_timestamp = (
    latest_image
    .get(
        "system:time_start"
    )
    .getInfo()
)


if latest_timestamp is None:

    raise ValueError(
        "Aucune image Landsat disponible."
    )


latest_date = (
    ee.Date(
        latest_timestamp
    )
    .format(
        "YYYY-MM-dd"
    )
    .getInfo()
)


latest_year = int(
    latest_date[:4]
)

latest_month = int(
    latest_date[5:7]
)


print()
print(
    "✓ Dernière image disponible :"
)

print(
    f"  {latest_date}"
)


# ============================================================
# 20. TÉLÉCHARGEMENT HTTP
# ============================================================

def download_file(
    url,
    output_file
):

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
                timeout=1800
            )

            response.raise_for_status()

            with open(
                output_file,
                "wb"
            ) as f:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if chunk:

                        f.write(chunk)


            if os.path.exists(
                output_file
            ):

                size = (
                    os.path.getsize(
                        output_file
                    )
                )

                if size > 0:

                    print(
                        f"        ✓ "
                        f"{size / 1024 / 1024:.2f} MB"
                    )

                    return True


        except Exception as e:

            print(
                f"        ⚠ Erreur : {e}"
            )


            if os.path.exists(
                output_file
            ):

                try:

                    os.remove(
                        output_file
                    )

                except Exception:
                    pass


            if attempt < MAX_RETRIES:

                time.sleep(5)


    return False


# ============================================================
# 21. MOSAÏQUE DES TUILES
# ============================================================

def mosaic_tiles(
    tile_files,
    output_file,
    aoi_geometry_shapely
):

    print()
    print(
        "    Fusion des tuiles..."
    )

    src_files = []

    try:

        for file in tile_files:

            src = rasterio.open(
                file
            )

            src_files.append(
                src
            )


        if len(src_files) == 0:

            raise ValueError(
                "Aucune tuile disponible."
            )


        mosaic, out_transform = merge(
            src_files,
            method="mean"
        )


        # ----------------------------------------------------
        # Profil
        # ----------------------------------------------------

        profile = src_files[0].profile.copy()

        profile.update(

            driver="GTiff",

            height=mosaic.shape[1],

            width=mosaic.shape[2],

            transform=out_transform,

            count=1,

            dtype="float32",

            nodata=-9999,

            compress=COMPRESSION,

            BIGTIFF="YES"
        )


        # ----------------------------------------------------
        # Nettoyage NaN
        # ----------------------------------------------------

        mosaic = mosaic.astype(
            "float32"
        )


        mosaic[
            ~__import__(
                "numpy"
            ).isfinite(
                mosaic
            )
        ] = -9999


        # ----------------------------------------------------
        # Écriture
        # ----------------------------------------------------

        with rasterio.open(
            output_file,
            "w",
            **profile
        ) as dst:

            dst.write(
                mosaic[0],
                1
            )


        print(
            "    ✓ Mosaïque créée."
        )

        print(
            f"    → {output_file}"
        )


    finally:

        for src in src_files:

            src.close()


# ============================================================
# 22. TRAITEMENT DES MOIS
# ============================================================

total_months = (
    (
        latest_year
        - START_YEAR
    )
    * 12
    + latest_month
)


current_month = 0

successful = 0
skipped = 0
failed = 0
no_data = 0


print()
print("=" * 70)

print(
    "TÉLÉCHARGEMENT NDVI LANDSAT"
)

print(
    f"{START_YEAR} → "
    f"{latest_year}-{latest_month:02d}"
)

print("=" * 70)

print(
    f"Nombre de mois : "
    f"{total_months}"
)


# ============================================================
# 23. BOUCLE ANNÉES
# ============================================================

for year in range(
    START_YEAR,
    latest_year + 1
):

    year_dir = os.path.join(
        OUTPUT_DIR,
        str(year)
    )

    os.makedirs(
        year_dir,
        exist_ok=True
    )


    if year == latest_year:

        max_month = latest_month

    else:

        max_month = 12


    print()
    print("-" * 70)

    print(
        f"ANNÉE {year}"
    )

    print("-" * 70)


    # ========================================================
    # BOUCLE MOIS
    # ========================================================

    for month in range(
        1,
        max_month + 1
    ):

        current_month += 1

        month_str = (
            f"{month:02d}"
        )

        period = (
            f"{year}_{month_str}"
        )


        # ----------------------------------------------------
        # FICHIER FINAL
        # ----------------------------------------------------

        output_file = os.path.join(
            year_dir,
            f"NDVI_LANDSAT_{period}.tif"
        )


        print()
        print(
            f"[{current_month}/"
            f"{total_months}] "
            f"NDVI LANDSAT "
            f"{year}-{month_str}"
        )


        # ====================================================
        # DÉJÀ TERMINÉ
        # ====================================================

        if os.path.exists(
            output_file
        ):

            size = os.path.getsize(
                output_file
            )

            if size > 0:

                print(
                    "    ✓ Mosaïque déjà présente "
                    "— ignorée."
                )

                skipped += 1

                continue


        # ====================================================
        # DOSSIER TEMPORAIRE DU MOIS
        # ====================================================

        month_temp_dir = os.path.join(
            TEMP_DIR,
            period
        )


        os.makedirs(
            month_temp_dir,
            exist_ok=True
        )


        # ====================================================
        # DATES
        # ====================================================

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


        # ====================================================
        # COLLECTION DU MOIS
        # ====================================================

        monthly_collection = (
            landsat_ndvi
            .filterDate(
                start_date,
                end_date
            )
            .filterBounds(
                aoi_geometry
            )
        )


        try:

            image_count = (
                monthly_collection
                .size()
                .getInfo()
            )

        except Exception as e:

            print(
                f"    ✗ Erreur collection : "
                f"{e}"
            )

            failed += 1

            continue


        print(
            f"    Images Landsat : "
            f"{image_count}"
        )


        # ====================================================
        # PAS DE DONNÉES
        # ====================================================

        if image_count == 0:

            print(
                "    ⚠ Aucune donnée."
            )

            no_data += 1

            continue


        # ====================================================
        # MOYENNE MENSUELLE
        # ====================================================

        try:

            monthly_ndvi = (
                monthly_collection
                .mean()
                .rename(
                    "NDVI"
                )
            )

        except Exception as e:

            print(
                f"    ✗ Erreur NDVI : "
                f"{e}"
            )

            failed += 1

            continue


        # ====================================================
        # TÉLÉCHARGEMENT DES TUILES
        # ====================================================

        tile_files = []

        tile_number = 0


        print()
        print(
            f"    Nombre de tuiles : "
            f"{len(tiles)}"
        )


        for tile_geometry in tiles:

            tile_number += 1


            tile_file = os.path.join(
                month_temp_dir,
                f"tile_{tile_number:04d}.tif"
            )


            print()
            print(
                f"    Tuile "
                f"{tile_number}/"
                f"{len(tiles)}"
            )


            # ------------------------------------------------
            # Si tuile déjà téléchargée
            # ------------------------------------------------

            if os.path.exists(
                tile_file
            ):

                if os.path.getsize(
                    tile_file
                ) > 0:

                    print(
                        "        ✓ Tuile déjà présente."
                    )

                    tile_files.append(
                        tile_file
                    )

                    continue


            # ------------------------------------------------
            # Intersection tuile / AOI
            # ------------------------------------------------

            intersection = (
                tile_geometry.intersection(
                    aoi_geometry_shapely
                )
            )


            if intersection.is_empty:

                print(
                    "        ⚠ Pas d'intersection."
                )

                continue


            ee_tile_geometry = (
                shapely_to_ee_geometry(
                    intersection
                )
            )


            # ------------------------------------------------
            # Clip
            # ------------------------------------------------

            tile_image = (
                monthly_ndvi
                .clip(
                    ee_tile_geometry
                )
            )


            # ------------------------------------------------
            # URL
            # ------------------------------------------------

            try:

                params = {

                    "name":
                        f"NDVI_LANDSAT_"
                        f"{period}_"
                        f"tile_{tile_number}",

                    "scale":
                        SCALE,

                    "crs":
                        CRS,

                    "region":
                        ee_tile_geometry,

                    "filePerBand":
                        False,

                    "format":
                        "GEO_TIFF"
                }


                print(
                    "        Génération URL..."
                )


                url = (
                    tile_image
                    .getDownloadURL(
                        params
                    )
                )


                print(
                    "        ✓ URL générée."
                )


                success = download_file(
                    url,
                    tile_file
                )


                if success:

                    tile_files.append(
                        tile_file
                    )

                else:

                    print(
                        "        ✗ Échec tuile."
                    )


            except Exception as e:

                print()
                print(
                    "        ✗ Erreur Earth Engine :"
                )

                print(
                    f"          {e}"
                )


            time.sleep(
                DOWNLOAD_PAUSE
            )


        # ====================================================
        # VÉRIFICATION TUILES
        # ====================================================

        print()
        print(
            f"    Tuiles disponibles : "
            f"{len(tile_files)}/"
            f"{len(tiles)}"
        )


        if len(tile_files) == 0:

            print(
                "    ✗ Aucune tuile téléchargée."
            )

            failed += 1

            continue


        # ====================================================
        # MOSAÏQUE
        # ====================================================

        try:

            mosaic_tiles(
                tile_files,
                output_file,
                aoi_geometry_shapely
            )


            successful += 1


        except Exception as e:

            print()
            print(
                "    ✗ Erreur mosaïque :"
            )

            print(
                f"      {e}"
            )

            failed += 1

            continue


        # ====================================================
        # SUPPRESSION TUILES TEMPORAIRES
        # ====================================================

        print()
        print(
            "    Nettoyage des tuiles temporaires..."
        )


        try:

            shutil.rmtree(
                month_temp_dir
            )

            print(
                "    ✓ Tuiles temporaires supprimées."
            )

        except Exception as e:

            print(
                f"    ⚠ Impossible de supprimer "
                f"le dossier temporaire : {e}"
            )


        # ====================================================
        # PAUSE
        # ====================================================

        time.sleep(2)


# ============================================================
# 24. NETTOYAGE GLOBAL
# ============================================================

try:

    if os.path.exists(
        TEMP_DIR
    ):

        remaining = os.listdir(
            TEMP_DIR
        )

        if len(remaining) == 0:

            os.rmdir(
                TEMP_DIR
            )

except Exception:

    pass


# ============================================================
# 25. RÉSUMÉ
# ============================================================

print()
print()
print("=" * 70)
print("TRAITEMENT LANDSAT TERMINÉ")
print("=" * 70)

print()

print(
    f"✓ Mosaïques créées : "
    f"{successful}"
)

print(
    f"↪ Déjà présentes : "
    f"{skipped}"
)

print(
    f"⚠ Mois sans données : "
    f"{no_data}"
)

print(
    f"✗ Échecs : "
    f"{failed}"
)

print()

print(
    "Dernière donnée Landsat détectée :"
)

print(
    f"    {latest_date}"
)

print()

print(
    "Dossier final :"
)

print(
    OUTPUT_DIR
)

print()
print("=" * 70)
print("✓ FIN DU PROGRAMME")
print("=" * 70)