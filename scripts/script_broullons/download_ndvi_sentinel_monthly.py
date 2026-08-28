import os
import time
import requests
import ee
import geopandas as gpd

from shapely.geometry import box, mapping


# ============================================================
# 1. PARAMÈTRES
# ============================================================

# ------------------------------------------------------------
# PÉRIODE D'ÉTUDE
# ------------------------------------------------------------

# Commence par tester une seule année
START_YEAR = 2020
END_YEAR = 2020

# Ensuite, pour toute la période Sentinel-2 :
#
# START_YEAR = 2015
# END_YEAR = 2025


# ------------------------------------------------------------
# PROJET GOOGLE EARTH ENGINE
# ------------------------------------------------------------

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
# DOSSIER DE SORTIE
# ------------------------------------------------------------

OUTPUT_DIR = (
    r"C:\Users\Hanitriniala_RH"
    r"\Documents\Projet_test"
    r"\NDVI_SENTINEL"
)


# ------------------------------------------------------------
# PARAMÈTRES DE TÉLÉCHARGEMENT
# ------------------------------------------------------------

CRS = "EPSG:4326"

# Sentinel-2
SCALE = 10

TILE_SIZE_DEG = 0.20


# Nombre de tentatives
MAX_RETRIES = 3


# Pause entre les téléchargements
DOWNLOAD_DELAY = 1


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

    print(
        "✓ Earth Engine initialisé avec succès."
    )

    print(
        f"✓ Projet Earth Engine : {EE_PROJECT}"
    )

except Exception as e:

    print()
    print(
        "✗ Impossible d'initialiser Earth Engine."
    )

    print(
        f"Erreur : {e}"
    )

    print()
    print(
        "Si nécessaire, exécute :"
    )

    print(
        "earthengine authenticate"
    )

    raise


# ============================================================
# 3. DOSSIER DE SORTIE
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

print()
print("Dossier de sortie :")
print(OUTPUT_DIR)


# ============================================================
# 4. CHARGEMENT DU SHAPEFILE
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT DE L'AOI")
print("=" * 70)


if not os.path.exists(
    AOI_SHP
):

    raise FileNotFoundError(
        f"""
Shapefile introuvable :

{AOI_SHP}
"""
    )


try:

    aoi_gdf = gpd.read_file(
        AOI_SHP
    )

except Exception as e:

    raise RuntimeError(
        f"""
Impossible de lire le shapefile :

{e}
"""
    )


print(
    "✓ Shapefile chargé."
)

print(
    f"  Nombre de géométries : {len(aoi_gdf)}"
)

print(
    f"  CRS actuel : {aoi_gdf.crs}"
)


# ============================================================
# 5. VÉRIFICATION DU CRS
# ============================================================

if aoi_gdf.crs is None:

    raise ValueError(
        "Le shapefile ne possède pas de CRS."
    )


# ============================================================
# 6. NETTOYAGE DES GÉOMÉTRIES
# ============================================================

print()
print(
    "Vérification et correction des géométries..."
)


# Supprimer géométries nulles

aoi_gdf = aoi_gdf[
    aoi_gdf.geometry.notna()
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Aucune géométrie valide dans le shapefile."
    )


# Corriger les géométries invalides

aoi_gdf["geometry"] = (
    aoi_gdf.geometry.make_valid()
)


# Supprimer géométries vides

aoi_gdf = aoi_gdf[
    ~aoi_gdf.geometry.is_empty
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Toutes les géométries sont vides."
    )


print(
    "✓ Géométries corrigées."
)


# ============================================================
# 7. CONVERSION EN EPSG:4326
# ============================================================

aoi_gdf = aoi_gdf.to_crs(
    CRS
)


print(
    "✓ AOI convertie en EPSG:4326."
)


# ============================================================
# 8. UNION DE L'AOI
# ============================================================

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
        "La géométrie globale de l'AOI est vide."
    )


print(
    "✓ Géométrie globale de l'AOI créée."
)


# ============================================================
# 9. CONVERSION DE L'AOI VERS EARTH ENGINE
# ============================================================

aoi_geojson = (
    mapping(
        aoi_geometry_shapely
    )
)


aoi = ee.FeatureCollection(
    [
        ee.Feature(
            ee.Geometry(
                aoi_geojson
            )
        )
    ]
)


aoi_geometry = (
    aoi.geometry()
)


print(
    "✓ AOI prête pour Earth Engine."
)


# ============================================================
# 10. CRÉATION AUTOMATIQUE DES TUILES
# ============================================================

print()
print("=" * 70)
print("DÉCOUPAGE AUTOMATIQUE DE L'AOI")
print("=" * 70)


minx, miny, maxx, maxy = (
    aoi_geometry_shapely.bounds
)


print()
print("Emprise AOI :")

print(
    f"  xmin = {minx}"
)

print(
    f"  ymin = {miny}"
)

print(
    f"  xmax = {maxx}"
)

print(
    f"  ymax = {maxy}"
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
                x + TILE_SIZE_DEG,
                maxx
            ),
            min(
                y + TILE_SIZE_DEG,
                maxy
            )
        )


        # Intersection avec l'AOI

        intersection = (
            tile_polygon.intersection(
                aoi_geometry_shapely
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


        y += TILE_SIZE_DEG


    x += TILE_SIZE_DEG


print()
print(
    f"✓ Nombre de tuiles créées : {len(tiles)}"
)


if len(tiles) == 0:

    raise ValueError(
        "Aucune tuile n'a été créée."
    )


# ============================================================
# 11. AFFICHAGE DES TUILES
# ============================================================

print()
print("Tuiles utilisées :")

for tile in tiles:

    print(
        f"  Tile {tile['id']:03d}"
    )


# ============================================================
# 12. COLLECTION SENTINEL-2
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT SENTINEL-2")
print("=" * 70)


sentinel = (
    ee.ImageCollection(
        "COPERNICUS/S2_SR_HARMONIZED"
    )

    .filterBounds(
        aoi_geometry
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
# 13. MASQUE DES NUAGES SENTINEL-2
# ============================================================

def mask_sentinel2(
    image
):

    """
    Masque les nuages et pixels problématiques.

    QA60 :
        bit 10 = nuage
        bit 11 = cirrus

    SCL :
        3  = ombre de nuage
        8  = nuage probabilité moyenne
        9  = nuage probabilité forte
        10 = cirrus
        11 = neige/glace
    """

    qa = image.select(
        "QA60"
    )


    cloud_bit = (
        1 << 10
    )


    cirrus_bit = (
        1 << 11
    )


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


# Appliquer le masque

sentinel = (
    sentinel.map(
        mask_sentinel2
    )
)


# ============================================================
# 14. FONCTION DE TÉLÉCHARGEMENT
# ============================================================

def download_file(
    url,
    output_file
):

    """
    Télécharge un fichier directement
    depuis Earth Engine vers le PC.
    """

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            print(
                f"        Téléchargement "
                f"(tentative "
                f"{attempt}/{MAX_RETRIES})..."
            )


            response = requests.get(
                url,
                stream=True,
                timeout=600
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

                        f.write(
                            chunk
                        )


            if os.path.exists(
                output_file
            ):

                file_size = (
                    os.path.getsize(
                        output_file
                    )
                )


                if file_size > 0:

                    print(
                        f"        ✓ Téléchargé : "
                        f"{file_size / 1024 / 1024:.2f} MB"
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

                print(
                    "        Nouvelle tentative "
                    "dans 5 secondes..."
                )


                time.sleep(
                    5
                )


    return False


# ============================================================
# 15. TRAITEMENT DES ANNÉES
# ============================================================

successful = 0

failed = 0

skipped = 0

empty_tiles = 0

total_months = (
    (END_YEAR - START_YEAR + 1)
    * 12
)


print()
print("=" * 70)

print(
    f"TÉLÉCHARGEMENT NDVI SENTINEL-2"
)

print(
    f"{START_YEAR} → {END_YEAR}"
)

print("=" * 70)


print()
print(
    f"Nombre de mois : {total_months}"
)

print(
    f"Nombre de tuiles : {len(tiles)}"
)

print(
    f"Fichiers potentiels : "
    f"{total_months * len(tiles)}"
)


# ============================================================
# 16. BOUCLE ANNÉES
# ============================================================

for year in range(
    START_YEAR,
    END_YEAR + 1
):


    print()
    print()
    print("#" * 70)

    print(
        f"ANNÉE {year}"
    )

    print(
        "#" * 70
    )


    # ========================================================
    # BOUCLE MOIS
    # ========================================================

    for month in range(
        1,
        13
    ):


        month_str = (
            f"{month:02d}"
        )


        period = (
            f"{year}_{month_str}"
        )


        print()
        print(
            "=" * 70
        )


        print(
            f"NDVI SENTINEL-2 "
            f"{period}"
        )


        print(
            "=" * 70
        )


        # ----------------------------------------------------
        # DATES DU MOIS
        # ----------------------------------------------------

        start_date = (
            ee.Date.fromYMD(
                year,
                month,
                1
            )
        )


        end_date = (
            start_date.advance(
                1,
                "month"
            )
        )


        # ----------------------------------------------------
        # COLLECTION MENSUELLE
        # ----------------------------------------------------

        monthly_collection = (
            sentinel
            .filterDate(
                start_date,
                end_date
            )
        )


        # ----------------------------------------------------
        # NOMBRE D'IMAGES
        # ----------------------------------------------------

        try:

            image_count = (
                monthly_collection
                .size()
                .getInfo()
            )


        except Exception as e:

            print(
                f"✗ Erreur lors du comptage : {e}"
            )


            failed += len(
                tiles
            )

            continue


        print()
        print(
            f"Images Sentinel-2 disponibles : "
            f"{image_count}"
        )


        # ----------------------------------------------------
        # AUCUNE IMAGE
        # ----------------------------------------------------

        if image_count == 0:

            print(
                "⚠ Aucune image pour ce mois."
            )


            failed += len(
                tiles
            )

            continue


        # ====================================================
        # CALCUL NDVI MENSUEL
        # ====================================================

        print()
        print(
            "Calcul du NDVI mensuel..."
        )


        try:

            monthly_ndvi = (
                monthly_collection

                .map(
                    lambda image:
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

                .mean()

                .toFloat()
            )


            print(
                "✓ NDVI mensuel calculé."
            )


        except Exception as e:

            print(
                f"✗ Erreur calcul NDVI : {e}"
            )


            failed += len(
                tiles
            )

            continue


        # ====================================================
        # BOUCLE SUR LES TUILES
        # ====================================================

        for tile in tiles:


            tile_id = tile["id"]

            tile_geometry = tile["geometry"]


            tile_name = (
                f"tile_{tile_id:03d}"
            )


            print()
            print(
                "-" * 70
            )


            print(
                f"{period} | "
                f"{tile_name}"
            )


            print(
                "-" * 70
            )


            # ------------------------------------------------
            # DOSSIER ANNÉE / MOIS
            # ------------------------------------------------

            month_dir = os.path.join(
                OUTPUT_DIR,
                str(year),
                month_str
            )


            os.makedirs(
                month_dir,
                exist_ok=True
            )


            # ------------------------------------------------
            # NOM FICHIER
            # ------------------------------------------------

            output_file = os.path.join(
                month_dir,
                (
                    f"NDVI_SENTINEL_"
                    f"{period}_"
                    f"{tile_name}.tif"
                )
            )


            # ------------------------------------------------
            # SI FICHIER EXISTE
            # ------------------------------------------------

            if os.path.exists(
                output_file
            ):

                if (
                    os.path.getsize(
                        output_file
                    ) > 0
                ):

                    print(
                        "    ✓ Fichier déjà présent."
                    )

                    skipped += 1

                    continue


            # ------------------------------------------------
            # CONVERSION TUILE → EE
            # ------------------------------------------------

            try:

                tile_geojson = mapping(
                    tile_geometry
                )


                tile_ee = ee.Geometry(
                    tile_geojson
                )


            except Exception as e:

                print(
                    f"    ✗ Erreur géométrie : "
                    f"{e}"
                )


                failed += 1

                continue


            # ------------------------------------------------
            # VÉRIFICATION DES IMAGES SUR LA TUILE
            # ------------------------------------------------

            try:

                tile_image_count = (
                    monthly_collection
                    .filterBounds(
                        tile_ee
                    )
                    .size()
                    .getInfo()
                )


            except Exception as e:

                print(
                    f"    ✗ Erreur vérification "
                    f"tuile : {e}"
                )


                failed += 1

                continue


            if tile_image_count == 0:

                print(
                    "    ⚠ Aucune image "
                    "sur cette tuile."
                )


                empty_tiles += 1

                continue


            print(
                f"    Images dans la tuile : "
                f"{tile_image_count}"
            )


            # ------------------------------------------------
            # CLIP DU NDVI
            # ------------------------------------------------

            try:

                tile_ndvi = (
                    monthly_ndvi
                    .clip(
                        tile_ee
                    )
                )


            except Exception as e:

                print(
                    f"    ✗ Erreur clip : {e}"
                )


                failed += 1

                continue


            # ------------------------------------------------
            # GÉNÉRATION URL
            # ------------------------------------------------

            try:

                print(
                    "    Génération de l'URL..."
                )


                download_url = (
                    tile_ndvi
                    .getDownloadURL(
                        {
                            "name":
                                (
                                    f"NDVI_SENTINEL_"
                                    f"{period}_"
                                    f"{tile_name}"
                                ),

                            "scale":
                                SCALE,

                            "crs":
                                CRS,

                            "region":
                                tile_ee,

                            "filePerBand":
                                False,

                            "format":
                                "GEO_TIFF"
                        }
                    )
                )


                print(
                    "    ✓ URL générée."
                )


            except Exception as e:

                print()
                print(
                    "    ✗ Erreur Earth Engine "
                    "pendant la génération de l'URL :"
                )

                print(
                    f"      {e}"
                )


                failed += 1

                continue


            # ------------------------------------------------
            # TÉLÉCHARGEMENT
            # ------------------------------------------------

            success = (
                download_file(
                    download_url,
                    output_file
                )
            )


            if success:

                successful += 1


            else:

                print(
                    "    ✗ Échec du téléchargement."
                )


                failed += 1


            # ------------------------------------------------
            # PAUSE
            # ------------------------------------------------

            time.sleep(
                DOWNLOAD_DELAY
            )


# ============================================================
# 17. RÉSUMÉ FINAL
# ============================================================

print()
print()
print("=" * 70)
print("TRAITEMENT SENTINEL-2 TERMINÉ")
print("=" * 70)


print()
print(
    f"✓ Fichiers téléchargés : "
    f"{successful}"
)


print(
    f"↪ Fichiers déjà présents : "
    f"{skipped}"
)


print(
    f"⚠ Tuiles sans image : "
    f"{empty_tiles}"
)


print(
    f"✗ Échecs : "
    f"{failed}"
)


print()
print(
    f"Nombre de mois : "
    f"{total_months}"
)


print(
    f"Nombre de tuiles : "
    f"{len(tiles)}"
)


print(
    f"Fichiers potentiels : "
    f"{total_months * len(tiles)}"
)


print()
print(
    "Dossier des résultats :"
)


print(
    OUTPUT_DIR
)


print()
print("=" * 70)
print("FIN DU PROGRAMME")
print("=" * 70)