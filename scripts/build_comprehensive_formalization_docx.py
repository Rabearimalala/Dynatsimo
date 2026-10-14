# -*- coding: utf-8 -*-
"""
Générateur des 6 diagrammes haute résolution et du document Word officiel :
Formalisation complète des chaînes de traitement CHIRPS, MODIS et ENSEMBLE (Abstraites et Concrètes)
"""

import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ----------------------------------------------------------------------
# 1. GÉNÉRATION DES 6 FIGURES MATPLOTLIB (300 DPI)
# ----------------------------------------------------------------------

def draw_vertical_chain(ax, title, subtitle, boxes, arrow_color='#0284C7'):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    ax.text(50, 96.5, title, ha='center', va='center', fontsize=14, fontweight='bold', color='#0F4C81', fontfamily='sans-serif')
    ax.text(50, 93.8, subtitle, ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#0D9488', fontfamily='sans-serif')
    ax.plot([10, 90], [91.5, 91.5], color='#CBD5E1', lw=1.5)
    
    for b in boxes:
        yc = b["y"]
        h = 13.0
        w = 86
        xl = 7
        
        box = FancyBboxPatch((xl, yc - h/2), w, h,
                             boxstyle="round,pad=0.6,rounding_size=1.2",
                             facecolor=b["bg"], edgecolor=b["border"], linewidth=2, zorder=2)
        ax.add_patch(box)
        
        badge = FancyBboxPatch((xl + 1.2, yc + h/2 - 3.2), 3.2, 2.4,
                               boxstyle="round,pad=0.3,rounding_size=0.6",
                               facecolor=b["border"], edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(xl + 2.8, yc + h/2 - 2.0, b["num"],
                ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF', zorder=4)
        
        ax.text(xl + 5.5, yc + h/2 - 2.0, f"{b['tag']} : {b['title']}",
                ha='left', va='center', fontsize=10.5, fontweight='bold', color=b["border"], zorder=4)
        
        yt = yc + 1.5
        for item in b["items"]:
            ax.text(xl + 3.0, yt, item, ha='left', va='center', fontsize=8.5, color='#1E293B', zorder=4)
            yt -= 2.2
            
        sub = FancyBboxPatch((xl + 2.0, yc - h/2 + 0.6), w - 4.0, 1.9,
                             boxstyle="round,pad=0.2,rounding_size=0.4",
                             facecolor='#FFFFFF', edgecolor=b["border"], linewidth=0.8, zorder=3)
        ax.add_patch(sub)
        ax.text(xl + 3.0, yc - h/2 + 1.55, f"FLUX : {b['in_out']}",
                ha='left', va='center', fontsize=7.8, fontweight='bold', color='#475569', zorder=4)
        
    pairs = [(72.4, 68.6), (55.4, 51.6), (38.4, 34.6), (21.4, 17.6)]
    for yt, yb in pairs:
        arr = FancyArrowPatch((50, yt), (50, yb),
                              arrowstyle='simple,head_width=6,head_length=6',
                              facecolor=arrow_color, edgecolor='none', zorder=5)
        ax.add_patch(arr)

def draw_4col_chain(ax, title, subtitle, cols):
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    ax.text(50, 97.0, title, ha='center', va='center', fontsize=14, fontweight='bold', color='#0F4C81', fontfamily='sans-serif')
    ax.text(50, 94.3, subtitle, ha='center', va='center', fontsize=10, fontstyle='italic', color='#0D9488', fontfamily='sans-serif')
    ax.plot([5, 95], [92.2, 92.2], color='#CBD5E1', lw=1.5)
    
    for col in cols:
        cx, cw = col["x"], col["w"]
        hdr = FancyBboxPatch((cx, 86.5), cw, 4.2,
                             boxstyle="round,pad=0.3,rounding_size=0.8",
                             facecolor=col["color"], edgecolor='none', zorder=2)
        ax.add_patch(hdr)
        ax.text(cx + cw/2, 88.6, col["title"],
                ha='center', va='center', fontsize=9.2, fontweight='bold', color='#FFFFFF', zorder=3)
        
        y_pos = [68, 48, 28, 8]
        for idx, (b_title, b_desc, b_col) in enumerate(col["boxes"]):
            yc = y_pos[idx]
            h = 16.5
            box = FancyBboxPatch((cx, yc), cw, h,
                                 boxstyle="round,pad=0.4,rounding_size=0.8",
                                 facecolor=col["bg"], edgecolor=col["color"], linewidth=1.2, zorder=2)
            ax.add_patch(box)
            
            ax.text(cx + 1.0, yc + h - 2.2, b_title,
                    ha='left', va='center', fontsize=8.2, fontweight='bold', color=col["color"], zorder=3)
            
            ax.text(cx + 1.0, yc + h/2 - 1.2, b_desc,
                    ha='left', va='center', fontsize=7.0, color='#1E293B', linespacing=1.35, zorder=3)
            
    arrow_pairs = [
        ((24.2, 76), (26.3, 76)), ((24.2, 56), (26.3, 56)), ((24.2, 16), (26.3, 16)),
        ((50.2, 76), (52.3, 76)), ((50.2, 36), (52.3, 36)), ((50.2, 16), (52.3, 16)),
        ((75.2, 76), (77.3, 76)), ((75.2, 56), (77.3, 56)), ((75.2, 16), (77.3, 16))
    ]
    for ps, pe in arrow_pairs:
        arr = FancyArrowPatch(ps, pe, arrowstyle='simple,head_width=4.5,head_length=4.5', facecolor='#64748B', edgecolor='none', zorder=4)
        ax.add_patch(arr)

# 1. Figure CHIRPS Abstraite
def fig_chirps_abstraite(path):
    fig = plt.figure(figsize=(14, 11), dpi=300)
    ax = fig.add_subplot(111)
    boxes = [
        {
            "num": "1", "tag": "PHASE 1", "title": "OBSERVATION PLUVIOMÉTRIQUE SATELLITAIRE & STATIONS",
            "y": 79, "bg": "#EFF6FF", "border": "#2563EB",
            "items": [
                "• Télédétection infrarouge thermique géostationnaire (durée des nuages froids convectifs)",
                "• Calibrage par micro-ondes passives et réanalyses atmosphériques globales (NOAA/NCEP)",
                "• Fusion et correction de biais avec les observations pluviométriques des stations au sol"
            ],
            "in_out": "Entrées : Signaux infrarouges + Pluviomètres   ➔   Sortie : Grilles globales brutes de pluie"
        },
        {
            "num": "2", "tag": "PHASE 2", "title": "PRÉTRAITEMENT SPATIAL & DÉCOUPAGE SUR LE GRAND SUD",
            "y": 62, "bg": "#F0FDF4", "border": "#16A34A",
            "items": [
                "• Découpage géométrique selon les frontières des 3 régions du Sud (Androy, Anosy, Atsimo-Andrefana)",
                "• Standardisation géodésique WGS84 (EPSG:4326) à résolution 0.05° (~5.3 km)",
                "• Agrégation temporelle en cumuls mensuels continus (série 1981–2026, 548 mois)"
            ],
            "in_out": "Entrées : Grilles globales   ➔   Sortie : Rasters régionaux mensuels découpés"
        },
        {
            "num": "3", "tag": "PHASE 3", "title": "CALCUL DES STATISTIQUES ZONALES & ANOMALIES DE PLUIE",
            "y": 45, "bg": "#FEFCE8", "border": "#CA8A04",
            "items": [
                "• Extraction des cumuls mensuels moyens par commune (121 communes du Grand Sud)",
                "• Établissement de la normale climatologique de référence 1981–2025 (P_ref,m)",
                "• Calcul du déficit net D_m = P_obs - P_ref (mm) et du taux d'écart relatif D% = (D_m / P_ref) * 100"
            ],
            "in_out": "Entrées : Rasters découpés + Polygones   ➔   Sortie : Séries temporelles d'anomalies"
        },
        {
            "num": "4", "tag": "PHASE 4", "title": "INTERPOLATION CONTINUE IDW & ISOHYÈTES",
            "y": 28, "bg": "#FDF2F8", "border": "#DB2777",
            "items": [
                "• Modélisation continue par pondération inverse de la distance IDW (Inverse Distance Weighting, p=2)",
                "• Génération des isolignes de précipitations par tranches régulières de 50 mm",
                "• Analyse des gradients pluviométriques d'Est (humide) en Ouest/Sud (semi-aride)"
            ],
            "in_out": "Entrées : Valeurs ponctuelles barycentres   ➔   Sortie : Courbes et surfaces d'isohyètes"
        },
        {
            "num": "5", "tag": "PHASE 5", "title": "DIAGNOSTIC DE SÉCHERESSE & RESTITUTION DÉCISIONNELLE",
            "y": 11, "bg": "#F8FAFC", "border": "#0F4C81",
            "items": [
                "• Grille de sévérité : Déficit Extrême (<-50%), Sévère (-50% à -25%), Modéré (-25% à -10%), Normal",
                "• Caractérisation des sécheresses pluriannuelles (ex: Épisode triennal historique 2020–2022)",
                "• Cartographie choroplèthe, animation chronologique et courbes de tendances pour l'alerte précoce"
            ],
            "in_out": "Entrées : Séries d'anomalies & Isohyètes   ➔   Sortie : Indicateurs d'alerte et tableaux de bord"
        }
    ]
    draw_vertical_chain(ax, "CHAÎNE DE TRAITEMENT ABSTRAITE — MODULE PLUVIOMÉTRIE CHIRPS",
                        "Modélisation Conceptuelle de l'Estimation, du Calcul des Anomalies et des Isohyètes", boxes, '#2563EB')
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# 2. Figure CHIRPS Concrète
def fig_chirps_concrete(path):
    fig = plt.figure(figsize=(15, 12), dpi=300)
    ax = fig.add_subplot(111)
    cols = [
        {
            "x": 3, "w": 21, "title": "1. SOURCE & INGESTION", "color": "#0284C7", "bg": "#F0F9FF",
            "boxes": [
                ("Serveur HTTP UCSB CHC", "• URL: data.chc.ucsb.edu\n• Format: chirps-v2.0.YYYY.MM.tif.gz\n• Résolution: 0.05° (~5 km)\n• Période: 1981–2026", "#0284C7"),
                ("download_chirps_VF.py", "• Ingestion automatisée HTTP\n• Décompression gzip en mémoire\n• Masquage: rasterio.mask.mask\n• Shapefile: 3_region.shp", "#0284C7"),
                ("Rasters Découpés", "• 548 fichiers GeoTIFF locaux\n• Dossier: CHIRPS_data/\n• Nom: chirps-v2.0.YYYY.MM.tif\n• Système: EPSG:4326 (WGS84)", "#0284C7"),
                ("Contrôle Qualité", "• Vérification NoData (-9999)\n• Détection dernier mois publié\n• Arrêt dynamique (Août 2026)\n• Logs d'intégrité fichiers", "#0284C7")
            ]
        },
        {
            "x": 26.5, "w": 23.5, "title": "2. TRAITEMENTS & SIG", "color": "#0D9488", "bg": "#F0FDF4",
            "boxes": [
                ("import-chirps-export.py", "• Rasterstats (zonal_stats)\n• Moyennes mensuelles / commune\n• 121 communes traitées\n• Calcul cumul annuel & saisons", "#0D9488"),
                ("isohyette_chirps_VF.py", "• Interpolation SciPy IDW (p=2)\n• Grille fine régulière 35x35\n• Extraction contours 50 mm\n• Export GeoTIFF & GeoJSON", "#0D9488"),
                ("export_isohyetes.py", "• Génération GeoJSON isohyètes\n• Calcul min, mean, max par pas\n• Dossier: public/data/isohyetes/\n• isohyetes_metadata.json", "#0D9488"),
                ("Calcul des Anomalies", "• Normale trentenaire 1981-2025\n• Écart D_m = P_obs - P_ref (mm)\n• Taux D% = (D_m / P_ref)*100\n• Mode Crise Triennale 2020-22", "#0D9488")
            ]
        },
        {
            "x": 52.5, "w": 22.5, "title": "3. BASE POSTGRES & CACHE", "color": "#7C3AED", "bg": "#FAF5FF",
            "boxes": [
                ("Table public.precipitation", "• PostgreSQL 15 + PostGIS\n• 123 300 enregistrements\n• Colonnes: commune_code, year,\n  month, precip_mm, anomalie_mm", "#7C3AED"),
                ("GeoServer WMS (8080)", "• Workspace: donnees_dynatsimo\n• Couches: chirps_YYYY_MM\n• Style SLD: dégradé bleu pluie\n• Tuiles WMS transparentes", "#7C3AED"),
                ("API REST (FastAPI :8000)", "• Script: scripts/api-server.py\n• Endpoint: /api/data\n• Endpoint: /api/sync/precipitation\n• Endpoint: /api/sync/all", "#7C3AED"),
                ("Cache JSON Public", "• annual-precipitations.json\n• monthly-climatology.json\n• anomalies.json, saisons.json\n• precip-records.json", "#7C3AED")
            ]
        },
        {
            "x": 77.5, "w": 19.5, "title": "4. INTERFACE REACT", "color": "#E11D48", "bg": "#FFF1F2",
            "boxes": [
                ("Cartes Leaflet", "• Mode Choroplèthe communale\n• Mode Isohyètes dynamiques\n• Mode Déficit Pluviométrique\n• Fonds de carte HD commutables", "#E11D48"),
                ("Lecteur Temporel", "• Animation play/pause (1.2s)\n• Scrubber mois par mois\n• Arrêt dynamique à Août 2026\n• Filtre intelligent des mois", "#E11D48"),
                ("Graphiques Recharts", "• Courbes de climatologie\n• Barres anomalies Rouge/Bleu\n• Infobulles interactives\n• Exportation table CSV", "#E11D48"),
                ("Recherche Commune", "• Zoom instantané sur commune\n• Badge District / Région\n• Fiche synthétique communale\n• Mode Plein écran & Thèmes", "#E11D48")
            ]
        }
    ]
    draw_4col_chain(ax, "CHAÎNE DE TRAITEMENT CONCRÈTE — MODULE PLUVIOMÉTRIE CHIRPS",
                    "Implémentation Opérationnelle : Ingestion HTTP, Traitements Python, PostGIS, WMS & React", cols)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# 3. Figure MODIS Abstraite
def fig_modis_abstraite(path):
    fig = plt.figure(figsize=(14, 11), dpi=300)
    ax = fig.add_subplot(111)
    boxes = [
        {
            "num": "1", "tag": "PHASE 1", "title": "CAPTATION MULTISPECTRALE SOLAIRE PAR SATELLITE",
            "y": 79, "bg": "#EFF6FF", "border": "#2563EB",
            "items": [
                "• Mesure de la réflectance dans la bande Rouge (620–670 nm, absorption par la chlorophylle)",
                "• Mesure de la réflectance dans le Proche Infrarouge PIR (841–876 nm, réflexion cellulaire foliaire)",
                "• Balayage spatial régulier à 250m de résolution (capteur MODIS Terra/Aqua)"
            ],
            "in_out": "Entrées : Rayonnement électromagnétique   ➔   Sortie : Bandes spectrales brutes (Rouge, PIR)"
        },
        {
            "num": "2", "tag": "PHASE 2", "title": "PRÉTRAITEMENT RADIOMÉTRIQUE & MASQUAGE NUAGEUX",
            "y": 62, "bg": "#F0FDF4", "border": "#16A34A",
            "items": [
                "• Analyse des masques de qualité atmosphérique (QA bitmask : nuages, cirrus, ombres portées)",
                "• Découpage sur l'emprise vectorielle du Grand Sud de Madagascar (AOI 3 régions)",
                "• Composition temporelle mensuelle (synthèse par valeur maximale MVC pour éliminer les résidus nuageux)"
            ],
            "in_out": "Entrées : Bandes brutes   ➔   Sortie : Composites mensuels optiques sans nuages"
        },
        {
            "num": "3", "tag": "PHASE 3", "title": "CALCUL DES INDICES BIOLOGIQUES (NDVI, VCI, VHI)",
            "y": 45, "bg": "#FEFCE8", "border": "#CA8A04",
            "items": [
                "• Indice de Végétation par Différence Normalisée : NDVI = (PIR - Rouge) / (PIR + Rouge)",
                "• Indice de Condition de la Végétation : VCI = (NDVI - NDVI_min) / (NDVI_max - NDVI_min) * 100",
                "• Statistiques zonales communales : extraction des moyennes de vigueur végétale par polygone communal"
            ],
            "in_out": "Entrées : Composites mensuels   ➔   Sortie : Matrices continues de NDVI et séries zonales"
        },
        {
            "num": "4", "tag": "PHASE 4", "title": "TYPOLOGIE EN 6 CLASSES D'ÉTAT DE LA BIOMASSE",
            "y": 28, "bg": "#FDF2F8", "border": "#DB2777",
            "items": [
                "• Discrétisation radiométrique : (1) Eau <0, (2) Sol nu 0–0.2, (3) Fourré dégradé 0.2–0.4,",
                "  (4) Fourré arbustif/Cultures 0.4–0.6, (5) Forêt sèche/Canopée 0.6–0.8, (6) Végétation très dense >0.8",
                "• Colorisation thématique et standardisation cartographique des seuils de biomasse"
            ],
            "in_out": "Entrées : Raster NDVI continu   ➔   Sortie : Cartes catégorielles en 6 classes"
        },
        {
            "num": "5", "tag": "PHASE 5", "title": "ANALYSE DE LA DÉGRADATION & RESTITUTION DÉCISIONNELLE",
            "y": 11, "bg": "#F8FAFC", "border": "#0F4C81",
            "items": [
                "• Évaluation du stress chlorophyllien et comparaison interannuelle du couvert végétal",
                "• Suivi de la dynamique de repousse post-hivernale et détection précoce du flétrissement",
                "• Restitution interactive multi-temporelle avec superposition des frontières communales"
            ],
            "in_out": "Entrées : Cartes 6 classes & Séries NDVI   ➔   Sortie : Indicateurs de biomasse et alertes dégradation"
        }
    ]
    draw_vertical_chain(ax, "CHAÎNE DE TRAITEMENT ABSTRAITE — MODULE VÉGÉTATION NDVI MODIS",
                        "Modélisation Conceptuelle du Traitement Multispectral et de la Classification en 6 Classes", boxes, '#16A34A')
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# 4. Figure MODIS Concrète
def fig_modis_concrete(path):
    fig = plt.figure(figsize=(15, 12), dpi=300)
    ax = fig.add_subplot(111)
    cols = [
        {
            "x": 3, "w": 21, "title": "1. EXTRACTION GEE & SOURCES", "color": "#0284C7", "bg": "#F0F9FF",
            "boxes": [
                ("Collection MODIS GEE", "• MODIS/061/MOD13Q1\n• Résolution: 250m (16 jours)\n• Bandes: sur_refl_b01/b02\n• API Google Earth Engine", "#0284C7"),
                ("download_ndvi_modis_VF", "• Authentification GEE Python\n• Masquage nuages QA bitmask\n• Réduction mensuelle MVC\n• Découpage sur 3_region.shp", "#0284C7"),
                ("GeoTIFF NDVI Générés", "• 319 rasters mensuels (2000-26)\n• Dossier: NDVI_MODIS/YYYY/\n• Nom: NDVI_MODIS_YYYY_MM.tif\n• Système: EPSG:4326", "#0284C7"),
                ("Capteurs Complémentaires", "• download_sentinnel_VF (10m)\n• download_ndvi_landsat_VF (30m)\n• Données comparatives capteurs\n• Validation croisée spatiale", "#0284C7")
            ]
        },
        {
            "x": 26.5, "w": 23.5, "title": "2. SEGMENTATION & CLUSTERS", "color": "#0D9488", "bg": "#F0FDF4",
            "boxes": [
                ("export_ndvi_6classes.py", "• Reclassification NumPy en 6 classes\n• Colorisation RGBA exacte\n• Masquage NoData (Alpha transparent)\n• 319 PNG générés dans public/", "#0D9488"),
                ("ndvi_classes_metadata.json", "• Catalogue complet des 319 périodes\n• URL relatives des tuiles PNG\n• Dimensions (1888x2092 px)\n• Bounding box géographique", "#0D9488"),
                ("cluster_ndvi_raster_VF.py", "• Clustering spatial non supervisé\n• Algorithmes CAH + K-Means\n• Analyse typologique des profils\n• Sortie: public/data/clusters/", "#0D9488"),
                ("Statistiques Communales", "• import-ndvi-from-gee.py\n• Moyennes mensuelles / commune\n• Séries 2000–2026 complètes\n• Export: vegetation-data.json", "#0D9488")
            ]
        },
        {
            "x": 52.5, "w": 22.5, "title": "3. STOCKAGE POSTGRES & WMS", "color": "#7C3AED", "bg": "#FAF5FF",
            "boxes": [
                ("Table ndvi_observations", "• PostgreSQL 15 / PostGIS\n• Colonnes: commune_code, sensor,\n  year, month, ndvi_mean\n• Séries historiques multi-satellites", "#7C3AED"),
                ("Table vegetation_payload", "• Payload JSON précalculé\n• Optimisation requêtes Dashboard\n• Chargement instantané React\n• Clé: commune_code", "#7C3AED"),
                ("GeoServer WMS NDVI", "• Workspace: donnees_dynatsimo\n• Couches: ndvi_YYYY_MM\n• Style SLD 6 classes officielles\n• Mode tuiles WMS transparentes", "#7C3AED"),
                ("Cache Tuiles Web", "• public/data/raster/ndvi_modis_6classes/\n• 319 PNG optimisés pour le web\n• metadata: ndvi_classes_metadata\n• vegetation-data.json", "#7C3AED")
            ]
        },
        {
            "x": 77.5, "w": 19.5, "title": "4. RESTITUTION REACT NDVI", "color": "#E11D48", "bg": "#FFF1F2",
            "boxes": [
                ("Overlay Leaflet NDVI", "• ImageOverlay PNG transparent\n• Alternative flux GeoServer WMS\n• Curseur d'opacité (0 à 100%)\n• Superposition limites communes", "#E11D48"),
                ("Lecteur Temporel NDVI", "• 319 périodes animables\n• Lecture / Pause / Vitesse réglable\n• Détection auto mois (Août 2026)\n• Scrubber chronologique", "#E11D48"),
                ("Légende 6 Classes", "• Eau (<0), Sol nu (0-0.2),\n  Fourré dégradé (0.2-0.4),\n  Arbustif (0.4-0.6), Canopée (0.6-0.8),\n  Végétation dense (0.8-1.0)", "#E11D48"),
                ("Comparateur Capteurs", "• Simulation Landsat 30m\n• Simulation Sentinel 10m\n• Comparaison zoomée 3 capteurs\n• Analyse de gain de résolution", "#E11D48")
            ]
        }
    ]
    draw_4col_chain(ax, "CHAÎNE DE TRAITEMENT CONCRÈTE — MODULE VÉGÉTATION NDVI MODIS",
                    "Implémentation Opérationnelle : API Earth Engine, Tuilage PNG 6 Classes, PostGIS & React", cols)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# 5. Figure ENSEMBLE Abstraite
def fig_ensemble_abstraite(path):
    fig = plt.figure(figsize=(14, 11), dpi=300)
    ax = fig.add_subplot(111)
    boxes = [
        {
            "num": "1", "tag": "PHASE 1", "title": "ACQUISITION & COUPLAGE MULTI-SOURCES BIOCLIMATIQUES",
            "y": 79, "bg": "#EFF6FF", "border": "#2563EB",
            "items": [
                "• Données Pluviométriques : Infrarouge thermique + Stations CHIRPS v2.0 (1981–2026)",
                "• Données d'Activité Chlorophyllienne : Réflectance Rouge/PIR multi-capteurs (MODIS, Sentinel, Landsat)",
                "• Données Territoriales : Maillage administratif vectoriel (121 Communes, 9 Districts, 3 Régions)"
            ],
            "in_out": "Entrées : Flux satellitaires hétérogènes   ➔   Sortie : Données brutes couplées"
        },
        {
            "num": "2", "tag": "PHASE 2", "title": "NORMALISATION & SYNCHRONISATION SPATIO-TEMPORELLE",
            "y": 62, "bg": "#F0FDF4", "border": "#16A34A",
            "items": [
                "• Harmonisation géodésique : Reprojection dans le repère mondial WGS84 (EPSG:4326)",
                "• Alignement temporel : Synchronisation au pas de temps mensuel commun (1981–2026)",
                "• Masquages de qualité : Élimination des bruits atmosphériques et découpage sur l'AOI Grand Sud"
            ],
            "in_out": "Entrées : Données brutes   ➔   Sortie : Rasters & Séries harmonisées et alignées"
        },
        {
            "num": "3", "tag": "PHASE 3", "title": "CALCULS CROISÉS & ANALYSE DE LA VULNÉRABILITÉ SÉCHERESSE",
            "y": 45, "bg": "#FEFCE8", "border": "#CA8A04",
            "items": [
                "• Calculs Pluvio : Climatologie de référence trentenaire P_ref, déficits volumétriques D_m et relatifs D%",
                "• Calculs Végétation : Indices de végétation NDVI, VCI (condition), VHI (santé globale de la végétation)",
                "• Analyse de corrélation croisée : Mesure du déphasage temporel entre déficit pluviométrique et flétrissement"
            ],
            "in_out": "Entrées : Rasters alignés   ➔   Sortie : Séries temporelles bivariées (Pluie vs NDVI)"
        },
        {
            "num": "4", "tag": "PHASE 4", "title": "MODÉLISATION SPATIALE INTÉGRÉE & TYPOLOGIES THÉMATIQUES",
            "y": 28, "bg": "#FDF2F8", "border": "#DB2777",
            "items": [
                "• Modélisation continue du champ de pluie par interpolation IDW (p=2) et génération des isohyètes",
                "• Modélisation discrète du couvert végétal en 6 classes d'état de la biomasse",
                "• Croisement spatial : Superposition des zones de fort déficit pluviométrique et de chute brutale du NDVI"
            ],
            "in_out": "Entrées : Séries bivariées   ➔   Sortie : Couches cartographiques couplées multi-échelles"
        },
        {
            "num": "5", "tag": "PHASE 5", "title": "SYSTÈME D'AIDE À LA DÉCISION & RESTITUTION MULTI-ÉCHELLES",
            "y": 11, "bg": "#F8FAFC", "border": "#0F4C81",
            "items": [
                "• Diagnostic territorial hiérarchisé : Échelle Communale ➔ District ➔ Région ➔ Grand Sud global",
                "• Grille d'alerte précoce sécheresse : Identification des communes prioritaires pour les secours humanitaires",
                "• Tableaux de bord décisionnels unifiés, cartes interactives avec timeline et exportations de rapports"
            ],
            "in_out": "Entrées : Couches couplées   ➔   Sortie : Plateforme décisionnelle unifiée DYNATSIMO"
        }
    ]
    draw_vertical_chain(ax, "CHAÎNE DE TRAITEMENT ABSTRAITE GLOBALE — SYSTÈME DYNATSIMO",
                        "Modélisation Intégrée Complète : Couplage Pluviométrie, Végétation & Décision Territoriale", boxes, '#0F4C81')
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# 6. Figure ENSEMBLE Concrète
def fig_ensemble_concrete(path):
    fig = plt.figure(figsize=(15, 12), dpi=300)
    ax = fig.add_subplot(111)
    cols = [
        {
            "x": 3, "w": 21, "title": "1. ACQUISITION & DONNÉES", "color": "#0284C7", "bg": "#F0F9FF",
            "boxes": [
                ("CHIRPS v2.0 (UCSB)", "• Pluviométrie 1981–2026\n• Format: .tif.gz (0.05°)\n• 548 rasters mensuels\n• HTTP data.chc.ucsb.edu", "#0284C7"),
                ("MODIS / Sentinel / Landsat", "• MOD13Q1 250m (2000-26)\n• Sentinel-2 MSI (10m)\n• Landsat 5/7/8/9 (30m)\n• Google Earth Engine API", "#0284C7"),
                ("Référentiel Administratif", "• Shapefile: 3_region.shp\n• 121 communes du Grand Sud\n• 9 districts & 3 régions\n• EPSG:4326 (WGS84)", "#0284C7"),
                ("Pipeline d'Ingestion", "• download_chirps_monthly_VF\n• download_ndvi_modis_VF\n• download_sentinnel_VF\n• sync_pipeline.py", "#0284C7")
            ]
        },
        {
            "x": 26.5, "w": 23.5, "title": "2. TRAITEMENTS SCIENTIFIQUES", "color": "#0D9488", "bg": "#F0FDF4",
            "boxes": [
                ("Prétraitements Rasters", "• Masquage: rasterio.mask\n• Filtrage nuages: QA bitmask\n• Reprojection GDAL WGS84\n• Compositing mensuel MVC", "#0D9488"),
                ("Isohyètes CHIRPS (IDW)", "• isohyette_chirps_VF.py\n• SciPy IDW puissance p=2\n• Isolignes pas 50 mm\n• GeoJSON + GeoTIFF", "#0D9488"),
                ("Segmentation 6 Classes", "• export_ndvi_6classes.py\n• 319 PNG RGBA transparents\n• metadata: ndvi_classes_metadata\n• Clustering CAH / K-Means", "#0D9488"),
                ("Statistiques & Anomalies", "• import-chirps-and-export.py\n• export-data.R (zonal_stats)\n• Déficits D_m & D% (1981-25)\n• Export 10 fichiers JSON", "#0D9488")
            ]
        },
        {
            "x": 52.5, "w": 22.5, "title": "3. PERSISTANCE & SERVEURS", "color": "#7C3AED", "bg": "#FAF5FF",
            "boxes": [
                ("PostgreSQL 15 / PostGIS", "• public.communes (géométries)\n• public.precipitation (123k)\n• public.ndvi_observations\n• Index spatiaux GiST", "#7C3AED"),
                ("GeoServer WMS (8080)", "• Workspace: donnees_dynatsimo\n• Couches: chirps_* & ndvi_*\n• Styles SLD sur mesure\n• Tuiles WMS transparentes", "#7C3AED"),
                ("Serveur API FastAPI (8000)", "• api-server.py (Uvicorn)\n• Endpoint: /api/data (JSON)\n• Endpoints: /api/sync/*\n• Proxy Vite intégré", "#7C3AED"),
                ("Cache JSON Public", "• public/data/*.json\n• communes.geojson, anomalies\n• isohyetes_metadata.json\n• ndvi_classes_metadata.json", "#7C3AED")
            ]
        },
        {
            "x": 77.5, "w": 19.5, "title": "4. APPLICATION WEB REACT", "color": "#E11D48", "bg": "#FFF1F2",
            "boxes": [
                ("Vues Applicatives", "• Vue Complète Page Unique\n• Vue Cartographique SIG\n• Vue Statistiques & Séries\n• Base de Données & Guide", "#E11D48"),
                ("Cartographie Interactive", "• React-Leaflet & Tuiles HD\n• Choroplèthe, Isohyètes, 6 Classes\n• Curseur opacité & superposition\n• Zoom instantané commune", "#E11D48"),
                ("Timeline Intelligente", "• Lecteur temporel animé (1.2s)\n• Détection auto mois (Août 2026)\n• Sélecteur dynamique adapté\n• Mode Crise 2020–22", "#E11D48"),
                ("Graphiques & Décision", "• Recharts: Climatologie & D%\n• Comparaison 3 capteurs\n• Grille sévérité sécheresse\n• Exportations CSV & rapports", "#E11D48")
            ]
        }
    ]
    draw_4col_chain(ax, "CHAÎNE DE TRAITEMENT CONCRÈTE GLOBALE — SYSTÈME DYNATSIMO",
                    "Architecture Technique Intégrée : Ingestion Multi-Sources, PostGIS, WMS, FastAPI & React", cols)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='#FFFFFF')
    plt.close()

# ----------------------------------------------------------------------
# 2. CONSTRUCTION DU DOCUMENT WORD OFFICIEL (.DOCX)
# ----------------------------------------------------------------------

def set_cell_background(cell, fill_hex):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}>'
                      f'<w:top w:w="{top}" w:type="dxa"/>'
                      f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
                      f'<w:left w:w="{left}" w:type="dxa"/>'
                      f'<w:right w:w="{right}" w:type="dxa"/>'
                      f'</w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)

def add_step_card(doc, num, title, description, border_color="0284C7", bg_color="F8FAFC"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=110, bottom=110, left=150, right=130)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_color}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(2)
    r_t = p.add_run(f"Étape {num} : {title}")
    r_t.bold = True
    r_t.font.name = "Calibri"
    r_t.font.size = Pt(10.5)
    r_t.font.color.rgb = RGBColor(15, 76, 129)
    
    p_b = cell.add_paragraph()
    p_b.paragraph_format.space_before = Pt(0)
    p_b.paragraph_format.space_after = Pt(0)
    r_b = p_b.add_run(description)
    r_b.font.name = "Calibri"
    r_b.font.size = Pt(9.2)
    r_b.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def build_formalization_docx(docx_path, img_paths):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.7)
        section.bottom_margin = Inches(0.7)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    PRIMARY = RGBColor(15, 76, 129)
    SECONDARY = RGBColor(13, 148, 136)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED = RGBColor(100, 116, 139)
    
    # ---------------- Header ----------------
    p_t = doc.add_paragraph()
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t.paragraph_format.space_before = Pt(0)
    p_t.paragraph_format.space_after = Pt(2)
    rt = p_t.add_run("FORMALISATION DES CHAÎNES DE TRAITEMENTS")
    rt.font.name = "Calibri"
    rt.font.size = Pt(22)
    rt.bold = True
    rt.font.color.rgb = PRIMARY
    
    p_s = doc.add_paragraph()
    p_s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_s.paragraph_format.space_after = Pt(10)
    rs = p_s.add_run("Modules CHIRPS (Pluviométrie), MODIS (NDVI) & Système Global DYNATSIMO")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    tbl_b = doc.add_table(rows=2, cols=2)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_b.autofit = False
    b_info = [
        [("Projet :", " DYNATSIMO (Surveillance Sécheresse & Activité Végétale)"), ("Zone :", " Grand Sud de Madagascar (Androy, Anosy, Atsimo-Andrefana)")],
        [("Période :", " 1981–2026 (Pluie CHIRPS) | 2000–2026 (NDVI MODIS)"), ("Contenu :", " 6 Figures Haute Définition (Abstraite & Concrète) + Fiches Explicatives")]
    ]
    for r_idx, row in enumerate(tbl_b.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(3.4)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            lbl, val = b_info[r_idx][c_idx]
            rl = p.add_run(lbl)
            rl.bold = True
            rl.font.size = Pt(9)
            rl.font.color.rgb = PRIMARY
            rv = p.add_run(val)
            rv.font.size = Pt(9)
            rv.font.color.rgb = DARK_TEXT
    set_table_borders(tbl_b, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # =============================================================
    # PARTIE 1 : MODULE PLUVIOMÉTRIE CHIRPS
    # =============================================================
    h_part1 = doc.add_paragraph()
    h_part1.paragraph_format.space_before = Pt(10)
    h_part1.paragraph_format.space_after = Pt(3)
    rh1 = h_part1.add_run("PARTIE I — MODULE PLUVIOMÉTRIE & DÉFICITS (CHIRPS)")
    rh1.font.name = "Calibri"
    rh1.font.size = Pt(16)
    rh1.bold = True
    rh1.font.color.rgb = PRIMARY
    
    # 1.1 Chaîne Abstraite CHIRPS
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("1. Chaîne de Traitement Abstraite (Niveau Conceptuel — CHIRPS)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["chirps_abs"]):
        doc.add_picture(img_paths["chirps_abs"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 1.A : Diagramme conceptuel de la chaîne abstraite CHIRPS (Pluviométrie & Déficits)")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Observation & Télédétection Pluviométrique",
                  "Mesure indirecte combinant les températures au sommet des nuages convectifs (Infrarouge thermique géostationnaire) "
                  "et les micro-ondes passives, calibrées en continu avec les observations des stations météorologiques terrestres.", "2563EB", "EFF6FF")
    add_step_card(doc, "2", "Prétraitement & Découpage Régional",
                  "Extraction géométrique des rasters 0.05° (~5.3 km) sur les limites du Grand Sud (Androy, Anosy, Atsimo-Andrefana) "
                  "dans le système géodésique WGS84 (EPSG:4326), avec constitution de la série mensuelle continue 1981–2026.", "16A34A", "F0FDF4")
    add_step_card(doc, "3", "Statistiques Zonales & Calcul des Déficits",
                  "Extraction des cumuls mensuels par commune (121 communes), calcul de la normale climatologique de référence 1981–2025 (P_ref,m), "
                  "du déficit volumétrique net D_m = P_obs - P_ref (mm) et de l'écart relatif en pourcentage D% = (D_m / P_ref) * 100.", "CA8A04", "FEFCE8")
    add_step_card(doc, "4", "Interpolation Continue IDW & Isohyètes",
                  "Reconstitution d'un champ continu de précipitations par pondération inverse de la distance IDW (p=2) et extraction des courbes d'isohyètes par pas de 50 mm.", "DB2777", "FDF2F8")
    add_step_card(doc, "5", "Diagnostic & Matrice de Sévérité Sécheresse",
                  "Classification des anomalies en 5 niveaux de stress hydrique (Déficit Extrême <-50%, Sévère -50% à -25%, Modéré -25% à -10%, Normal, Excédent) "
                  "et analyse des épisodes pluriannuels historiques (Crise Triennale 2020–2022).", "0F4C81", "F8FAFC")
    
    doc.add_page_break()
    
    # 1.2 Chaîne Concrète CHIRPS
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("2. Chaîne de Traitement Concrète (Implémentation Opérationnelle — CHIRPS)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["chirps_cnc"]):
        doc.add_picture(img_paths["chirps_cnc"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 1.B : Architecture technique et flux opérationnels du module CHIRPS")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Ingestion HTTP & Décompression (download_chirps_monthly_VF.py)",
                  "Téléchargement automatisé des archives `.tif.gz` depuis `data.chc.ucsb.edu`, décompression en mémoire, découpage avec `rasterio.mask` "
                  "selon le shapefile `Regions 3/3_region.shp` et sauvegarde de 548 rasters mensuels dans `CHIRPS_data/chirps-v2.0.YYYY.MM.tif`.", "0284C7", "F0F9FF")
    add_step_card(doc, "2", "Interpolation IDW & Export Isohyètes (isohyette_chirps_VF.py & export_isohyetes.py)",
                  "Algorithme SciPy IDW sur grille fine 35x35, extraction des courbes de niveau 50 mm et génération des fichiers GeoJSON dans `public/data/isohyetes/` "
                  "avec index de métadonnées `isohyetes_metadata.json` (min, mean, max par période).", "0D9488", "F0FDF4")
    add_step_card(doc, "3", "Statistiques Zonales & Base PostgreSQL (import-chirps-and-export.py & export-data.R)",
                  "Calcul des moyennes communales via `rasterstats.zonal_stats`, insertion dans la table PostgreSQL `public.precipitation` (123 300 lignes de 1981 à 2026) "
                  "et export des fichiers JSON légers (`annual-precipitations.json`, `anomalies.json`, `precip-records.json`, `saisons.json`).", "7C3AED", "FAF5FF")
    add_step_card(doc, "4", "Restitution Cartographique & Serveurs (GeoServer WMS, FastAPI & React)",
                  "Publication des couches WMS `donnees_dynatsimo:chirps_*` (Port 8080), API REST FastAPI (Port 8000) et interface React-Leaflet "
                  "avec défilement temporel animé, arrêt dynamique au dernier mois disponible (Août 2026) et graphiques interactifs Recharts.", "E11D48", "FFF1F2")
    
    doc.add_page_break()
    
    # =============================================================
    # PARTIE 2 : MODULE VÉGÉTATION NDVI MODIS
    # =============================================================
    h_part2 = doc.add_paragraph()
    h_part2.paragraph_format.space_before = Pt(8)
    h_part2.paragraph_format.space_after = Pt(3)
    rh2 = h_part2.add_run("PARTIE II — MODULE VÉGÉTATION & BIOMASSE (MODIS NDVI)")
    rh2.font.name = "Calibri"
    rh2.font.size = Pt(16)
    rh2.bold = True
    rh2.font.color.rgb = PRIMARY
    
    # 2.1 Chaîne Abstraite MODIS
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("1. Chaîne de Traitement Abstraite (Niveau Conceptuel — MODIS)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["modis_abs"]):
        doc.add_picture(img_paths["modis_abs"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 2.A : Diagramme conceptuel de la chaîne abstraite MODIS (NDVI & 6 Classes)")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Mesure Multispectrale Solaire",
                  "Acquisition de la réflectance dans la bande Rouge (620–670 nm, absorption photosynthétique) et dans le Proche Infrarouge (841–876 nm, réflexion cellulaire mésophylle) "
                  "à une résolution spatiale de 250m par les capteurs MODIS Terra et Aqua.", "2563EB", "EFF6FF")
    add_step_card(doc, "2", "Correction Radiométrique & Débruitage Nuageux",
                  "Filtrage des contaminations atmosphériques via les masques de qualité QA (nuages, cirrus, ombres portées) et synthèse temporelle mensuelle "
                  "par composition de valeur maximale (MVC) sur l'AOI du Grand Sud.", "16A34A", "F0FDF4")
    add_step_card(doc, "3", "Calcul des Indices Biologiques de Végétation",
                  "Calcul matriciel du NDVI = (PIR - Rouge) / (PIR + Rouge), des indices de condition végétale VCI et de santé VHI, "
                  "avec agrégation zonale de la moyenne de vigueur foliaire par polygone communal (2000–2026).", "CA8A04", "FEFCE8")
    add_step_card(doc, "4", "Typologie & Discrétisation en 6 Classes de Biomasse",
                  "Segmentation de l'espace en 6 classes qualitatives : (1) Eau <0, (2) Sol nu / Très faible 0–0.2, (3) Fourré dégradé 0.2–0.4, "
                  "(4) Fourré arbustif / Cultures 0.4–0.6, (5) Forêt sèche / Canopée 0.6–0.8, (6) Végétation très dense >0.8.", "DB2777", "FDF2F8")
    add_step_card(doc, "5", "Évaluation de la Dégradation & Restitution",
                  "Diagnostic spatio-temporel de la perte de couvert végétal, suivi de la phénologie des cultures et restitution cartographique interactive.", "0F4C81", "F8FAFC")
    
    doc.add_page_break()
    
    # 2.2 Chaîne Concrète MODIS
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("2. Chaîne de Traitement Concrète (Implémentation Opérationnelle — MODIS)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["modis_cnc"]):
        doc.add_picture(img_paths["modis_cnc"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 2.B : Architecture technique et flux opérationnels du module MODIS NDVI")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Extraction Google Earth Engine (download_ndvi_modis_monthly_VF.py)",
                  "Requêtes cloud GEE sur la collection `MODIS/061/MOD13Q1` (250m), masquage bitmask des nuages, calcul du NDVI, découpage sur `3_region.shp` "
                  "et export de 319 GeoTIFF mensuels dans `NDVI_MODIS/YYYY/NDVI_MODIS_YYYY_MM.tif`.", "0284C7", "F0F9FF")
    add_step_card(doc, "2", "Segmentation 6 Classes & Tuilage PNG (export_ndvi_6classes.py & cluster_ndvi_raster_VF.py)",
                  "Reclassification matricielle NumPy en 6 classes, colorisation RGBA avec fond transparent NoData, export de 319 tuiles PNG dans `public/data/raster/ndvi_modis_6classes/` "
                  "et génération du catalogue `ndvi_classes_metadata.json`.", "0D9488", "F0FDF4")
    add_step_card(doc, "3", "Persistance PostgreSQL & Cache JSON (import-ndvi-from-gee.py)",
                  "Statistiques zonales par commune, insertion dans la table `public.ndvi_observations` et `public.vegetation_payload`, "
                  "avec export du fichier `vegetation-data.json`.", "7C3AED", "FAF5FF")
    add_step_card(doc, "4", "Restitution Web React & Comparaison Capteurs (React-Leaflet)",
                  "Affichage Leaflet avec ImageOverlay transparent ou flux GeoServer WMS, curseur d'opacité (0–100%), animation temporelle MODIS (319 périodes) "
                  "et comparateur multi-capteurs (Sentinel 10m vs Landsat 30m vs MODIS 250m).", "E11D48", "FFF1F2")
    
    doc.add_page_break()
    
    # =============================================================
    # PARTIE 3 : SYSTÈME GLOBAL DYNATSIMO (ENSEMBLE INTÉGRÉ)
    # =============================================================
    h_part3 = doc.add_paragraph()
    h_part3.paragraph_format.space_before = Pt(8)
    h_part3.paragraph_format.space_after = Pt(3)
    rh3 = h_part3.add_run("PARTIE III — SYSTÈME GLOBAL INTÉGRÉ DYNATSIMO")
    rh3.font.name = "Calibri"
    rh3.font.size = Pt(16)
    rh3.bold = True
    rh3.font.color.rgb = PRIMARY
    
    # 3.1 Chaîne Abstraite Globale
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("1. Chaîne de Traitement Abstraite Globale (Couplage Pluie + Végétation + Décision)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["ensemble_abs"]):
        doc.add_picture(img_paths["ensemble_abs"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 3.A : Diagramme conceptuel de la chaîne abstraite globale DYNATSIMO (Système Intégré)")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Acquisition Multi-Sources Couplée",
                  "Intégration synergique des flux pluviométriques (CHIRPS), des flux de réflectance végétale (MODIS, Sentinel, Landsat) "
                  "et du référentiel territorial vectoriel des 121 communes du Grand Sud.", "2563EB", "EFF6FF")
    add_step_card(doc, "2", "Normalisation & Synchronisation Spatio-Temporelle",
                  "Alignement calendaire mensuel commun (1981–2026), projection géodésique universelle WGS84 (EPSG:4326) et masquages géométriques unifiés sur l'AOI.", "16A34A", "F0FDF4")
    add_step_card(doc, "3", "Calculs Croisés & Analyse de Vulnérabilité",
                  "Couplage bivarié des séries temporelles : analyse conjointe du déficit pluviométrique (D_m, D%) et de la chute du NDVI, "
                  "avec mesure du déphasage pluie-biomasse pour anticiper les baisses de rendement agricole.", "CA8A04", "FEFCE8")
    add_step_card(doc, "4", "Modélisation Spatiale Intégrée",
                  "Croisement thématique continu (Isohyètes IDW) et catégoriel (6 classes NDVI) permettant d'isoler géographiquement les zones critiques en crise agro-climatique.", "DB2777", "FDF2F8")
    add_step_card(doc, "5", "Plateforme d'Aide à la Décision Multi-Échelles",
                  "Hiérarchisation administrative (Commune ➔ District ➔ Région), ciblage des communes prioritaires pour l'aide d'urgence et diffusion interactive.", "0F4C81", "F8FAFC")
    
    doc.add_page_break()
    
    # 3.2 Chaîne Concrète Globale
    h_sub = doc.add_paragraph()
    h_sub.paragraph_format.space_before = Pt(4)
    h_sub.paragraph_format.space_after = Pt(2)
    rs = h_sub.add_run("2. Chaîne de Traitement Concrète Globale (Architecture Technique Complète)")
    rs.font.name = "Calibri"
    rs.font.size = Pt(13)
    rs.bold = True
    rs.font.color.rgb = SECONDARY
    
    if os.path.exists(img_paths["ensemble_cnc"]):
        doc.add_picture(img_paths["ensemble_cnc"], width=Inches(6.6))
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(8)
        rc = p_cap.add_run("Figure 3.B : Architecture technique de bout en bout du système complet DYNATSIMO")
        rc.font.size = Pt(9)
        rc.italic = True
        rc.font.color.rgb = MUTED
        
    add_step_card(doc, "1", "Tier 1 — Ingestion & Sources de Données",
                  "Serveur UCSB HTTP (CHIRPS), Google Earth Engine Cloud API (MODIS/Sentinel/Landsat), Shapefile vectoriel `Regions 3/3_region.shp` "
                  "et orchestrateur de synchronisation `scripts/sync_pipeline.py`.", "0284C7", "F0F9FF")
    add_step_card(doc, "2", "Tier 2 — Traitements Scientifiques & Modélisation Python/R",
                  "Découpage Rasterio Mask, filtrage QA bitmask, interpolation SciPy IDW (`isohyette_chirps_VF.py`), tuilage 6 classes (`export_ndvi_6classes.py`), "
                  "statistiques zonales `rasterstats` et calcul des anomalies trentenaires.", "0D9488", "F0FDF4")
    add_step_card(doc, "3", "Tier 3 — Persistance, WMS & Serveurs d'API",
                  "Base PostgreSQL 15 / PostGIS (tables `communes`, `precipitation`, `ndvi_observations`), Serveur GeoServer WMS (Port 8080), "
                  "Serveur API FastAPI (`scripts/api-server.py` Port 8000) et cache public JSON optimisé.", "7C3AED", "FAF5FF")
    add_step_card(doc, "4", "Tier 4 — Application Web Interactive React / Vite",
                  "Front-End réactif avec 6 modules de navigation (Vue Complète, Cartographie, Statistiques, Base de Données, Guide), "
                  "React-Leaflet avec modes Choroplèthe/Isohyètes/NDVI, lecteur temporel animé intelligent (ajustement dynamique aux données réelles ex: Août 2026) "
                  "et graphiques décisionnels Recharts.", "E11D48", "FFF1F2")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # =============================================================
    # TABLEAU COMPARATIF RÉCAPITULATIF
    # =============================================================
    h_tab = doc.add_paragraph()
    h_tab.paragraph_format.space_before = Pt(8)
    h_tab.paragraph_format.space_after = Pt(3)
    rtab = h_tab.add_run("Synthèse des 6 Chaînes de Traitements Formalisées")
    rtab.font.name = "Calibri"
    rtab.font.size = Pt(14)
    rtab.bold = True
    rtab.font.color.rgb = PRIMARY
    
    tbl_s = doc.add_table(rows=4, cols=3)
    tbl_s.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_s.autofit = False
    
    headers_s = ["Module / Périmètre", "Chaîne Abstraite (Conceptuelle)", "Chaîne Concrète (Technique & Scripts)"]
    for c_idx, txt in enumerate(headers_s):
        cell = tbl_s.cell(0, c_idx)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(txt)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    s_rows = [
        ("Module CHIRPS (Pluviométrie)", "Figure 1.A : Infrarouge thermique ➔ Masquage AOI ➔ Normales trentenaires & Déficits D_m, D% ➔ IDW Isohyètes ➔ Diagnostic Sécheresse", "Figure 1.B : Ingestion HTTP UCSB ➔ rasterio.mask ➔ SciPy IDW ➔ PostgreSQL precipitation (123k) ➔ GeoServer WMS ➔ React Timeline"),
        ("Module MODIS (Végétation)", "Figure 2.A : Spectres Rouge/PIR ➔ Filtrage nuages QA ➔ NDVI/VCI/VHI ➔ Typologie 6 classes de biomasse ➔ Suivi Dégradation", "Figure 2.B : Google Earth Engine API ➔ Tuilage PNG 6 classes RGBA transparents ➔ PostGIS ndvi_observations ➔ React ImageOverlay & Comparateur capteurs"),
        ("Système Global DYNATSIMO", "Figure 3.A : Synergie Pluie + Végétation ➔ Synchronisation mensuelle ➔ Couplage bivarié Pluie/NDVI ➔ Modélisation continue/catégorielle ➔ Aide à la Décision", "Figure 3.B : Pipeline complet 4 tiers (Ingestion multi-sources ➔ Scripts Python/R ➔ PostGIS/GeoServer/FastAPI ➔ Application React/Leaflet/Recharts)")
    ]
    
    widths_s = [Inches(1.8), Inches(2.5), Inches(2.5)]
    for r_idx, r_val in enumerate(s_rows, start=1):
        for c_idx, val in enumerate(r_val):
            cell = tbl_s.cell(r_idx, c_idx)
            cell.width = widths_s[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_TEXT
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = PRIMARY
                
    set_table_borders(tbl_s, color="CBD5E1", sz="4")
    
    try:
        doc.save(docx_path)
        print(f"Document Word officiel généré avec succès : {docx_path}")
    except PermissionError:
        alt_path = os.path.join(os.getcwd(), "Formalisation_Chaines_Traitements_DYNATSIMO.docx")
        doc.save(alt_path)
        print(f"Fichier enregistré sous le nom alternatif : {alt_path}")

if __name__ == "__main__":
    scratch_dir = os.path.join(os.getcwd(), "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    
    img_paths = {
        "chirps_abs": os.path.join(scratch_dir, "fig1_chirps_abstraite.png"),
        "chirps_cnc": os.path.join(scratch_dir, "fig2_chirps_concrete.png"),
        "modis_abs": os.path.join(scratch_dir, "fig3_modis_abstraite.png"),
        "modis_cnc": os.path.join(scratch_dir, "fig4_modis_concrete.png"),
        "ensemble_abs": os.path.join(scratch_dir, "fig5_ensemble_abstraite.png"),
        "ensemble_cnc": os.path.join(scratch_dir, "fig6_ensemble_concrete.png"),
    }
    
    print("1. Génération des 6 figures matplotlib...")
    fig_chirps_abstraite(img_paths["chirps_abs"])
    fig_chirps_concrete(img_paths["chirps_cnc"])
    fig_modis_abstraite(img_paths["modis_abs"])
    fig_modis_concrete(img_paths["modis_cnc"])
    fig_ensemble_abstraite(img_paths["ensemble_abs"])
    fig_ensemble_concrete(img_paths["ensemble_cnc"])
    
    print("2. Compilation du document Word avec les 6 figures et explications...")
    docx_file = os.path.join(os.getcwd(), "Formalisation_Chaines_Traitements_DYNATSIMO.docx")
    build_formalization_docx(docx_file, img_paths)
