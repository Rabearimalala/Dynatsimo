# ================================================================
# 1. IMPORTATIONS
# ================================================================

import os
import re

import numpy as np
import rasterio


# ================================================================
# 2. CONFIGURATION
# ================================================================

# ------------------------------------------------
# Dossier principal du projet
# ------------------------------------------------

PROJECT_DIR = (
    r"C:\Users\Hanitriniala_RH\Documents"
    r"\Dynatsimo\dynatsimo-react"
)


# ------------------------------------------------
# Dossier contenant les rasters CHIRPS
# ------------------------------------------------

CHIRPS_DIR = os.path.join(
    PROJECT_DIR,
    "CHIRPS_data"
)


# ------------------------------------------------
# Dossier de sortie
# ------------------------------------------------

OUTPUT_DIR = os.path.join(
    CHIRPS_DIR,
    "isohyetes"
)


# ------------------------------------------------
# Intervalle entre les isohyètes
# ------------------------------------------------
#
# Exemple :
# 10 = 10, 20, 30, 40...
#
# ------------------------------------------------

CONTOUR_INTERVAL = 10.0


# ------------------------------------------------
# Valeur NoData
# ------------------------------------------------

NODATA_VALUE = -9999.0


# ------------------------------------------------
# Type de données du GeoTIFF
# ------------------------------------------------

OUTPUT_DTYPE = "float32"


# ================================================================
# 3. CRÉATION DU DOSSIER
# ================================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ================================================================
# 4. AFFICHAGE
# ================================================================

print()
print("=" * 75)
print("CHIRPS → ISOHYÈTES → GEOTIFF")
print("=" * 75)

print()
print("Dossier des rasters :")
print(CHIRPS_DIR)

print()
print("Dossier de sortie :")
print(OUTPUT_DIR)

print()
print(
    f"Intervalle des isohyètes : "
    f"{CONTOUR_INTERVAL:g} mm"
)

print()
print("Shapefile : NON UTILISÉ")

print("=" * 75)


# ================================================================
# 5. VÉRIFICATION DU DOSSIER
# ================================================================

if not os.path.exists(CHIRPS_DIR):

    raise FileNotFoundError(
        "\n❌ Dossier CHIRPS introuvable :\n"
        f"{CHIRPS_DIR}"
    )


# ================================================================
# 6. RECHERCHE DES RASTERS
# ================================================================

print()
print("=" * 75)
print("RECHERCHE DES RASTERS CHIRPS")
print("=" * 75)


pattern = re.compile(
    r"^chirps-v2\.0\.(\d{4})\.(\d{2})\.tif$",
    re.IGNORECASE
)


raster_files = []


for filename in os.listdir(CHIRPS_DIR):

    match = pattern.match(
        filename
    )

    if not match:
        continue


    year = int(
        match.group(1)
    )

    month = int(
        match.group(2)
    )


    if not 1 <= month <= 12:
        continue


    path = os.path.join(
        CHIRPS_DIR,
        filename
    )


    if os.path.isfile(path):

        raster_files.append(
            (
                year,
                month,
                path
            )
        )


# ================================================================
# 7. TRI CHRONOLOGIQUE
# ================================================================

raster_files.sort(
    key=lambda x: (
        x[0],
        x[1]
    )
)


print()

print(
    f"✓ Nombre de rasters trouvés : "
    f"{len(raster_files)}"
)


if not raster_files:

    raise RuntimeError(
        "\n❌ Aucun raster CHIRPS trouvé."
    )


# ================================================================
# 8. AFFICHAGE DES PREMIERS RASTERS
# ================================================================

print()
print("Rasters détectés :")


for year, month, path in raster_files[:10]:

    print(
        f"  ✓ {year}-{month:02d} → "
        f"{os.path.basename(path)}"
    )


if len(raster_files) > 10:

    print(
        f"  ... et "
        f"{len(raster_files) - 10} autre(s)"
    )


# ================================================================
# 9. FONCTION DE CRÉATION DU GEOTIFF ISOHYÈTES
# ================================================================

def create_isohyete_raster(
    input_path,
    output_path,
    year,
    month
):

    """
    Transforme un raster CHIRPS mensuel en raster
    d'isohyètes.

    Chaque pixel reçoit le niveau d'isohyète
    correspondant à sa valeur de précipitation.

    Exemple avec un intervalle de 10 mm :

        17 mm  → 20 mm
        24 mm  → 20 mm
        27 mm  → 30 mm
        43 mm  → 40 mm
        108 mm → 110 mm

    NoData reste NoData.
    """

    print()
    print()
    print("=" * 75)

    print(
        f"TRAITEMENT : {year}-{month:02d}"
    )

    print("=" * 75)


    # ============================================================
    # SI LE FICHIER EXISTE
    # ============================================================

    if os.path.exists(
        output_path
    ):

        print()
        print(
            "✓ GeoTIFF déjà présent."
        )

        print(
            f"→ {os.path.basename(output_path)}"
        )

        print(
            "→ Traitement ignoré."
        )

        return "SKIPPED"


    # ============================================================
    # OUVERTURE DU RASTER
    # ============================================================

    try:

        with rasterio.open(
            input_path
        ) as src:

            # ====================================================
            # INFORMATIONS
            # ====================================================

            print()

            print(
                f"CRS        : {src.crs}"
            )

            print(
                f"Largeur    : {src.width}"
            )

            print(
                f"Hauteur    : {src.height}"
            )

            print(
                f"Résolution : {src.res}"
            )

            print(
                f"NoData     : {src.nodata}"
            )


            # ====================================================
            # LECTURE
            # ====================================================

            print()

            print(
                "Lecture du raster..."
            )


            data = src.read(
                1
            ).astype(
                np.float32
            )


            # ====================================================
            # DÉTERMINATION DU NODATA
            # ====================================================

            source_nodata = src.nodata


            if source_nodata is None:

                source_nodata = NODATA_VALUE


            # ====================================================
            # MASQUE DES PIXELS VALIDES
            # ====================================================

            valid = np.isfinite(
                data
            )


            valid &= (
                data != source_nodata
            )


            valid &= (
                data != NODATA_VALUE
            )


            # ====================================================
            # VÉRIFICATION
            # ====================================================

            if not np.any(valid):

                print()

                print(
                    "❌ Aucun pixel valide."
                )

                return False


            # ====================================================
            # STATISTIQUES
            # ====================================================

            values = data[
                valid
            ]


            minimum = float(
                np.min(values)
            )

            maximum = float(
                np.max(values)
            )

            moyenne = float(
                np.mean(values)
            )


            print()

            print(
                f"Précipitation minimale : "
                f"{minimum:.2f} mm"
            )

            print(
                f"Précipitation maximale : "
                f"{maximum:.2f} mm"
            )

            print(
                f"Précipitation moyenne   : "
                f"{moyenne:.2f} mm"
            )


            # ====================================================
            # CALCUL DES NIVEAUX
            # ====================================================
            #
            # Exemple :
            #
            # minimum = 17.7
            # maximum = 216.8
            #
            # niveaux :
            #
            # 20
            # 30
            # ...
            # 220
            #
            # ====================================================

            isohyete_data = np.full(
                data.shape,
                NODATA_VALUE,
                dtype=np.float32
            )


            # ====================================================
            # ARRONDI AU NIVEAU D'ISOHYÈTE SUPÉRIEUR
            # ====================================================
            #
            # Exemple :
            #
            # 17.7 → 20
            # 23.1 → 30
            # 46.8 → 50
            #
            # ====================================================

            isohyete_values = (
                np.ceil(
                    values /
                    CONTOUR_INTERVAL
                )
                *
                CONTOUR_INTERVAL
            )


            # ====================================================
            # ÉCRITURE DES VALEURS
            # ====================================================

            isohyete_data[
                valid
            ] = isohyete_values


            # ====================================================
            # VALEURS MIN/MAX DES ISOHYÈTES
            # ====================================================

            iso_min = float(
                np.min(
                    isohyete_values
                )
            )

            iso_max = float(
                np.max(
                    isohyete_values
                )
            )


            print()

            print(
                f"Intervalle : "
                f"{CONTOUR_INTERVAL:g} mm"
            )

            print(
                f"Isohyète minimale : "
                f"{iso_min:g} mm"
            )

            print(
                f"Isohyète maximale : "
                f"{iso_max:g} mm"
            )


            # ====================================================
            # PROFIL DU GEOTIFF
            # ====================================================

            profile = src.profile.copy()


            profile.update({

                "driver":
                    "GTiff",

                "dtype":
                    OUTPUT_DTYPE,

                "count":
                    1,

                "nodata":
                    NODATA_VALUE,

                "compress":
                    "deflate",

                "predictor":
                    2,

                "tiled":
                    True

            })


            # ====================================================
            # ÉCRITURE
            # ====================================================

            print()

            print(
                "Création du GeoTIFF..."
            )


            with rasterio.open(
                output_path,
                "w",
                **profile
            ) as dst:

                dst.write(
                    isohyete_data,
                    1
                )


                # =================================================
                # MASQUE DE TRANSPARENCE
                # =================================================

                mask_data = np.where(
                    valid,
                    255,
                    0
                ).astype(
                    np.uint8
                )


                dst.write_mask(
                    mask_data
                )


                # =================================================
                # MÉTADONNÉES
                # =================================================

                dst.update_tags(

                    YEAR=year,

                    MONTH=month,

                    DATA_SOURCE="CHIRPS",

                    PRODUCT="Isohyetes",

                    INTERVAL_MM=(
                        CONTOUR_INTERVAL
                    ),

                    MIN_PRECIP_MM=(
                        minimum
                    ),

                    MAX_PRECIP_MM=(
                        maximum
                    ),

                    MEAN_PRECIP_MM=(
                        moyenne
                    )
                )


    except Exception as e:

        print()

        print(
            "❌ Erreur :"
        )

        print(
            str(e)
        )

        return False


    # ============================================================
    # VÉRIFICATION
    # ============================================================

    try:

        with rasterio.open(
            output_path
        ) as check:

            print()

            print(
                "Vérification du GeoTIFF..."
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
                f"  Résolution: {check.res}"
            )

            print(
                f"  NoData    : {check.nodata}"
            )

            print(
                f"  Type      : {check.dtypes[0]}"
            )


    except Exception as e:

        print()

        print(
            "⚠ Vérification impossible :"
        )

        print(
            e
        )


    # ============================================================
    # TAILLE
    # ============================================================

    file_size = (
        os.path.getsize(
            output_path
        )
        /
        (
            1024 *
            1024
        )
    )


    # ============================================================
    # SUCCÈS
    # ============================================================

    print()

    print("=" * 75)

    print(
        "✓ ISOHYÈTES GEOTIFF CRÉÉES"
    )

    print("=" * 75)

    print()

    print(
        f"Date       : "
        f"{year}-{month:02d}"
    )

    print(
        f"Intervalle : "
        f"{CONTOUR_INTERVAL:g} mm"
    )

    print(
        f"Taille     : "
        f"{file_size:.2f} Mo"
    )

    print()

    print(
        "Fichier :"
    )

    print(
        output_path
    )

    print()

    return True


# ================================================================
# 10. TRAITEMENT DE TOUS LES RASTERS
# ================================================================

processed_count = 0
skipped_count = 0
failed_count = 0


print()
print()
print("=" * 75)

print(
    "DÉBUT DE LA CRÉATION DES GEOTIFF ISOHYÈTES"
)

print("=" * 75)


for year, month, raster_path in raster_files:


    output_filename = (
        f"isohyetes_"
        f"{year}_"
        f"{month:02d}.tif"
    )


    output_path = os.path.join(
        OUTPUT_DIR,
        output_filename
    )


    result = create_isohyete_raster(
        raster_path,
        output_path,
        year,
        month
    )


    if result is True:

        processed_count += 1


    elif result == "SKIPPED":

        skipped_count += 1


    else:

        failed_count += 1


# ================================================================
# 11. RÉSUMÉ
# ================================================================

print()
print()
print("=" * 75)

print(
    "TRAITEMENT TERMINÉ"
)

print("=" * 75)

print()

print(
    f"✓ GeoTIFF créés : "
    f"{processed_count}"
)

print(
    f"→ Déjà présents : "
    f"{skipped_count}"
)

print(
    f"❌ Échecs       : "
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