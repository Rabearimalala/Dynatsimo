# =============================================================
# SURVEILLANCE AUTOMATIQUE ET CLASSIFICATION NDVI
# =============================================================
#
# Le script :
#
# 1. Surveille automatiquement le dossier NDVI_MODIS
# 2. Détecte les nouveaux fichiers TIFF
# 3. Attend que le fichier soit complètement créé
# 4. Ignore les fichiers vides ou incomplets
# 5. Crée automatiquement 1 TIFF classifié par raster
# 6. Continue indéfiniment
#
# CLASSES NDVI :
#
# 0 = NoData
# 1 = NDVI très faible     : 0 < NDVI <= 0.2
# 2 = NDVI faible          : 0.2 < NDVI <= 0.4
# 3 = NDVI moyen           : 0.4 < NDVI <= 0.6
# 4 = NDVI élevé           : 0.6 < NDVI <= 0.8
# 5 = NDVI très élevé      : 0.8 < NDVI <= 1
#
# =============================================================

import os
import re
import time
import numpy as np
import rasterio


# =============================================================
# PARAMÈTRES
# =============================================================

# Dossier contenant les rasters NDVI
INPUT_DIR = r"C:\Users\Hanitriniala_RH\Documents\Projet_test\dynatsimo-react\NDVI_MODIS"


# Dossier des résultats
OUTPUT_DIR = (
    r"C:\Users\Hanitriniala_RH\Documents"
    r"\Projet_test\dynatsimo-react\NDVI_MODIS\RESULTATS_5_CLASSES"
)


# Vérification toutes les 60 secondes
CHECK_INTERVAL = 60


# Temps d'attente pour vérifier si un fichier est stable
STABILITY_WAIT = 10


# Taille minimale en octets
# Un fichier de 0 octet sera automatiquement ignoré
MIN_FILE_SIZE = 1000


# Création du dossier des résultats
os.makedirs(OUTPUT_DIR, exist_ok=True)


# =============================================================
# COULEURS DES CLASSES
# =============================================================

COLORMAP = {

    # 0 = NoData
    0: (0, 0, 0, 0),

    # 1 = NDVI très faible
    # #87360c
    1: (135, 54, 12, 255),

    # 2 = NDVI faible
    2: (196, 110, 45, 255),

    # 3 = NDVI moyen
    3: (150, 170, 80, 255),

    # 4 = NDVI élevé
    4: (70, 130, 55, 255),

    # 5 = NDVI très élevé
    # #00441b
    5: (0, 68, 27, 255)
}


# =============================================================
# EXTRACTION ANNÉE ET MOIS
# =============================================================

def get_year_month(filename):

    """
    Exemple :

    NDVI_MODIS_2000_02.tif

    Retourne :

    2000, 2
    """

    match = re.search(
        r"(20\d{2})_(0[1-9]|1[0-2])",
        filename
    )

    if match:

        year = int(match.group(1))
        month = int(match.group(2))

        return year, month

    return None, None


# =============================================================
# VÉRIFICATION DE LA STABILITÉ DU FICHIER
# =============================================================

def is_file_stable(filepath):

    """
    Vérifie que :

    - le fichier existe ;
    - sa taille est suffisante ;
    - sa taille ne change pas pendant STABILITY_WAIT secondes.

    Cela évite de traiter un fichier pendant son téléchargement
    ou pendant son export.
    """

    try:

        if not os.path.exists(filepath):

            return False


        size_before = os.path.getsize(filepath)


        # Fichier trop petit ou vide
        if size_before < MIN_FILE_SIZE:

            return False


        # Attendre
        time.sleep(STABILITY_WAIT)


        if not os.path.exists(filepath):

            return False


        size_after = os.path.getsize(filepath)


        # Le fichier est stable si sa taille ne change pas
        return size_before == size_after


    except Exception as e:

        print(
            f"⚠️ Impossible de vérifier le fichier : {filepath}"
        )

        print(f"Erreur : {e}")

        return False


# =============================================================
# RECHERCHE DES RASTERS
# =============================================================

def find_rasters():

    raster_files = []


    for root, dirs, files in os.walk(INPUT_DIR):


        # Ne jamais parcourir le dossier des résultats
        dirs[:] = [

            d for d in dirs

            if d != "RESULTATS_5_CLASSES"

        ]


        for file in files:


            # Chercher uniquement TIFF
            if file.lower().endswith((".tif", ".tiff")):


                filepath = os.path.join(
                    root,
                    file
                )


                raster_files.append(filepath)


    return sorted(raster_files)


# =============================================================
# CRÉATION DU CHEMIN DE SORTIE
# =============================================================

def get_output_file(input_file):

    filename = os.path.basename(input_file)


    year, month = get_year_month(filename)


    # =========================================================
    # SI ANNÉE ET MOIS SONT IDENTIFIÉS
    # =========================================================

    if year is not None:


        # Créer un dossier par année
        year_output_dir = os.path.join(

            OUTPUT_DIR,

            str(year)

        )


        os.makedirs(

            year_output_dir,

            exist_ok=True

        )


        # Exemple :
        #
        # NDVI_CLASS_2000_02.tif

        output_name = (
            f"NDVI_CLASS_{year}_{month:02d}.tif"
        )


        return os.path.join(

            year_output_dir,

            output_name

        )


    # =========================================================
    # SI ANNÉE / MOIS NON RECONNUS
    # =========================================================

    output_name = (
        "CLASSIFIED_"
        + filename
    )


    return os.path.join(

        OUTPUT_DIR,

        output_name

    )


# =============================================================
# CLASSIFICATION DU NDVI
# =============================================================

def classify_ndvi(input_file, output_file):

    print("\n" + "-" * 70)

    print(
        f"TRAITEMENT : "
        f"{os.path.basename(input_file)}"
    )

    print("-" * 70)


    try:

        # =====================================================
        # LECTURE DU RASTER
        # =====================================================

        with rasterio.open(input_file) as src:


            ndvi = src.read(1).astype(
                np.float32
            )


            profile = src.profile.copy()


            nodata = src.nodata


    except Exception as e:


        print("\n❌ Impossible d'ouvrir le raster.")

        print(f"Erreur : {e}")

        return False


    # =========================================================
    # INFORMATIONS
    # =========================================================

    print(
        f"Dimensions : "
        f"{ndvi.shape[1]} x {ndvi.shape[0]}"
    )


    print(
        f"NoData original : "
        f"{nodata}"
    )


    # =========================================================
    # MASQUE DES PIXELS VALIDES
    # =========================================================

    valid_mask = np.isfinite(ndvi)


    # Exclure le NoData
    if nodata is not None:

        valid_mask &= (
            ndvi != nodata
        )


    # =========================================================
    # VÉRIFICATION DES PIXELS
    # =========================================================

    valid_values = ndvi[valid_mask]


    if len(valid_values) == 0:


        print(
            "❌ Aucun pixel valide trouvé."
        )


        return False


    # =========================================================
    # DÉTECTION AUTOMATIQUE DU FACTEUR D'ÉCHELLE
    # =========================================================

    max_value = np.max(valid_values)


    print(
        f"Valeur NDVI minimale : "
        f"{np.min(valid_values)}"
    )


    print(
        f"Valeur NDVI maximale : "
        f"{max_value}"
    )


    # Si les valeurs ressemblent à du NDVI MODIS × 10000
    if max_value > 2:


        print(
            "\n⚠️ Facteur d'échelle détecté."
        )


        print(
            "Conversion automatique : "
            "NDVI = valeur / 10000"
        )


        ndvi[valid_mask] = (
            ndvi[valid_mask] / 10000.0
        )


    # =========================================================
    # CRÉATION DU RASTER CLASSIFIÉ
    # =========================================================

    classified = np.zeros(

        ndvi.shape,

        dtype=np.uint8

    )


    # =========================================================
    # CLASSE 1
    #
    # NDVI très faible
    # 0 < NDVI <= 0.2
    # =========================================================

    mask_class_1 = (

        valid_mask

        & (ndvi > 0)

        & (ndvi <= 0.2)

    )


    classified[mask_class_1] = 1


    # =========================================================
    # CLASSE 2
    #
    # NDVI faible
    # 0.2 < NDVI <= 0.4
    # =========================================================

    mask_class_2 = (

        valid_mask

        & (ndvi > 0.2)

        & (ndvi <= 0.4)

    )


    classified[mask_class_2] = 2


    # =========================================================
    # CLASSE 3
    #
    # NDVI moyen
    # 0.4 < NDVI <= 0.6
    # =========================================================

    mask_class_3 = (

        valid_mask

        & (ndvi > 0.4)

        & (ndvi <= 0.6)

    )


    classified[mask_class_3] = 3


    # =========================================================
    # CLASSE 4
    #
    # NDVI élevé
    # 0.6 < NDVI <= 0.8
    # =========================================================

    mask_class_4 = (

        valid_mask

        & (ndvi > 0.6)

        & (ndvi <= 0.8)

    )


    classified[mask_class_4] = 4


    # =========================================================
    # CLASSE 5
    #
    # NDVI très élevé
    # 0.8 < NDVI <= 1
    # =========================================================

    mask_class_5 = (

        valid_mask

        & (ndvi > 0.8)

        & (ndvi <= 1.0)

    )


    classified[mask_class_5] = 5


    # =========================================================
    # STATISTIQUES
    # =========================================================

    print("\nRÉPARTITION DES CLASSES")


    valid_classified = np.sum(
        classified > 0
    )


    for classe in range(1, 6):


        count = np.sum(
            classified == classe
        )


        if valid_classified > 0:

            percentage = (
                count
                / valid_classified
                * 100
            )

        else:

            percentage = 0


        print(

            f"Classe {classe} : "
            f"{count:,} pixels "
            f"({percentage:.2f}%)"

        )


    # =========================================================
    # VÉRIFICATION DES VALEURS FINALES
    # =========================================================

    unique_values = np.unique(
        classified
    )


    print(
        "\nValeurs finales présentes : "
        f"{unique_values}"
    )


    # =========================================================
    # CONFIGURATION DU TIFF DE SORTIE
    # =========================================================

    profile.update(

        dtype=rasterio.uint8,

        count=1,

        nodata=0,

        compress="lzw"

    )


    # =========================================================
    # ÉCRITURE DU RÉSULTAT
    # =========================================================

    try:


        with rasterio.open(

            output_file,

            "w",

            **profile

        ) as dst:


            # Écriture des classes
            dst.write(

                classified,

                1

            )


            # Palette de couleurs
            dst.write_colormap(

                1,

                COLORMAP

            )


            # Métadonnées
            dst.update_tags(

                classification="NDVI 5 classes",

                class_1="0 < NDVI <= 0.2 : NDVI très faible",

                class_2="0.2 < NDVI <= 0.4 : NDVI faible",

                class_3="0.4 < NDVI <= 0.6 : NDVI moyen",

                class_4="0.6 < NDVI <= 0.8 : NDVI élevé",

                class_5="0.8 < NDVI <= 1.0 : NDVI très élevé"

            )


    except Exception as e:


        print(
            f"\n❌ Erreur lors de l'écriture : {e}"
        )


        return False


    print(
        "\n✅ RASTER CLASSIFIÉ CRÉÉ AVEC SUCCÈS"
    )


    print(output_file)


    return True


# =============================================================
# PROGRAMME PRINCIPAL :
# SURVEILLANCE AUTOMATIQUE
# =============================================================

print("\n" + "=" * 70)

print(
    "SURVEILLANCE AUTOMATIQUE DES RASTERS NDVI"
)

print("=" * 70)


print(f"\n📁 Dossier surveillé :\n{INPUT_DIR}")

print(
    f"\n📁 Résultats :\n{OUTPUT_DIR}"
)

print(
    f"\n⏱️ Vérification toutes les "
    f"{CHECK_INTERVAL} secondes."
)

print(
    "\n👀 Le programme reste actif."
)

print(
    "🛑 Appuyez sur Ctrl + C pour arrêter."
)


# =============================================================
# BOUCLE INFINIE
# =============================================================

try:


    while True:


        print("\n" + "=" * 70)

        print(
            "RECHERCHE DE NOUVEAUX RASTERS..."
        )

        print("=" * 70)


        # Rechercher tous les TIFF
        raster_files = find_rasters()


        print(
            f"\nNombre de fichiers trouvés : "
            f"{len(raster_files)}"
        )


        new_count = 0


        # =====================================================
        # ANALYSE DE CHAQUE RASTER
        # =====================================================

        for input_file in raster_files:


            filename = os.path.basename(
                input_file
            )


            # -------------------------------------------------
            # Vérifier si le fichier est stable
            # -------------------------------------------------

            if not is_file_stable(input_file):


                print(

                    f"\n⏳ Fichier ignoré temporairement "
                    f"(vide ou en cours d'écriture) : "
                    f"{filename}"

                )


                continue


            # -------------------------------------------------
            # Déterminer le fichier résultat
            # -------------------------------------------------

            output_file = get_output_file(
                input_file
            )


            # -------------------------------------------------
            # Si le résultat existe déjà :
            # ne pas retraiter
            # -------------------------------------------------

            if os.path.exists(output_file):


                print(

                    f"✓ Déjà traité : {filename}"

                )


                continue


            # -------------------------------------------------
            # Nouveau fichier
            # -------------------------------------------------

            print(

                f"\n🆕 NOUVEAU RASTER DÉTECTÉ : "
                f"{filename}"

            )


            new_count += 1


            # -------------------------------------------------
            # CLASSIFICATION
            # -------------------------------------------------

            result = classify_ndvi(

                input_file,

                output_file

            )


            if result:


                print(

                    f"\n✅ TERMINÉ : {filename}"

                )


            else:


                print(

                    f"\n❌ ÉCHEC : {filename}"

                )


        # =====================================================
        # RÉSUMÉ
        # =====================================================

        if new_count == 0:


            print(

                "\n✓ Aucun nouveau raster à traiter."

            )


        else:


            print(

                f"\n🎉 {new_count} nouveau(x) "
                f"raster(s) détecté(s) et traité(s)."

            )


        # =====================================================
        # ATTENTE
        # =====================================================

        print(

            f"\n⏳ Nouvelle vérification dans "
            f"{CHECK_INTERVAL} secondes..."

        )


        time.sleep(
            CHECK_INTERVAL
        )


# =============================================================
# ARRÊT MANUEL
# =============================================================

except KeyboardInterrupt:


    print("\n")

    print("=" * 70)

    print(
        "🛑 SURVEILLANCE ARRÊTÉE PAR L'UTILISATEUR"
    )

    print("=" * 70)

    print(
        "\nLe programme est terminé."
    )