# -*- coding: utf-8 -*-
"""
Générateur de diagrammes haute résolution pour les chaînes de traitement DYNATSIMO
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def create_figure_abstraite(output_path):
    fig = plt.figure(figsize=(14, 11), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    # Fond
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    # Titre du diagramme
    ax.text(50, 96.5, "CHAÎNE DE TRAITEMENT ABSTRAITE (NIVEAU CONCEPTUEL)",
            ha='center', va='center', fontsize=16, fontweight='bold', color='#0F4C81',
            fontfamily='sans-serif')
    ax.text(50, 93.8, "Flux Logique & Méthodologique de Transformation des Données Géospatiales",
            ha='center', va='center', fontsize=11, fontstyle='italic', color='#0D9488',
            fontfamily='sans-serif')

    # Ligne de séparation
    ax.plot([10, 90], [91.5, 91.5], color='#CBD5E1', lw=1.5)

    boxes_data = [
        {
            "num": "1",
            "title": "ACQUISITION & TÉLÉDÉTECTION MULTI-SOURCES",
            "icon": "📡",
            "y": 79,
            "bg": "#EFF6FF",
            "border": "#2563EB",
            "items": [
                "• Réflectances optiques multispectrales (Bandes Rouge & Proche Infrarouge PIR)",
                "• Estimations pluviométriques satellitaires (Infrarouge thermique & Réanalyses)",
                "• Référentiel vectoriel des limites administratives (Communes, Districts, Régions)"
            ],
            "in_out": "Entrées : Signaux bruts capteurs  ➔  Sortie : Matrices brutes géoréférencées"
        },
        {
            "num": "2",
            "title": "PRÉTRAITEMENT & HARMONISATION SPATIO-TEMPORELLE",
            "icon": "🧹",
            "y": 62,
            "bg": "#F0FDF4",
            "border": "#16A34A",
            "items": [
                "• Découpage spatial strict sur l'Aire d'Intérêt (AOI Grand Sud de Madagascar)",
                "• Masquage des artéfacts atmosphériques (Nuages, ombres et cirrus via masques QA)",
                "• Reprojection cartographique uniforme (WGS84 EPSG:4326) et normalisation mensuelle"
            ],
            "in_out": "Entrées : Rasters bruts  ➔  Sortie : Rasters corrigés et normalisés par mois"
        },
        {
            "num": "3",
            "title": "CALCUL DES INDICES BIOCLIMATIQUES & STATISTIQUES ZONALES",
            "icon": "🧮",
            "y": 45,
            "bg": "#FEFCE8",
            "border": "#CA8A04",
            "items": [
                "• Indice de végétation : NDVI = (PIR - Rouge) / (PIR + Rouge) & Santé végétale (VCI, VHI)",
                "• Climatologie de référence trentenaire : Moyenne historique de pluie P_ref (1981–2025)",
                "• Déficits hydriques communaux : Déficit net D_m = P_obs - P_ref (mm) et relatif D% (%)"
            ],
            "in_out": "Entrées : Rasters normalisés  ➔  Sortie : Séries temporelles agrégées par commune"
        },
        {
            "num": "4",
            "title": "MODÉLISATION SPATIALE CONTINUE & TYPOLOGIE BIO-VÉGÉTALE",
            "icon": "🗺️",
            "y": 28,
            "bg": "#FDF2F8",
            "border": "#DB2777",
            "items": [
                "• Interpolation spatiale continue par IDW (Inverse Distance Weighting, puissance p=2)",
                "• Génération des courbes et champs d'isohyètes (pas régulier de 50 mm de pluie)",
                "• Discrétisation radiométrique de la biomasse en 6 classes d'état de végétation"
            ],
            "in_out": "Entrées : Données zonales  ➔  Sortie : Isolignes isohyètes & Cartes thématiques"
        },
        {
            "num": "5",
            "title": "STRUCTURATION RELATIONNELLE & RESTITUTION DÉCISIONNELLE",
            "icon": "📊",
            "y": 11,
            "bg": "#F8FAFC",
            "border": "#0F4C81",
            "items": [
                "• Hiérarchisation gigogne multi-échelles (Échelle Commune ➔ District ➔ Région)",
                "• Grille d'évaluation de la sévérité des sécheresses (Déficit Modéré, Sévère, Extrême)",
                "• Restitution dynamique spatio-temporelle (Cartographie choroplèthe, timeline interactive)"
            ],
            "in_out": "Entrées : Modèles spatiaux  ➔  Sortie : Indicateurs d'aide à la décision & Tableaux de bord"
        }
    ]

    for b in boxes_data:
        y_center = b["y"]
        height = 13.2
        width = 86
        x_left = 7
        
        # Boîte principale
        box = FancyBboxPatch((x_left, y_center - height/2), width, height,
                             boxstyle="round,pad=0.6,rounding_size=1.2",
                             facecolor=b["bg"], edgecolor=b["border"], linewidth=2, zorder=2)
        ax.add_patch(box)
        
        # Pastille Numéro
        badge = FancyBboxPatch((x_left + 1.2, y_center + height/2 - 3.2), 3.2, 2.4,
                               boxstyle="round,pad=0.3,rounding_size=0.6",
                               facecolor=b["border"], edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(x_left + 2.8, y_center + height/2 - 2.0, b["num"],
                ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF', zorder=4)
        
        # Titre de l'étape
        ax.text(x_left + 5.5, y_center + height/2 - 2.0, f"{b['icon']}  {b['title']}",
                ha='left', va='center', fontsize=11, fontweight='bold', color=b["border"], zorder=4)
        
        # Points descriptifs
        y_text = y_center + 1.6
        for item in b["items"]:
            ax.text(x_left + 3.0, y_text, item,
                    ha='left', va='center', fontsize=8.8, color='#1E293B', zorder=4)
            y_text -= 2.3
            
        # Ligne d'Entrée / Sortie en bas de boîte
        sub_box = FancyBboxPatch((x_left + 2.0, y_center - height/2 + 0.6), width - 4.0, 1.9,
                                 boxstyle="round,pad=0.2,rounding_size=0.4",
                                 facecolor='#FFFFFF', edgecolor=b["border"], linewidth=0.8, zorder=3)
        ax.add_patch(sub_box)
        ax.text(x_left + 3.0, y_center - height/2 + 1.55, f"🔄 {b['in_out']}",
                ha='left', va='center', fontsize=8.0, fontweight='bold', color='#475569', zorder=4)

    # Flèches de transition entre les boîtes
    arrow_y_pairs = [(72.4, 68.6), (55.4, 51.6), (38.4, 34.6), (21.4, 17.6)]
    for y_top, y_bot in arrow_y_pairs:
        arrow = FancyArrowPatch((50, y_top), (50, y_bot),
                                arrowstyle='simple,head_width=6,head_length=6',
                                facecolor='#0284C7', edgecolor='none', zorder=5)
        ax.add_patch(arrow)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Figure abstraite générée : {output_path}")

def create_figure_concrete(output_path):
    fig = plt.figure(figsize=(15, 12), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    # Titre
    ax.text(50, 97.0, "CHAÎNE DE TRAITEMENT CONCRÈTE (ARCHITECTURE TECHNIQUE DYNATSIMO)",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F4C81',
            fontfamily='sans-serif')
    ax.text(50, 94.3, "Pipeline Logiciel, Formats de Données, Scripts Python/R, PostgreSQL & Front-End React",
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#0D9488',
            fontfamily='sans-serif')
    ax.plot([5, 95], [92.2, 92.2], color='#CBD5E1', lw=1.5)

    # 4 Colonnes Techniques
    cols = [
        {
            "x": 3, "w": 21, "title": "1. SOURCES & ENTRÉES", "color": "#0284C7", "bg": "#F0F9FF",
            "boxes": [
                ("CHIRPS v2.0 (UCSB)", "• Format: GeoTIFF (.tif.gz)\n• Résolution: 0.05° (~5 km)\n• Période: 1981–2026 (Mensuel)\n• Serveur HTTP UCSB CHC", "#0284C7"),
                ("MODIS MOD13Q1", "• Format: Image Collection\n• Résolution: 250m / 16 jours\n• Capteur: Terra/Aqua\n• API Google Earth Engine", "#0284C7"),
                ("Sentinel-2 & Landsat", "• Sentinel-2 MSI (10m)\n• Landsat 5/7/8/9 (30m)\n• Filtrage nuages QA bitmask\n• API Earth Engine Cloud", "#0284C7"),
                ("Référentiel SIG", "• Shapefile 3_region.shp\n• 121 communes du Sud\n• Attributs & frontières\n• EPSG:4326 (WGS84)", "#0284C7")
            ]
        },
        {
            "x": 26.5, "w": 23.5, "title": "2. SCRIPTS & TRAITEMENTS", "color": "#0D9488", "bg": "#F0FDF4",
            "boxes": [
                ("download_chirps_monthly_VF.py", "• Ingestion HTTP & décompression\n• Découpage rasterio.mask\n• 548 rasters mensuels\n• Sortie: CHIRPS_data/*.tif", "#0D9488"),
                ("download_ndvi_modis_VF.py", "• Requêtes Google Earth Engine\n• Calculs NDVI (NIR-Red)/(NIR+Red)\n• Compositing mensuel\n• Sortie: NDVI_MODIS/*.tif", "#0D9488"),
                ("isohyette_chirps_VF.py", "• Interpolation SciPy IDW (p=2)\n• Extraction isolignes 50 mm\n• Export GeoJSON & GeoTIFF\n• Sortie: public/data/isohyetes/", "#0D9488"),
                ("export_ndvi_6classes.py", "• Segmentation en 6 classes\n• Colorisation RGBA NoData trans.\n• 319 rasters PNG mensuels\n• Sortie: public/data/raster/", "#0D9488")
            ]
        },
        {
            "x": 52.5, "w": 22.5, "title": "3. STOCKAGE & SERVEURS", "color": "#7C3AED", "bg": "#FAF5FF",
            "boxes": [
                ("Base PostgreSQL / PostGIS", "• Table public.communes\n• Table public.precipitation\n• Table public.ndvi_observations\n• 123 300 enregistrements", "#7C3AED"),
                ("Serveur GeoServer WMS", "• Workspace: donnees_dynatsimo\n• Couches: chirps_YYYY_MM\n• Couches: ndvi_YYYY_MM\n• Port standard: 8080", "#7C3AED"),
                ("Serveur API REST Python", "• Script: scripts/api-server.py\n• FastAPI + Uvicorn (Port 8000)\n• Endpoints: /api/data\n• Endpoints: /api/sync/*", "#7C3AED"),
                ("Cache JSON Statique", "• overview.json, saisons.json\n• communes.geojson\n• annual-precipitations.json\n• anomalies.json, ndvi_classes", "#7C3AED")
            ]
        },
        {
            "x": 77.5, "w": 19.5, "title": "4. RESTITUTION REACT", "color": "#E11D48", "bg": "#FFF1F2",
            "boxes": [
                ("Cartographie Dynamique", "• React-Leaflet & Tuiles WMS\n• Choroplèthe & Isohyètes\n• NDVI 6 classes transparent\n• Switch fonds de carte HD", "#E11D48"),
                ("Lecteur Temporel", "• Slider & Play/Pause (1.2s)\n• Détection auto des mois\n• Arrêt dynamique (Août 2026)\n• Mode Crise 2020–22", "#E11D48"),
                ("Graphiques Recharts", "• Courbes de climatologie\n• Barres anomalies D% (Rouge/Bleu)\n• Zoom temporel & infobulles\n• Exportation CSV complète", "#E11D48"),
                ("Barre de Recherche", "• Autocomplétion commune\n• Zoom instantané sur commune\n• Badge District & Région\n• Mode Plein Écran & Thèmes", "#E11D48")
            ]
        }
    ]

    for col in cols:
        cx, cw = col["x"], col["w"]
        # En-tête de colonne
        hdr = FancyBboxPatch((cx, 86.5), cw, 4.2,
                             boxstyle="round,pad=0.3,rounding_size=0.8",
                             facecolor=col["color"], edgecolor='none', zorder=2)
        ax.add_patch(hdr)
        ax.text(cx + cw/2, 88.6, col["title"],
                ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=3)
        
        # Boîtes d'éléments
        y_pos = [68, 48, 28, 8]
        for idx, (b_title, b_desc, b_col) in enumerate(col["boxes"]):
            y_c = y_pos[idx]
            h = 16.5
            box = FancyBboxPatch((cx, y_c), cw, h,
                                 boxstyle="round,pad=0.4,rounding_size=0.8",
                                 facecolor=col["bg"], edgecolor=col["color"], linewidth=1.2, zorder=2)
            ax.add_patch(box)
            
            # Titre boîte
            ax.text(cx + 1.0, y_c + h - 2.2, b_title,
                    ha='left', va='center', fontsize=8.5, fontweight='bold', color=col["color"], zorder=3)
            
            # Texte boîte
            ax.text(cx + 1.0, y_c + h/2 - 1.2, b_desc,
                    ha='left', va='center', fontsize=7.2, color='#1E293B', linespacing=1.35, zorder=3)

    # Flèches horizontales de liaison entre colonnes
    arrow_pairs = [
        ((24.2, 76), (26.3, 76)), ((24.2, 56), (26.3, 56)), ((24.2, 16), (26.3, 16)),
        ((50.2, 76), (52.3, 76)), ((50.2, 36), (52.3, 36)), ((50.2, 16), (52.3, 16)),
        ((75.2, 76), (77.3, 76)), ((75.2, 56), (77.3, 56)), ((75.2, 16), (77.3, 16))
    ]
    for p_start, p_end in arrow_pairs:
        arr = FancyArrowPatch(p_start, p_end,
                              arrowstyle='simple,head_width=4.5,head_length=4.5',
                              facecolor='#64748B', edgecolor='none', zorder=4)
        ax.add_patch(arr)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print(f"Figure concrète générée : {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.getcwd(), "scratch")
    os.makedirs(out_dir, exist_ok=True)
    create_figure_abstraite(os.path.join(out_dir, "figure_chaine_abstraite.png"))
    create_figure_concrete(os.path.join(out_dir, "figure_chaine_concrete.png"))
