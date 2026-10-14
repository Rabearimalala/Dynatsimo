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
# 5. Détecte automatiquement le facteur d'échelle MODIS
# 6. Crée automatiquement 1 TIFF classifié par raster
# 7. Classe les pixels NDVI en 6 classes
# 8. Continue indéfiniment
#
# =============================================================
#
# CLASSES NDVI :
#
# 0 = NoData
# 1 = Eau              : NDVI < 0
# 2 = NDVI très faible : 0 <= NDVI <= 0.2
# 3 = NDVI faible      : 0.2 < NDVI <= 0.4
# 4 = NDVI moyen       : 0.4 < NDVI <= 0.6
# 5 = NDVI élevé       : 0.6 < NDVI <= 0.8
# 6 = NDVI très élevé  : 0.8 < NDVI <= 1
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

# -------------------------------------------------------------
# Dossier contenant les rasters NDVI
# -------------------------------------------------------------

INPUT_DIR = (
    r"C:\Users\Hanitriniala_RH"
    r"\Documents\Projet_test\dynatsimo-react\NDVI_MODIS"
)


# -------------------------------------------------------------
# Dossier des résultats
# -------------------------------------------------------------

OUTPUT_DIR = (
    r"C:\Users\Hanitriniala_RH"
    r"\Documents\Projet_test\dynatsimo-react\NDVI_MODIS"
    r"\RESULTATS_6_CLASSES"
)


# -------------------------------------------------------------
# Vérification toutes les 60 secondes
# -------------------------------------------------------------

CHECK_INTERVAL = 60


# -------------------------------------------------------------
# Temps d'attente pour vérifier si un fichier est stable
# -------------------------------------------------------------

STABILITY_WAIT = 10


# -------------------------------------------------------------
# Taille minimale en octets
# -------------------------------------------------------------
#
# Un fichier inférieur à cette taille est considéré comme
# potentiellement incomplet.
#
# -------------------------------------------------------------

MIN_FILE_SIZE = 1000


# =============================================================
# CRÉATION DU DOSSIER DES RÉSULTATS
# =============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# =============================================================
# COULEURS DES CLASSES
# =============================================================
#
# Les couleurs sont données au format RGBA :
#
# R, G, B, Alpha
#
# =============================================================

COLORMAP = {

    # ---------------------------------------------------------
    # 0 = NoData
    # ---------------------------------------------------------
    0: (0, 0, 0, 0),


    # ---------------------------------------------------------
    # 1 = Eau
    #
    # Couleur : #0c19ff
    # ---------------------------------------------------------
    1: (12, 25, 255, 255),


    # ---------------------------------------------------------
    # 2 = NDVI très faible
    #
    # Couleur : #87360c
    # ---------------------------------------------------------
    2: (135, 54, 12, 255),


    # ---------------------------------------------------------
    # 3 = NDVI faible
    #
    # Couleur : #c46e2d
    # ---------------------------------------------------------
    3: (196, 110, 45, 255),


    # ---------------------------------------------------------
    # 4 = NDVI moyen
    #
    # Couleur : #96aa50
    # ---------------------------------------------------------
    4: (150, 170, 80, 255),


    # ---------------------------------------------------------
    # 5 = NDVI élevé
    #
    # Couleur : #468237
    # ---------------------------------------------------------
    5: (70, 130, 55, 255),


    # ---------------------------------------------------------
    # 6 = NDVI très élevé
    #
    # Couleur : #00441b
    # ---------------------------------------------------------
    6: (0, 68, 27, 255)
}


# =============================================================
# EXTRACTION ANNÉE ET MOIS
# =============================================================

def get_year_month(filename):

    """
    Recherche une année et un mois dans le nom du fichier.

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

        year = int(
            match.group(1)
        )

        month = int(
            match.group(2)
        )

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

        # -----------------------------------------------------
        # Vérifier que le fichier existe
        # -----------------------------------------------------

        if not os.path.exists(filepath):

            return False


        # -----------------------------------------------------
        # Taille initiale
        # -----------------------------------------------------

        size_before = os.path.getsize(
            filepath
        )


        # -----------------------------------------------------
        # Fichier trop petit
        # -----------------------------------------------------

        if size_before < MIN_FILE_SIZE:

            return False


        # -----------------------------------------------------
        # Attendre
        # -----------------------------------------------------

        time.sleep(
            STABILITY_WAIT
        )


        # -----------------------------------------------------
        # Vérifier à nouveau l'existence
        # -----------------------------------------------------

        if not os.path.exists(filepath):

            return False


        # -----------------------------------------------------
        # Taille finale
        # -----------------------------------------------------

        size_after = os.path.getsize(
            filepath
        )


        # -----------------------------------------------------
        # Le fichier est stable si sa taille ne change pas
        # -----------------------------------------------------

        return size_before == size_after


    except Exception as e:

        print(
            f"⚠️ Impossible de vérifier le fichier : "
            f"{filepath}"
        )

        print(
            f"Erreur : {e}"
        )

        return False


# =============================================================
# RECHERCHE DES RASTERS
# =============================================================

def find_rasters():

    """
    Recherche tous les fichiers TIFF dans INPUT_DIR.

    Le dossier RESULTATS_6_CLASSES est automatiquement exclu
    afin d'éviter que les fichiers produits soient retraités.
    """

    raster_files = []


    for root, dirs, files in os.walk(
        INPUT_DIR
    ):

        # -----------------------------------------------------
        # Ne jamais parcourir le dossier des résultats
        # -----------------------------------------------------

        dirs[:] = [

            d for d in dirs

            if d != "RESULTATS_6_CLASSES"
        ]


        for file in files:

            # -------------------------------------------------
            # Chercher uniquement les TIFF
            # -------------------------------------------------

            if file.lower().endswith(
                (".tif", ".tiff")
            ):

                filepath = os.path.join(
                    root,
                    file
                )

                raster_files.append(
                    filepath
                )


    return sorted(
        raster_files
    )


# =============================================================
# CRÉATION DU CHEMIN DE SORTIE
# =============================================================

def get_output_file(input_file):

    """
    Détermine automatiquement le chemin du raster classifié.

    Exemple :

        NDVI_MODIS_2000_02.tif

    devient :

        RESULTATS_6_CLASSES/
            2000/
                NDVI_CLASS_2000_02.tif
    """

    filename = os.path.basename(
        input_file
    )


    year, month = get_year_month(
        filename
    )


    # =========================================================
    # SI ANNÉE ET MOIS SONT IDENTIFIÉS
    # =========================================================

    if year is not None:

        # -----------------------------------------------------
        # Créer un dossier par année
        # -----------------------------------------------------

        year_output_dir = os.path.join(

            OUTPUT_DIR,

            str(year)
        )


        os.makedirs(

            year_output_dir,

            exist_ok=True
        )


        # -----------------------------------------------------
        # Nom du fichier de sortie
        # -----------------------------------------------------

        output_name = (

            f"NDVI_CLASS_{year}_"
            f"{month:02d}.tif"
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

def classify_ndvi(
    input_file,
    output_file
):

    print(
        "\n" + "-" * 70
    )

    print(
        "TRAITEMENT : "
        f"{os.path.basename(input_file)}"
    )

    print(
        "-" * 70
    )


    # =========================================================
    # LECTURE DU RASTER
    # =========================================================

    try:

        with rasterio.open(
            input_file
        ) as src:

            # -------------------------------------------------
            # Lecture de la première bande
            # -------------------------------------------------

            ndvi = src.read(1).astype(
                np.float32
            )


            # -------------------------------------------------
            # Copier le profil du raster original
            # -------------------------------------------------

            profile = src.profile.copy()


            # -------------------------------------------------
            # Récupérer le NoData
            # -------------------------------------------------

            nodata = src.nodata


    except Exception as e:

        print(
            "\n❌ Impossible d'ouvrir le raster."
        )

        print(
            f"Erreur : {e}"
        )

        return False


    # =========================================================
    # INFORMATIONS SUR LE RASTER
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

    valid_mask = np.isfinite(
        ndvi
    )


    # ---------------------------------------------------------
    # Exclure le NoData
    # ---------------------------------------------------------

    if nodata is not None:

        valid_mask &= (
            ndvi != nodata
        )


    # =========================================================
    # VÉRIFICATION DES PIXELS
    # =========================================================

    valid_values = ndvi[
        valid_mask
    ]


    if len(valid_values) == 0:

        print(
            "❌ Aucun pixel valide trouvé."
        )

        return False


    # =========================================================
    # STATISTIQUES AVANT CONVERSION
    # =========================================================

    min_value = np.min(
        valid_values
    )

    max_value = np.max(
        valid_values
    )


    print(
        f"Valeur NDVI minimale "
        f"(avant conversion) : "
        f"{min_value}"
    )


    print(
        f"Valeur NDVI maximale "
        f"(avant conversion) : "
        f"{max_value}"
    )


    # =========================================================
    # DÉTECTION AUTOMATIQUE DU FACTEUR D'ÉCHELLE
    # =========================================================
    #
    # MODIS peut stocker le NDVI sous forme :
    #
    # NDVI réel × 10000
    #
    # Exemple :
    #
    # 7500 = 0.75
    # 2500 = 0.25
    # -1000 = -0.10
    #
    # =========================================================

    if max_value > 2:

        print(
            "\n⚠️ Facteur d'échelle détecté."
        )

        print(
            "Conversion automatique : "
            "NDVI = valeur / 10000"
        )


        ndvi[valid_mask] = (

            ndvi[valid_mask]

            / 10000.0
        )


    else:

        print(
            "\n✓ Aucun facteur d'échelle "
            "important détecté."
        )


    # =========================================================
    # NOUVELLES STATISTIQUES APRÈS CONVERSION
    # =========================================================

    valid_values = ndvi[
        valid_mask
    ]


    min_ndvi = np.min(
        valid_values
    )

    max_ndvi = np.max(
        valid_values
    )


    print(
        f"NDVI minimal après conversion : "
        f"{min_ndvi:.4f}"
    )


    print(
        f"NDVI maximal après conversion : "
        f"{max_ndvi:.4f}"
    )


    # =========================================================
    # CRÉATION DU RASTER CLASSIFIÉ
    # =========================================================

    classified = np.zeros(

        ndvi.shape,

        dtype=np.uint8
    )


    # =========================================================
    # CLASSE 1 : EAU
    #
    # NDVI < 0
    #
    # Couleur : #0c19ff
    # =========================================================

    mask_water = (

        valid_mask

        & (ndvi < 0)
    )


    classified[
        mask_water
    ] = 1


    # =========================================================
    # CLASSE 2 : NDVI TRÈS FAIBLE
    #
    # 0 <= NDVI <= 0.2
    #
    # Couleur : #87360c
    # =========================================================

    mask_class_2 = (

        valid_mask

        & (ndvi >= 0)

        & (ndvi <= 0.2)
    )


    classified[
        mask_class_2
    ] = 2


    # =========================================================
    # CLASSE 3 : NDVI FAIBLE
    #
    # 0.2 < NDVI <= 0.4
    #
    # Couleur : #c46e2d
    # =========================================================

    mask_class_3 = (

        valid_mask

        & (ndvi > 0.2)

        & (ndvi <= 0.4)
    )


    classified[
        mask_class_3
    ] = 3


    # =========================================================
    # CLASSE 4 : NDVI MOYEN
    #
    # 0.4 < NDVI <= 0.6
    #
    # Couleur : #96aa50
    # =========================================================

    mask_class_4 = (

        valid_mask

        & (ndvi > 0.4)

        & (ndvi <= 0.6)
    )


    classified[
        mask_class_4
    ] = 4


    # =========================================================
    # CLASSE 5 : NDVI ÉLEVÉ
    #
    # 0.6 < NDVI <= 0.8
    #
    # Couleur : #468237
    # =========================================================

    mask_class_5 = (

        valid_mask

        & (ndvi > 0.6)

        & (ndvi <= 0.8)
    )


    classified[
        mask_class_5
    ] = 5


    # =========================================================
    # CLASSE 6 : NDVI TRÈS ÉLEVÉ
    #
    # 0.8 < NDVI <= 1
    #
    # Couleur : #00441b
    # =========================================================

    mask_class_6 = (

        valid_mask

        & (ndvi > 0.8)

        & (ndvi <= 1.0)
    )


    classified[
        mask_class_6
    ] = 6


    # =========================================================
    # PIXELS HORS INTERVALLE
    # =========================================================
    #
    # Si un pixel valide possède une valeur :
    #
    # NDVI > 1
    #
    # il n'est affecté à aucune classe.
    #
    # Ces pixels restent donc à 0.
    #
    # =========================================================

    out_of_range_mask = (

        valid_mask

        & (
            (ndvi > 1.0)
        )
    )


    out_of_range_count = np.sum(
        out_of_range_mask
    )


    if out_of_range_count > 0:

        print(
            "\n⚠️ Pixels NDVI > 1 détectés : "
            f"{out_of_range_count:,}"
        )


    # =========================================================
    # STATISTIQUES
    # =========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "RÉPARTITION DES 6 CLASSES"
    )

    print(
        "=" * 70
    )


    # ---------------------------------------------------------
    # Nombre total de pixels classifiés
    # ---------------------------------------------------------

    valid_classified = np.sum(

        classified > 0
    )


    # =========================================================
    # AFFICHAGE DES CLASSES
    # =========================================================

    class_names = {

        1: "Eau",

        2: "NDVI très faible",

        3: "NDVI faible",

        4: "NDVI moyen",

        5: "NDVI élevé",

        6: "NDVI très élevé"
    }


    for classe in range(
        1,
        7
    ):

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

            f"{class_names[classe]} "

            f"→ {count:,} pixels "

            f"({percentage:.2f}%)"
        )


    # =========================================================
    # PIXELS NODATA
    # =========================================================

    nodata_count = np.sum(

        classified == 0
    )


    print(
        "\nNoData / non classés : "
        f"{nodata_count:,} pixels"
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

        # -----------------------------------------------------
        # Créer le dossier parent si nécessaire
        # -----------------------------------------------------

        os.makedirs(

            os.path.dirname(
                output_file
            ),

            exist_ok=True
        )


        # -----------------------------------------------------
        # Écriture du raster
        # -----------------------------------------------------

        with rasterio.open(

            output_file,

            "w",

            **profile

        ) as dst:


            # -------------------------------------------------
            # Écriture des classes
            # -------------------------------------------------

            dst.write(

                classified,

                1
            )


            # -------------------------------------------------
            # Palette de couleurs
            # -------------------------------------------------

            dst.write_colormap(

                1,

                COLORMAP
            )


            # -------------------------------------------------
            # Métadonnées
            # -------------------------------------------------

            dst.update_tags(

                classification=(
                    "NDVI 6 classes"
                ),

                class_0=(
                    "NoData"
                ),

                class_1=(
                    "NDVI < 0 : Eau"
                ),

                class_2=(
                    "0 <= NDVI <= 0.2 : "
                    "NDVI très faible"
                ),

                class_3=(
                    "0.2 < NDVI <= 0.4 : "
                    "NDVI faible"
                ),

                class_4=(
                    "0.4 < NDVI <= 0.6 : "
                    "NDVI moyen"
                ),

                class_5=(
                    "0.6 < NDVI <= 0.8 : "
                    "NDVI élevé"
                ),

                class_6=(
                    "0.8 < NDVI <= 1.0 : "
                    "NDVI très élevé"
                ),

                source=(
                    "NDVI MODIS"
                ),

                scale_factor=(
                    "Conversion automatique "
                    "si nécessaire : /10000"
                )
            )


    except Exception as e:

        print(
            "\n❌ Erreur lors de l'écriture : "
            f"{e}"
        )

        return False


    # =========================================================
    # SUCCÈS
    # =========================================================

    print(
        "\n✅ RASTER CLASSIFIÉ "
        "CRÉÉ AVEC SUCCÈS"
    )


    print(
        f"📁 {output_file}"
    )


    return True


# =============================================================
# PROGRAMME PRINCIPAL
# =============================================================
#
# SURVEILLANCE AUTOMATIQUE
#
# =============================================================

print(
    "\n" + "=" * 70
)


print(
    "SURVEILLANCE AUTOMATIQUE "
    "DES RASTERS NDVI"
)


print(
    "=" * 70
)


print(
    "\n📁 Dossier surveillé :"
)


print(
    INPUT_DIR
)


print(
    "\n📁 Résultats :"
)


print(
    OUTPUT_DIR
)


print(
    "\n📊 Classification : 6 classes"
)


print(
    "🌊 Classe 1 : Eau (NDVI < 0)"
)


print(
    "🌱 Classes 2 à 6 : végétation"
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

        print(
            "\n" + "=" * 70
        )


        print(
            "RECHERCHE DE NOUVEAUX RASTERS..."
        )


        print(
            "=" * 70
        )


        # =====================================================
        # RECHERCHER TOUS LES TIFF
        # =====================================================

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

            if not is_file_stable(
                input_file
            ):

                print(

                    "\n⏳ Fichier ignoré "
                    "temporairement "
                    "(vide ou en cours "
                    "d'écriture) : "

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

            if os.path.exists(
                output_file
            ):

                print(

                    f"✓ Déjà traité : "
                    f"{filename}"
                )

                continue


            # -------------------------------------------------
            # Nouveau fichier
            # -------------------------------------------------

            print(

                "\n🆕 NOUVEAU RASTER "
                "DÉTECTÉ : "

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

                    "\n✅ TERMINÉ : "
                    f"{filename}"
                )


            else:

                print(

                    "\n❌ ÉCHEC : "
                    f"{filename}"
                )


        # =====================================================
        # RÉSUMÉ
        # =====================================================

        if new_count == 0:

            print(
                "\n✓ Aucun nouveau "
                "raster à traiter."
            )


        else:

            print(

                f"\n🎉 {new_count} nouveau(x) "
                "raster(s) détecté(s) "
                "et traité(s)."
            )


        # =====================================================
        # ATTENTE
        # =====================================================

        print(

            f"\n⏳ Nouvelle vérification "
            f"dans {CHECK_INTERVAL} "
            "secondes..."
        )


        time.sleep(
            CHECK_INTERVAL
        )


# =============================================================
# ARRÊT MANUEL
# =============================================================

except KeyboardInterrupt:

    print(
        "\n"
    )


    print(
        "=" * 70
    )


    print(
        "🛑 SURVEILLANCE ARRÊTÉE "
        "PAR L'UTILISATEUR"
    )


    print(
        "=" * 70
    )


    print(
        "\nLe programme est terminé."
    )