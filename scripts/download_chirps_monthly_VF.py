# ================================================================
# 1. IMPORTATIONS
# ================================================================

import os
import sys
import gzip
import shutil
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import requests
import rasterio
import geopandas as gpd

from rasterio.mask import mask


# ================================================================
# 2. CONFIGURATION
# ================================================================


from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

# ----------------------------------------------------------------
# SHAPEFILE DE LA ZONE D'ÉTUDE
# ----------------------------------------------------------------

SHAPEFILE = str(ROOT_DIR / "Regions 3" / "3_region.shp")


# ----------------------------------------------------------------
# DOSSIER DE SORTIE
# ----------------------------------------------------------------

OUTPUT_DIR = str(ROOT_DIR / "CHIRPS_data")


# ----------------------------------------------------------------
# DOSSIER TEMPORAIRE
# ----------------------------------------------------------------

TEMP_DIR = os.path.join(
    OUTPUT_DIR,
    "_temp"
)


# ----------------------------------------------------------------
# URL DE BASE CHIRPS
# ----------------------------------------------------------------

BASE_URL = (
    "https://data.chc.ucsb.edu/products/"
    "CHIRPS-2.0/global_monthly/tifs"
)


# ----------------------------------------------------------------
# DATE DE DÉBUT
# ----------------------------------------------------------------

START_YEAR = 1981
START_MONTH = 1


# ----------------------------------------------------------------
# IMPORTANT :
#
# Il n'y a PAS de END_YEAR.
#
# Le script détecte automatiquement le dernier mois disponible.
# ----------------------------------------------------------------


# ----------------------------------------------------------------
# Valeur NoData
# ----------------------------------------------------------------

NODATA_VALUE = -9999


# ----------------------------------------------------------------
# Paramètres de téléchargement
# ----------------------------------------------------------------

TIMEOUT = 120

CHUNK_SIZE = 1024 * 1024  # 1 Mo

MAX_RETRIES = 3

RETRY_DELAY = 5


# ----------------------------------------------------------------
# Petite pause entre les téléchargements
# ----------------------------------------------------------------

DOWNLOAD_DELAY = 1


# ================================================================
# 3. CRÉATION DES DOSSIERS
# ================================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

os.makedirs(
    TEMP_DIR,
    exist_ok=True
)


# ================================================================
# 4. AFFICHAGE INITIAL
# ================================================================

print()
print("=" * 75)
print("CHIRPS - TÉLÉCHARGEMENT AUTOMATIQUE")
print("=" * 75)

print()
print("Date de début :")
print(
    f"  {START_YEAR}-{START_MONTH:02d}"
)

print()
print("Date de fin :")
print(
    "  AUTOMATIQUE → dernier mois disponible sur CHIRPS"
)

print()
print("Zone d'étude :")
print(
    SHAPEFILE
)

print()
print("Dossier de sortie :")
print(
    OUTPUT_DIR
)

print()
print(
    "Le script va continuer jusqu'à ce que "
    "CHIRPS ne fournisse plus de fichier."
)

print("=" * 75)


# ================================================================
# 5. VÉRIFICATION DU SHAPEFILE
# ================================================================

if not os.path.exists(
    SHAPEFILE
):

    raise FileNotFoundError(
        "\n❌ Shapefile introuvable :\n"
        f"{SHAPEFILE}"
    )


# ================================================================
# 6. LECTURE DU SHAPEFILE
# ================================================================

print()
print("=" * 75)
print("LECTURE DU SHAPEFILE")
print("=" * 75)

try:

    zones = gpd.read_file(
        SHAPEFILE
    )

except Exception as e:

    raise RuntimeError(
        "\n❌ Impossible de lire le shapefile :\n"
        f"{e}"
    )


# ================================================================
# 7. VÉRIFICATION DU SHAPEFILE
# ================================================================

if zones.empty:

    raise ValueError(
        "❌ Le shapefile ne contient aucune géométrie."
    )


if zones.crs is None:

    raise ValueError(
        "❌ Le shapefile ne possède pas de CRS."
    )


# Supprimer les géométries NULL

zones = zones[
    zones.geometry.notna()
].copy()


if zones.empty:

    raise ValueError(
        "❌ Aucune géométrie valide."
    )


print()
print(
    f"✓ Nombre de géométries : {len(zones)}"
)

print(
    f"✓ CRS : {zones.crs}"
)


# ================================================================
# 8. CORRECTION DES GÉOMÉTRIES INVALIDES
# ================================================================

invalid_count = (
    ~zones.geometry.is_valid
).sum()


if invalid_count > 0:

    print()
    print(
        f"⚠ {invalid_count} géométrie(s) invalide(s)."
    )

    print(
        "Correction des géométries..."
    )

    zones["geometry"] = (
        zones.geometry.buffer(0)
    )

    print(
        "✓ Géométries corrigées."
    )


# ================================================================
# 9. FONCTION DE TÉLÉCHARGEMENT
# ================================================================

def download_file(
    url,
    destination
):
    """
    Télécharge un fichier CHIRPS.

    Retourne :

    True
        téléchargement réussi

    False
        erreur temporaire après plusieurs essais

    "NOT_FOUND"
        fichier inexistant sur le serveur
    """


    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        print()
        print(
            f"Tentative {attempt}/{MAX_RETRIES}"
        )

        try:

            with requests.get(
                url,
                stream=True,
                timeout=TIMEOUT
            ) as response:


                # =================================================
                # FICHIER NON DISPONIBLE
                # =================================================

                if response.status_code == 404:

                    print()
                    print(
                        "⚠ HTTP 404 : fichier inexistant."
                    )

                    return "NOT_FOUND"


                # =================================================
                # AUTRE ERREUR HTTP
                # =================================================

                if response.status_code != 200:

                    print(
                        f"⚠ HTTP {response.status_code}"
                    )

                    if attempt < MAX_RETRIES:

                        print(
                            f"Nouvelle tentative dans "
                            f"{RETRY_DELAY} secondes..."
                        )

                        time.sleep(
                            RETRY_DELAY
                        )

                        continue

                    return False


                # =================================================
                # TAILLE DU FICHIER
                # =================================================

                total_size = int(
                    response.headers.get(
                        "content-length",
                        0
                    )
                )


                downloaded = 0


                # =================================================
                # ÉCRITURE
                # =================================================

                with open(
                    destination,
                    "wb"
                ) as f:

                    for chunk in response.iter_content(
                        chunk_size=CHUNK_SIZE
                    ):

                        if chunk:

                            f.write(chunk)

                            downloaded += len(chunk)


                            # -------------------------------------
                            # AFFICHAGE PROGRESSION
                            # -------------------------------------

                            if total_size > 0:

                                percent = (
                                    downloaded /
                                    total_size
                                ) * 100

                                print(
                                    f"\rProgression : "
                                    f"{percent:6.2f} %",
                                    end=""
                                )


                print()


            print(
                "✓ Téléchargement terminé."
            )

            return True


        except requests.exceptions.RequestException as e:

            print()
            print(
                f"⚠ Erreur réseau : {e}"
            )

            if attempt < MAX_RETRIES:

                print(
                    f"Nouvelle tentative dans "
                    f"{RETRY_DELAY} secondes..."
                )

                time.sleep(
                    RETRY_DELAY
                )

            else:

                print(
                    "❌ Nombre maximum de tentatives atteint."
                )


    return False


# ================================================================
# 10. FONCTION DE DÉCOMPRESSION
# ================================================================

def decompress_gzip(
    gz_path,
    tif_path
):
    """
    Décompresse un fichier .gz en .tif.
    """

    print()
    print(
        "Décompression..."
    )

    try:

        with gzip.open(
            gz_path,
            "rb"
        ) as f_in:

            with open(
                tif_path,
                "wb"
            ) as f_out:

                shutil.copyfileobj(
                    f_in,
                    f_out
                )


        print(
            "✓ Décompression terminée."
        )

        return True


    except Exception as e:

        print()
        print(
            f"❌ Erreur de décompression : {e}"
        )

        return False


# ================================================================
# 11. FONCTION DE DÉCOUPAGE
# ================================================================

def clip_raster(
    input_raster,
    output_raster,
    zones
):
    """
    Découpe le raster CHIRPS selon la zone d'étude.

    L'extérieur de la zone est :
        -9999
        + masque transparent
    """

    print()
    print(
        "Découpage selon la zone d'étude..."
    )


    try:

        # ========================================================
        # OUVERTURE DU RASTER
        # ========================================================

        with rasterio.open(
            input_raster
        ) as src:


            print(
                f"CRS du raster : {src.crs}"
            )

            print(
                f"NoData original : {src.nodata}"
            )


            # ====================================================
            # REPROJECTION DU SHAPEFILE
            # ====================================================

            if zones.crs != src.crs:

                print(
                    "Reprojection du shapefile "
                    "vers le CRS du raster..."
                )

                zones_proj = zones.to_crs(
                    src.crs
                )

            else:

                zones_proj = zones


            # ====================================================
            # GÉOMÉTRIES
            # ====================================================

            geometries = [
                geom.__geo_interface__
                for geom in zones_proj.geometry
                if (
                    geom is not None
                    and not geom.is_empty
                )
            ]


            if not geometries:

                raise ValueError(
                    "Aucune géométrie utilisable."
                )


            # ====================================================
            # DÉCOUPAGE
            # ====================================================

            clipped_data, clipped_transform = mask(
                src,
                geometries,
                crop=True,
                filled=True,
                nodata=NODATA_VALUE
            )


            # ====================================================
            # MÉTADONNÉES
            # ====================================================

            metadata = src.meta.copy()

            metadata.update({

                "driver": "GTiff",

                "height":
                    clipped_data.shape[1],

                "width":
                    clipped_data.shape[2],

                "transform":
                    clipped_transform,

                "nodata":
                    NODATA_VALUE,

                "compress":
                    "deflate",

                "predictor":
                    2

            })


            # ====================================================
            # ÉCRITURE
            # ====================================================

            with rasterio.open(
                output_raster,
                "w",
                **metadata
            ) as dst:


                # ----------------------------------------------
                # Écriture des données
                # ----------------------------------------------

                dst.write(
                    clipped_data
                )


                # ----------------------------------------------
                # MASQUE DE TRANSPARENCE
                # ----------------------------------------------
                #
                # 0   = transparent
                # 255 = visible
                #
                # ----------------------------------------------

                mask_data = (
                    clipped_data[0] != NODATA_VALUE
                ).astype(
                    "uint8"
                ) * 255


                dst.write_mask(
                    mask_data
                )


        # ========================================================
        # VÉRIFICATION
        # ========================================================

        with rasterio.open(
            output_raster
        ) as check:

            print()
            print(
                "✓ Vérification du raster final"
            )

            print(
                f"  CRS       : {check.crs}"
            )

            print(
                f"  Largeur   : {check.width}"
            )

            print(
                f"  Hauteur   : {check.height}"
            )

            print(
                f"  NoData    : {check.nodata}"
            )

            print(
                f"  Bandes    : {check.count}"
            )


        print()
        print(
            "✓ Découpage terminé."
        )

        print(
            "✓ Extérieur = NoData."
        )

        print(
            "✓ Masque de transparence créé."
        )

        return True


    except Exception as e:

        print()
        print(
            "❌ Erreur pendant le découpage :"
        )

        print(
            e
        )

        return False


# ================================================================
# 12. FONCTION DE SUPPRESSION
# ================================================================

def delete_file(
    path
):

    if os.path.exists(
        path
    ):

        try:

            os.remove(
                path
            )

            print(
                f"✓ Supprimé : "
                f"{os.path.basename(path)}"
            )

        except Exception as e:

            print(
                f"⚠ Impossible de supprimer "
                f"{path} : {e}"
            )


# ================================================================
# 13. INITIALISATION DE LA DATE
# ================================================================

year = START_YEAR
month = START_MONTH


# ================================================================
# 14. COMPTEURS
# ================================================================

downloaded_count = 0
skipped_count = 0
failed_count = 0


# ================================================================
# 15. BOUCLE AUTOMATIQUE
# ================================================================

while True:


    month_str = f"{month:02d}"


    # ============================================================
    # NOMS DES FICHIERS
    # ============================================================

    filename_gz = (
        f"chirps-v2.0."
        f"{year}."
        f"{month_str}.tif.gz"
    )


    filename_tif = (
        f"chirps-v2.0."
        f"{year}."
        f"{month_str}.tif"
    )


    # ============================================================
    # CHEMINS
    # ============================================================

    output_path = os.path.join(
        OUTPUT_DIR,
        filename_tif
    )


    temp_gz_path = os.path.join(
        TEMP_DIR,
        filename_gz
    )


    temp_tif_path = os.path.join(
        TEMP_DIR,
        filename_tif
    )


    # ============================================================
    # AFFICHAGE
    # ============================================================

    print()
    print()
    print("=" * 75)
    print(
        f"TRAITEMENT : {year}-{month_str}"
    )
    print("=" * 75)


    # ============================================================
    # 16. SI LE FICHIER FINAL EXISTE
    # ============================================================

    if os.path.exists(
        output_path
    ):

        print()
        print(
            f"✓ Déjà présent : {filename_tif}"
        )

        print(
            "→ Aucun téléchargement."
        )

        skipped_count += 1


    else:

        # ========================================================
        # URL
        # ========================================================

        url = (
            f"{BASE_URL}/"
            f"{filename_gz}"
        )


        print()
        print(
            f"URL : {url}"
        )


        # ========================================================
        # NETTOYAGE TEMPORAIRE
        # ========================================================

        delete_file(
            temp_gz_path
        )

        delete_file(
            temp_tif_path
        )


        # ========================================================
        # 17. TÉLÉCHARGEMENT
        # ========================================================

        result = download_file(
            url,
            temp_gz_path
        )


        # ========================================================
        # 18. SI LE FICHIER N'EXISTE PLUS
        # ========================================================

        if result == "NOT_FOUND":

            print()
            print("=" * 75)
            print(
                "DERNIER MOIS CHIRPS DISPONIBLE ATTEINT"
            )
            print("=" * 75)

            print()
            print(
                f"Le fichier suivant n'existe pas :"
            )

            print(
                filename_gz
            )

            print()
            print(
                "Le téléchargement s'arrête automatiquement."
            )

            break


        # ========================================================
        # 19. ERREUR DE TÉLÉCHARGEMENT
        # ========================================================

        if result is False:

            print()
            print(
                f"❌ Échec pour {year}-{month_str}"
            )

            failed_count += 1

            # ----------------------------------------------------
            # IMPORTANT :
            #
            # On n'arrête PAS le script.
            #
            # Une erreur réseau n'est pas considérée comme
            # la fin des données CHIRPS.
            # ----------------------------------------------------

        else:

            # ====================================================
            # 20. DÉCOMPRESSION
            # ====================================================

            success = decompress_gzip(
                temp_gz_path,
                temp_tif_path
            )


            if not success:

                delete_file(
                    temp_gz_path
                )

                failed_count += 1

            else:

                # =================================================
                # 21. SUPPRESSION DU .GZ
                # =================================================

                delete_file(
                    temp_gz_path
                )


                # =================================================
                # 22. DÉCOUPAGE
                # =================================================

                success = clip_raster(
                    temp_tif_path,
                    output_path,
                    zones
                )


                # =================================================
                # 23. SUPPRESSION DU TIFF MONDIAL
                # =================================================

                delete_file(
                    temp_tif_path
                )


                # =================================================
                # 24. VÉRIFICATION
                # =================================================

                if (
                    success
                    and
                    os.path.exists(
                        output_path
                    )
                ):

                    file_size = (
                        os.path.getsize(
                            output_path
                        )
                        /
                        (1024 * 1024)
                    )


                    print()
                    print(
                        f"✓ SUCCÈS : {filename_tif}"
                    )

                    print(
                        f"✓ Taille finale : "
                        f"{file_size:.2f} Mo"
                    )

                    downloaded_count += 1

                else:

                    print()
                    print(
                        f"❌ Échec du traitement "
                        f"{filename_tif}"
                    )

                    # --------------------------------------------
                    # Supprimer un fichier incomplet
                    # --------------------------------------------

                    delete_file(
                        output_path
                    )

                    failed_count += 1


        # ========================================================
        # PAUSE
        # ========================================================

        time.sleep(
            DOWNLOAD_DELAY
        )


    # ============================================================
    # 25. PASSAGE AU MOIS SUIVANT
    # ============================================================

    month += 1


    if month > 12:

        month = 1

        year += 1


# ================================================================
# 26. NETTOYAGE FINAL
# ================================================================

print()
print("=" * 75)
print("NETTOYAGE FINAL")
print("=" * 75)


# Supprimer d'éventuels fichiers temporaires

for filename in os.listdir(
    TEMP_DIR
):

    path = os.path.join(
        TEMP_DIR,
        filename
    )

    if os.path.isfile(
        path
    ):

        delete_file(
            path
        )


# Supprimer le dossier temporaire s'il est vide

try:

    if os.path.exists(
        TEMP_DIR
    ):

        if not os.listdir(
            TEMP_DIR
        ):

            os.rmdir(
                TEMP_DIR
            )

            print(
                "✓ Dossier temporaire supprimé."
            )

except Exception as e:

    print(
        f"⚠ Nettoyage impossible : {e}"
    )


# ================================================================
# 27. RÉSUMÉ FINAL
# ================================================================

print()
print()
print("=" * 75)
print("TÉLÉCHARGEMENT TERMINÉ")
print("=" * 75)

print()
print(
    f"✓ Nouveaux rasters téléchargés : "
    f"{downloaded_count}"
)

print(
    f"→ Rasters déjà présents ignorés : "
    f"{skipped_count}"
)

print(
    f"❌ Échecs : "
    f"{failed_count}"
)

print()
print(
    "Dossier de sortie :"
)

print(
    OUTPUT_DIR
)

print()
print("=" * 75)
print("FIN")
print("=" * 75)
