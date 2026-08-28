import os
import time
import requests
import ee
import geopandas as gpd


# ============================================================
# 1. PARAMÈTRES
# ============================================================

# Année de début
START_YEAR = 2000


# ============================================================
# PROJET GOOGLE EARTH ENGINE
# ============================================================

EE_PROJECT = "eehanitriniala"


# ============================================================
# CHEMIN DU SHAPEFILE
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
    r"\dynatsimo-react\NDVI_MODIS"
)


# ============================================================
# PARAMÈTRES MODIS
# ============================================================

# MOD13Q1 = résolution 250 m
SCALE = 250

# Projection de sortie
CRS = "EPSG:4326"

# Facteur d'échelle MODIS
# NDVI réel = valeur MODIS × 0.0001
NDVI_SCALE = 0.0001

# Nombre maximum de tentatives de téléchargement
MAX_RETRIES = 3


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
    print(
        "✗ Impossible d'initialiser "
        "Earth Engine."
    )

    print()
    print("Erreur :")
    print(e)

    print()
    print(
        "Si nécessaire, exécute :"
    )

    print()
    print(
        "    earthengine authenticate"
    )

    print()

    raise


# ============================================================
# 3. CRÉATION DU DOSSIER DE SORTIE
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


if not os.path.exists(AOI_SHP):

    raise FileNotFoundError(
        f"\nShapefile introuvable :\n{AOI_SHP}"
    )


try:

    aoi_gdf = gpd.read_file(
        AOI_SHP
    )

except Exception as e:

    raise RuntimeError(
        "Impossible de lire le shapefile :\n"
        f"{e}"
    )


print(
    "✓ Shapefile chargé."
)

print(
    f"  Nombre de géométries : "
    f"{len(aoi_gdf)}"
)

print(
    f"  CRS actuel : "
    f"{aoi_gdf.crs}"
)


# ============================================================
# 5. VÉRIFICATION DU CRS
# ============================================================

if aoi_gdf.crs is None:

    raise ValueError(
        "Le shapefile n'a pas de système "
        "de coordonnées (CRS)."
    )


# ============================================================
# 6. CORRECTION DES GÉOMÉTRIES
# ============================================================

print()
print(
    "Vérification des géométries..."
)


# Supprimer les géométries nulles

aoi_gdf = aoi_gdf[
    aoi_gdf.geometry.notna()
].copy()


if len(aoi_gdf) == 0:

    raise ValueError(
        "Le shapefile ne contient "
        "aucune géométrie valide."
    )


# Corriger les géométries invalides

try:

    aoi_gdf["geometry"] = (
        aoi_gdf.geometry.make_valid()
    )

except AttributeError:

    print(
        "⚠ make_valid() indisponible."
    )

    print(
        "   Les géométries existantes "
        "seront utilisées."
    )


print(
    "✓ Géométries vérifiées."
)


# ============================================================
# 7. CONVERSION EN EPSG:4326
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
# 8. UNION DES GÉOMÉTRIES
# ============================================================

print()
print(
    "Préparation de la géométrie globale "
    "de l'AOI..."
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
        "La géométrie globale de l'AOI "
        "est vide."
    )


print(
    "✓ Géométrie globale créée."
)


# ============================================================
# 9. CONVERSION GEOJSON → EARTH ENGINE
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


aoi_geometry = (
    aoi.geometry()
)


print(
    "✓ AOI prête pour Earth Engine."
)


# ============================================================
# 10. CHARGEMENT MODIS
# ============================================================

print()
print("=" * 70)
print("CHARGEMENT DES DONNÉES MODIS")
print("=" * 70)


modis = (
    ee.ImageCollection(
        "MODIS/061/MOD13Q1"
    )
    .filterBounds(
        aoi_geometry
    )
    .select(
        "NDVI"
    )
)


print(
    "✓ Collection MODIS MOD13Q1 chargée."
)


# ============================================================
# 11. DÉTECTION AUTOMATIQUE DE LA DERNIÈRE
#     DONNÉE MODIS DISPONIBLE
# ============================================================

print()
print("=" * 70)
print(
    "RECHERCHE DE LA DERNIÈRE DONNÉE MODIS"
)
print("=" * 70)


try:

    # Image la plus récente
    latest_image = (
        modis
        .sort(
            "system:time_start",
            False
        )
        .first()
    )


    # Vérifier qu'une image existe

    if latest_image is None:

        raise ValueError(
            "Aucune donnée MODIS disponible."
        )


    # Date de la dernière image

    latest_timestamp = (
        latest_image
        .get(
            "system:time_start"
        )
        .getInfo()
    )


    if latest_timestamp is None:

        raise ValueError(
            "Impossible de déterminer "
            "la date de la dernière image MODIS."
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


    latest_year = (
        int(latest_date[0:4])
    )


    latest_month = (
        int(latest_date[5:7])
    )


    print()
    print(
        "✓ Dernière image MODIS disponible :"
    )

    print(
        f"  {latest_date}"
    )

    print()
    print(
        "✓ Le téléchargement sera effectué "
        "jusqu'au :"
    )

    print(
        f"  {latest_year}-{latest_month:02d}"
    )


except Exception as e:

    raise RuntimeError(
        "\nImpossible de déterminer "
        "la dernière donnée MODIS :\n"
        f"{e}"
    )


# ============================================================
# 12. FONCTION DE TÉLÉCHARGEMENT
# ============================================================

def download_file(
    url,
    output_file
):

    """
    Télécharge un fichier depuis une URL
    avec plusieurs tentatives.
    """

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            print(
                f"    Téléchargement "
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

                        f.write(chunk)


            # ------------------------------------------------
            # Vérification du fichier
            # ------------------------------------------------

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
                        f"    ✓ Fichier téléchargé "
                        f"({file_size / 1024 / 1024:.2f} MB)"
                    )

                    return True


        except Exception as e:

            print(
                f"    ⚠ Erreur : {e}"
            )


            # Supprimer fichier incomplet

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
                    "    Nouvelle tentative "
                    "dans 5 secondes..."
                )

                time.sleep(5)


    return False


# ============================================================
# 13. CALCUL DU NOMBRE TOTAL DE MOIS
# ============================================================

total_months = (
    (
        latest_year
        - START_YEAR
        + 1
    )
    * 12
    - (12 - latest_month)
)


current_month = 0

successful = 0

failed = 0

skipped = 0

no_data = 0


# ============================================================
# 14. DÉBUT DU TRAITEMENT
# ============================================================

print()
print("=" * 70)

print(
    "TÉLÉCHARGEMENT NDVI MODIS"
)

print(
    f"{START_YEAR} → "
    f"{latest_year}-{latest_month:02d}"
)

print("=" * 70)

print()
print(
    f"Nombre de mois à vérifier : "
    f"{total_months}"
)


# ============================================================
# 15. BOUCLE ANNÉES
# ============================================================

for year in range(
    START_YEAR,
    latest_year + 1
):


    # --------------------------------------------------------
    # Dossier de l'année
    # --------------------------------------------------------

    year_dir = os.path.join(
        OUTPUT_DIR,
        str(year)
    )


    os.makedirs(
        year_dir,
        exist_ok=True
    )


    print()
    print("-" * 70)

    print(
        f"ANNÉE {year}"
    )

    print("-" * 70)


    # ========================================================
    # DÉTERMINER LE DERNIER MOIS À TRAITER
    # ========================================================

    if year == latest_year:

        last_month = latest_month

    else:

        last_month = 12


    # ========================================================
    # BOUCLE MOIS
    # ========================================================

    for month in range(
        1,
        last_month + 1
    ):


        current_month += 1


        month_str = (
            f"{month:02d}"
        )


        period = (
            f"{year}_{month_str}"
        )


        output_file = os.path.join(
            year_dir,
            f"NDVI_MODIS_{period}.tif"
        )


        print()

        print(
            f"[{current_month}/"
            f"{total_months}] "
            f"NDVI {year}-{month_str}"
        )


        # ====================================================
        # VÉRIFIER SI LE FICHIER EXISTE
        # ====================================================

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
                    "    ✓ Fichier déjà présent "
                    "— ignoré."
                )

                skipped += 1

                continue


        # ====================================================
        # DATES DU MOIS
        # ====================================================

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


        # ====================================================
        # COLLECTION DU MOIS
        # ====================================================

        monthly_collection = (
            modis
            .filterDate(
                start_date,
                end_date
            )
        )


        # ====================================================
        # NOMBRE D'IMAGES
        # ====================================================

        try:

            image_count = (
                monthly_collection
                .size()
                .getInfo()
            )

        except Exception as e:

            print(
                "    ✗ Impossible de connaître "
                "le nombre d'images :"
            )

            print(
                f"      {e}"
            )

            failed += 1

            continue


        print(
            f"    Images MODIS disponibles : "
            f"{image_count}"
        )


        # ====================================================
        # AUCUNE DONNÉE
        # ====================================================

        if image_count == 0:

            print(
                "    ⚠ Aucune donnée pour ce mois."
            )

            no_data += 1

            continue


        # ====================================================
        # MOYENNE MENSUELLE NDVI
        # ====================================================

        try:

            monthly_ndvi = (
                monthly_collection
                .mean()
                .multiply(
                    NDVI_SCALE
                )
                .rename(
                    "NDVI"
                )
                .clip(
                    aoi_geometry
                )
            )

        except Exception as e:

            print(
                f"    ✗ Erreur calcul NDVI : "
                f"{e}"
            )

            failed += 1

            continue


        # ====================================================
        # PARAMÈTRES DOWNLOAD
        # ====================================================

        try:

            download_params = {

                "name":
                    f"NDVI_MODIS_{period}",

                "scale":
                    SCALE,

                "crs":
                    CRS,

                "region":
                    aoi_geometry,

                "filePerBand":
                    False,

                "format":
                    "GEO_TIFF"
            }


            # =================================================
            # URL DE TÉLÉCHARGEMENT
            # =================================================

            print(
                "    Génération de l'URL..."
            )


            download_url = (
                monthly_ndvi
                .getDownloadURL(
                    download_params
                )
            )


            print(
                "    ✓ URL générée."
            )


            # =================================================
            # TÉLÉCHARGEMENT DIRECT
            # =================================================

            success = download_file(
                download_url,
                output_file
            )


            if success:

                successful += 1

            else:

                print(
                    "    ✗ Échec définitif."
                )

                failed += 1


        except Exception as e:

            print()
            print(
                "    ✗ Erreur Earth Engine :"
            )

            print(
                f"      {e}"
            )

            failed += 1


        # ====================================================
        # PETITE PAUSE
        # ====================================================

        time.sleep(1)


# ============================================================
# 16. RÉSUMÉ FINAL
# ============================================================

print()
print()
print("=" * 70)

print(
    "TRAITEMENT TERMINÉ"
)

print("=" * 70)

print()

print(
    f"✓ Téléchargés : "
    f"{successful}"
)

print(
    f"↪ Déjà présents : "
    f"{skipped}"
)

print(
    f"⚠ Sans données : "
    f"{no_data}"
)

print(
    f"✗ Échecs : "
    f"{failed}"
)

print()

print(
    "Dernière donnée MODIS détectée :"
)

print(
    f"    {latest_date}"
)

print()

print(
    "Dossier des résultats :"
)

print(
    OUTPUT_DIR
)

print("=" * 70)