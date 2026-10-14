# -*- coding: utf-8 -*-
"""
Script de génération du document Word complet :
"Chaînes de Traitements (Abstraite et Concrète) du Projet DYNATSIMO"
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

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

def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
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

def add_callout_box(doc, title, text, bg_color="F0F9FF", border_color="0284C7", icon="📌"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.8)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=180, right=160)
    
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
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_t = p.add_run(f"{icon} {title}")
    run_t.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(15, 76, 129)
    
    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(2)
    run_b = p_body.add_run(text)
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(10)
    run_b.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def generate_document(output_path):
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
    
    PRIMARY = RGBColor(15, 76, 129)      # Bleu Profond #0F4C81
    SECONDARY = RGBColor(13, 148, 136)   # Vert Émeraude / Sarcelle #0D9488
    DARK_TEXT = RGBColor(30, 41, 59)     # Ardoise Foncé #1E293B
    MUTED = RGBColor(100, 116, 139)      # Gris Moyen #64748B
    DANGER = RGBColor(225, 29, 72)       # Rouge Rubis #E11D48
    
    # Titre Principal
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    run_title = p_title.add_run("DYNATSIMO — CHAÎNES DE TRAITEMENTS")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(22)
    run_title.font.bold = True
    run_title.font.color.rgb = PRIMARY
    
    # Sous-titre
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(10)
    run_sub = p_sub.add_run("Architecture Méthodologique & Implémentation Opérationnelle des Données Géospatiales")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = SECONDARY
    
    # Fiche d'identification
    tbl_meta = doc.add_table(rows=2, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    
    meta_info = [
        [("Projet :", " DYNATSIMO (Dynamique Spatio-Temporelle du Sud de Madagascar)"), ("Domaine :", " Télédétection, Climatologie & Analyse Bio-végétale")],
        [("Zone d'étude :", " Grand Sud de Madagascar (Androy, Anosy, Atsimo-Andrefana)"), ("Horizon temporel :", " 1981 – 2026 (Précipitations CHIRPS) & 2000 – 2026 (NDVI MODIS/Landsat/Sentinel)")]
    ]
    
    for r_idx, row in enumerate(tbl_meta.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(3.4)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            lbl, val = meta_info[r_idx][c_idx]
            r_lbl = p.add_run(lbl)
            r_lbl.bold = True
            r_lbl.font.size = Pt(9.5)
            r_lbl.font.color.rgb = PRIMARY
            r_val = p.add_run(val)
            r_val.font.size = Pt(9.5)
            r_val.font.color.rgb = DARK_TEXT
            
    set_table_borders(tbl_meta, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # -------------------------------------------------------------
    # 1. INTRODUCTION & CONTEXTE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("1. Contexte & Objectifs du Projet DYNATSIMO")
    run_h1.font.name = "Calibri"
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Le projet DYNATSIMO a été conçu pour fournir un système d'information géographique (SIG) et décisionnel dédié "
        "à la surveillance continue des sécheresses, de la pluviométrie et de l'activité chlorophyllienne dans le Grand Sud de Madagascar "
        "(régions Androy, Anosy et Atsimo-Andrefana). Cette région semi-aride est régulièrement confrontée à des déficits pluviométriques sévères "
        "et récurrents (notamment la sécheresse triennale historique de 2020–2022)."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "Pour répondre aux besoins des décideurs, agronomes et acteurs humanitaires, le système structure ses flux de données "
        "à travers deux niveaux complémentaires de modélisation : une "
    )
    p.add_run("chaîne de traitement abstraite (conceptuelle)").bold = True
    p.add_run(" qui définit la logique théorique de transformation des données géospatiales, et une ")
    p.add_run("chaîne de traitement concrète (opérationnelle)").bold = True
    p.add_run(" qui détaille l'implémentation logicielle, les scripts, bases de données et services interactifs.")
    
    # -------------------------------------------------------------
    # 2. CHAÎNE DE TRAITEMENT ABSTRAITE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("2. Chaîne de Traitement Abstraite (Niveau Conceptuel)")
    run_h1.font.name = "Calibri"
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La chaîne de traitement abstraite décrit le modèle logique et théorique de la donnée, indépendamment des outils technologiques "
        "ou langages de programmation choisis. Elle formalise les 5 phases scientifiques fondamentales requises pour transformer des signaux "
        "satellitaires bruts en indicateurs décisionnels d'alerte précoce."
    )
    
    # Phase A1
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Phase 1 : Acquisition & Télédétection Multi-Sources")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Télédétection Optique Multispectrale : Captation de la réflectance au sol dans les bandes Rouge (0.64–0.67 µm, absorption par la chlorophylle) "
        "et Proche Infrarouge (PIR, 0.85–0.88 µm, forte réflectance de la structure cellulaire mésophylle des feuilles vivantes).\n"
        "• Estimation Pluviométrique Spatiale : Mesure indirecte des précipitations combinant l'imagerie infrarouge thermique géostationnaire (température au sommet des nuages convectifs) "
        "et les réanalyses atmosphériques couplées aux observations de stations météorologiques terrestres.\n"
        "• Référentiel Géospatial Administratif : Délimitation vectorielle des mailles territoriales (polygones des Communes, Districts et Régions)."
    )
    
    # Phase A2
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Phase 2 : Prétraitement & Harmonisation Spatio-Temporelle")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Découpage & Emprise (Spatial Clipping) : Extraction stricte des pixels sur l'Aire d'Intérêt (AOI) du Grand Sud.\n"
        "• Filtrage Radiométrique & Masquage des Nuages : Élimination des pixels contaminés par les nuages, ombres portées et cirrus via des masques de qualité atmosphérique.\n"
        "• Standardisation Géodésique & Temporelle : Harmonisation dans un système de coordonnées de référence commun (WGS84 EPSG:4326) et agrégation sous un pas de temps mensuel uniforme (12 périodes par an)."
    )
    
    # Phase A3
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Phase 3 : Calcul des Variables Bioclimatiques & Statistiques Zonales")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Indice de Végétation par Différence Normalisée (NDVI) : Évaluation de la vigueur de la couverture végétale :\n"
        "      NDVI = (PIR - Rouge) / (PIR + Rouge)\n"
        "• Indice de Condition de la Végétation (VCI) & Santé Végétale (VHI) : Mesure relative de l'état de la biomasse par rapport aux extremums historiques :\n"
        "      VCI = (NDVI_obs - NDVI_min) / (NDVI_max - NDVI_min) × 100\n"
        "• Précipitations & Anomalies Pluviométriques : Établissement de la normale de référence trentenaire (P_ref,m sur 1981–2025) et calcul des écarts volumétriques (D_m) et relatifs (D%) :\n"
        "      D_m = P_obs,m - P_ref,m  (en mm)  |  D% = (D_m / P_ref,m) × 100  (en %)\n"
        "• Agrégation Zonale Vectorielle : Calcul de la valeur moyenne, minimale et maximale de chaque variable surfacique pour chaque commune du territoire."
    )
    
    # Phase A4
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Phase 4 : Modélisation Spatiale & Typologie Bio-Végétale")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Interpolation Spatiale Continue (IDW - Inverse Distance Weighting) : Reconstruction d'un champ continu de précipitations à partir des barycentres communaux pour générer les isolignes de pluie (isohyètes par pas de 50 mm).\n"
        "• Typologie en 6 Classes de Végétation : Discrétisation radiométrique de l'espace en 6 classes qualitatives : (1) Eau / Zones humides (<0), (2) Sol nu / Très faible (0–0.2), (3) Fourrés dégradés (0.2–0.4), (4) Fourrés arbustifs / Cultures (0.4–0.6), (5) Forêt sèche / Canopée (0.6–0.8), (6) Végétation très dense (0.8–1.0)."
    )
    
    # Phase A5
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(8)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Phase 5 : Structuration Relationnelle & Restitution Décisionnelle")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "• Hiérarchisation Multi-Échelles : Agrégation gigogne des indicateurs : Commune → District → Région → Grand Sud.\n"
        "• Matrice de Gravité de la Sécheresse : Classification des anomalies en 5 seuils : Déficit Extrême (<-50%), Déficit Sévère (-50% à -25%), Déficit Modéré (-25% à -10%), Normal (-10% à +10%), Excédent (>+10%).\n"
        "• Restitution Dynamique Spatio-Temporelle : Cartographie choroplèthe, courbes isohyètes, défilement temporel mois par mois et séries chronologiques interactives."
    )
    
    # Tableau Récapitulatif Abstrait
    p_tbl_title = doc.add_paragraph()
    p_tbl_title.paragraph_format.space_before = Pt(8)
    p_tbl_title.paragraph_format.space_after = Pt(4)
    run_tt = p_tbl_title.add_run("Tableau 1 : Synthèse de la Chaîne de Traitement Abstraite")
    run_tt.bold = True
    run_tt.font.size = Pt(11)
    run_tt.font.color.rgb = PRIMARY
    
    tbl_abs = doc.add_table(rows=6, cols=4)
    tbl_abs.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_abs.autofit = False
    
    headers_abs = ["Phase Conceptuelle", "Données en Entrée", "Opérations & Modèles Logiques", "Sortie Conceptuelle"]
    for c_idx, text in enumerate(headers_abs):
        cell = tbl_abs.cell(0, c_idx)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rows_abs_data = [
        ("1. Acquisition", "Spectres Rouge/PIR, Infrarouge thermique pluie, Vecteurs limites", "Télédétection optique, réanalyse spatiale, découpage AOI", "Matrices brutes géoréférencées"),
        ("2. Prétraitement", "Rasters bruts multi-satellites, Shapefile AOI", "Masquage nuageux QA, reprojection WGS84, composition mensuelle", "Rasters corrigés normalisés"),
        ("3. Extraction", "Rasters normalisés, Polygones des communes", "Calculs NDVI, VCI, VHI, Climatologie trentenaire, anomalies D_m, D%", "Séries d'indicateurs par commune"),
        ("4. Modélisation", "Séries communales, Rasters NDVI", "Interpolation IDW (Isohyètes), Discrétisation 6 classes biomasse", "Isohyètes continues & Cartes 6 classes"),
        ("5. Restitution", "Indicateurs spatiaux, matrices temporelles", "Agrégation hiérarchique, matrice de gravité sécheresse, animation", "Tableaux de bord & Cartographie interactive")
    ]
    
    col_widths_abs = [Inches(1.4), Inches(1.8), Inches(2.2), Inches(1.4)]
    for r_idx, row_data in enumerate(rows_abs_data, start=1):
        for c_idx, val in enumerate(row_data):
            cell = tbl_abs.cell(r_idx, c_idx)
            cell.width = col_widths_abs[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_TEXT
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = PRIMARY
                
    set_table_borders(tbl_abs, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # -------------------------------------------------------------
    # 3. CHAÎNE DE TRAITEMENT CONCRÈTE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("3. Chaîne de Traitement Concrète (Implémentation Opérationnelle DYNATSIMO)")
    run_h1.font.name = "Calibri"
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La chaîne de traitement concrète détaille la mise en œuvre logicielle réelle au sein du projet DYNATSIMO : les sources exactes, "
        "les scripts Python et R exécutés, les bibliothèques scientifiques (Rasterio, GeoPandas, Scipy, GDAL), la base PostgreSQL/PostGIS, "
        "le serveur cartographique GeoServer WMS et l'application Web React/Vite."
    )
    
    # Architecture Pipeline
    add_callout_box(
        doc,
        title="Architecture Technique du Pipeline DYNATSIMO",
        text="• Ingestion & Télédétection : Scripts Python automatisés (Requests, Google Earth Engine API, Rasterio, Geopandas).\n"
             "• Calcul Spatial & SIG : Algorithmes SciPy (IDW), Rasterstats (Zonal Statistics), GDAL/OGR (Contour vectoriel).\n"
             "• Stockage & Diffusion API : Base PostgreSQL 15 + PostGIS, Serveur FastAPI (scripts/api-server.py) + Cache JSON statique.\n"
             "• Cartographie Serveur : GeoServer WMS (espace de travail donnees_dynatsimo).\n"
             "• Front-End Réactif : React 18, Vite 8, Leaflet, React-Leaflet, Recharts.",
        bg_color="F0FDF4",
        border_color="0D9488",
        icon="⚙️"
    )
    
    # Étape C1
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Étape 1 : Collecte & Ingestion Automatisée des Données Brutes")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "1.1. Précipitations CHIRPS v2.0 (1981–2026) :\n"
        "   • Script : `scripts/download_chirps_monthly_VF.py`\n"
        "   • Source : Climate Hazards Center UCSB (`https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs`)\n"
        "   • Processus : Téléchargement mensuel des `.tif.gz`, décompression GZIP, découpage géométrique avec `rasterio.mask.mask()` "
        "en utilisant le shapefile `Regions 3/3_region.shp`. Résolution spatiale 0.05° (~5 km).\n"
        "   • Sortie : Fichiers `CHIRPS_data/chirps-v2.0.YYYY.MM.tif` (1981-01 à 2026-08).\n\n"
        "1.2. Activité Végétale NDVI Multi-Capteurs (2000–2026) :\n"
        "   • Scripts : `scripts/download_ndvi_modis_monthly_VF.py`, `scripts/download_sentinnel_monthly_VF.py`, `scripts/download_ndvi_landsat_monthly_VF.py`\n"
        "   • Sources : Google Earth Engine API (MODIS MOD13Q1 250m, Landsat 5/7/8/9 30m, Sentinel-2 10m).\n"
        "   • Processus : Filtrage des nuages via masques QA, calcul matriciel NDVI = (B_nir - B_red) / (B_nir + B_red), composition mensuelle "
        "et exportation GeoTIFF.\n"
        "   • Sortie : `NDVI_MODIS/YYYY/NDVI_MODIS_YYYY_MM.tif`, `NDVI_LANDSAT/`, `NDVI_SENTINEL/`."
    )
    
    # Étape C2
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Étape 2 : Interpolation Spatiale IDW & Génération des Isohyètes")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Scripts : `scripts/isohyette_chirps_VF.py` et `scripts/export_isohyetes.py`\n"
        "• Algorithme IDW : Interpolation par pondération inverse de la distance avec exposant p=2 sur une grille fine régulière (35x35 à 100x100 points).\n"
        "• Vectorisation des Isolignes : Extraction des courbes de niveau de précipitations (pas de 50 mm) par interpolation linéaire ou contours GDAL.\n"
        "• Sortie Web : Fichiers GeoJSON vectoriels dans `public/data/isohyetes/` et index de métadonnées `public/data/isohyetes_metadata.json` "
        "(contenant pour chaque mois/année/décennie : les URL GeoJSON, min, max et moyenne de pluie)."
    )
    
    # Étape C3
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Étape 3 : Classification NDVI 6 Classes & Génération des Tuiles PNG")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Scripts : `scripts/export_ndvi_6classes.py` et `scripts/cluster_ndvi_raster_VF.py`\n"
        "• Segmentation Matricielle : Reclassification numpy du raster NDVI en 6 classes d'état de végétation.\n"
        "• Colorisation RGBA & Tuilage Web : Application de la palette officielle (Bleu eau, Marron sol nu, Orange dégradé, Jaune-vert arbustif, Vert canopée, Vert foncé forêt dense) "
        "avec canal alpha transparent pour le fond (NoData = transparent).\n"
        "• Sortie Web : Images PNG géoréférencées dans `public/data/raster/ndvi_modis_6classes/YYYY/ndvi_class_YYYY_MM.png` "
        "et fichier de métadonnées `public/data/ndvi_classes_metadata.json` (319 périodes mensuelles documentées de 2000 à 2026)."
    )
    
    # Étape C4
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Étape 4 : Statistiques Zonales, Base PostgreSQL & Export JSON")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Scripts : `scripts/import-chirps-and-export.py` et `scripts/export-data.R`\n"
        "• Calcul Zonal : Utilisation de `rasterstats.zonal_stats` pour croiser les rasters mensuels avec les polygones des 121 communes du Grand Sud.\n"
        "• Base PostgreSQL/PostGIS :\n"
        "   - Table `public.communes` : Code, nom, district, région, géométrie vectorielle.\n"
        "   - Table `public.precipitation` : Enregistrements mensuels (123 300 lignes, 1981–2026).\n"
        "   - Table `public.ndvi_observations` : Valeurs NDVI moyennes mensuelles par commune et capteur.\n"
        "• Génération des Fichiers JSON de Restitution (`public/data/`) :\n"
        "   - `overview.json` : Indicateurs clés consolidés pour le tableau de bord.\n"
        "   - `communes.geojson` : Géométries vectorielles complètes avec attributs.\n"
        "   - `annual-precipitations.json` : Cumuls annuels par commune.\n"
        "   - `monthly-climatology.json` : Moyenne climatologique historique (1981–2025).\n"
        "   - `anomalies.json` : Déficits hydriques D_m et pourcentages d'écart D%.\n"
        "   - `precip-records.json` : Série mensuelle exhaustive complète pour l'animation."
    )
    
    # Étape C5
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(10)
    h2.paragraph_format.space_after = Pt(2)
    run_h2 = h2.add_run("Étape 5 : Serveurs de Données & Restitution Front-End React")
    run_h2.font.name = "Calibri"
    run_h2.font.size = Pt(12)
    run_h2.font.bold = True
    run_h2.font.color.rgb = SECONDARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "• Serveur API REST Python (`scripts/api-server.py`) : Serveur FastAPI / Uvicorn (Port 8000) fournissant `/api/data` "
        "et les points d'entrée de synchronisation dynamique `/api/sync/all`, `/api/sync/precipitation`.\n"
        "• Serveur Cartographique GeoServer (Port 8080) : Publication des couches WMS `donnees_dynatsimo` pour l'affichage raster en tuiles tuilées dynamiques.\n"
        "• Application Web React (`src/main.jsx`) :\n"
        "   - Module Cartographie : Choix entre Choroplèthe communale, Isohyètes CHIRPS et NDVI MODIS 6 classes.\n"
        "   - Lecteur Temporel / Timeline : Contrôleur interactif avec vitesse réglable, scrubber et synchronisation mois/année.\n"
        "   - Filtrage Dynamique Intelligent : Détection automatique des mois disponibles dans la base de données (ex: limitation automatique à Août pour 2026).\n"
        "   - Tableaux de Bord & Graphiques : Séries temporelles Recharts, comparaison capteurs (Landsat vs Sentinel vs MODIS), export CSV."
    )
    
    # Tableau Récapitulatif Concret
    p_tbl_title2 = doc.add_paragraph()
    p_tbl_title2.paragraph_format.space_before = Pt(10)
    p_tbl_title2.paragraph_format.space_after = Pt(4)
    run_tt2 = p_tbl_title2.add_run("Tableau 2 : Synthèse de la Chaîne de Traitement Concrète")
    run_tt2.bold = True
    run_tt2.font.size = Pt(11)
    run_tt2.font.color.rgb = PRIMARY
    
    tbl_cnc = doc.add_table(rows=6, cols=4)
    tbl_cnc.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cnc.autofit = False
    
    headers_cnc = ["Étape Concrète", "Scripts & Technologies", "Entrées & Formats", "Livrables / Sorties Produits"]
    for c_idx, text in enumerate(headers_cnc):
        cell = tbl_cnc.cell(0, c_idx)
        set_cell_background(cell, "0D9488")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rows_cnc_data = [
        ("Étape 1 : Collecte", "Python, Requests, Earth Engine API, GZIP", "CHIRPS v2.0 (.tif.gz), MODIS MOD13Q1, Sentinel-2, Landsat", "Rasters GeoTIFF découpés dans CHIRPS_data/ et NDVI_MODIS/"),
        ("Étape 2 : Isohyètes", "Python (SciPy IDW, GeoPandas, GDAL)", "Barycentres communaux, Cumuls pluviométriques", "GeoJSON isohyètes dans public/data/isohyetes/ & isohyetes_metadata.json"),
        ("Étape 3 : 6 Classes NDVI", "Python (NumPy, PIL, Rasterio)", "Rasters NDVI bruts (250m)", "Tuiles PNG transparentes RGBA & ndvi_classes_metadata.json"),
        ("Étape 4 : Base & Export", "Python (Rasterstats, Psycopg2), PostgreSQL/PostGIS, R", "Shapefile communes, Rasters mensuels", "Tables PostgreSQL (communes, precipitation) & 10 fichiers JSON publics"),
        ("Étape 5 : Web & SIG", "React 18, Vite, Leaflet, Recharts, FastAPI, GeoServer", "Fichiers JSON, Flux GeoServer WMS, API /api/data", "Application Web interactive DYNATSIMO avec timeline")
    ]
    
    col_widths_cnc = [Inches(1.4), Inches(1.8), Inches(1.8), Inches(1.8)]
    for r_idx, row_data in enumerate(rows_cnc_data, start=1):
        for c_idx, val in enumerate(row_data):
            cell = tbl_cnc.cell(r_idx, c_idx)
            cell.width = col_widths_cnc[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 1 else "F0FDF4")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_TEXT
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = SECONDARY
                
    set_table_borders(tbl_cnc, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # -------------------------------------------------------------
    # 4. MATRICE DE CORRESPONDANCE (ABSTRAIT VS CONCRET)
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("4. Matrice de Correspondance (Abstrait vs Concret)")
    run_h1.font.name = "Calibri"
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Ce tableau établit la correspondance directe entre les concepts scientifiques de la chaîne abstraite "
        "et les composants techniques réels développés dans le projet DYNATSIMO."
    )
    
    tbl_mat = doc.add_table(rows=6, cols=3)
    tbl_mat.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_mat.autofit = False
    
    headers_mat = ["Phase Abstraite (Concept)", "Composant Concret DYNATSIMO", "Description de l'Implémentation"]
    for c_idx, text in enumerate(headers_mat):
        cell = tbl_mat.cell(0, c_idx)
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rows_mat_data = [
        ("Télédétection Multi-Sources", "download_chirps_monthly_VF.py & GEE API", "Requêtes automatisées vers le serveur UCSB et l'infrastructure Google Cloud"),
        ("Normalisation & Masquage", "Rasterio Mask & GDAL", "Découpage selon le shapefile 3_region.shp et conversion EPSG:4326"),
        ("Indices Bioclimatiques", "Rasterstats, NumPy & export-data.R", "Calcul du NDVI, moyennes zonales communales, D_m et D% par rapport à 1981–2025"),
        ("Modélisation Spatiale", "isohyette_chirps_VF.py & export_ndvi_6classes.py", "Interpolation IDW p=2 et reclassification en 6 catégories PNG transparentes"),
        ("Diffusion & Restitution", "React 18 + Leaflet + Recharts + FastAPI", "Interface Web moderne avec timeline, sélecteur dynamique de mois et cartes interactives")
    ]
    
    col_widths_mat = [Inches(1.8), Inches(2.2), Inches(2.8)]
    for r_idx, row_data in enumerate(rows_mat_data, start=1):
        for c_idx, val in enumerate(row_data):
            cell = tbl_mat.cell(r_idx, c_idx)
            cell.width = col_widths_mat[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_TEXT
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = PRIMARY
                
    set_table_borders(tbl_mat, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(14)
    
    # -------------------------------------------------------------
    # 5. CONCLUSION
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(4)
    run_h1 = h1.add_run("5. Conclusion & Perspectives")
    run_h1.font.name = "Calibri"
    run_h1.font.size = Pt(15)
    run_h1.font.bold = True
    run_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "L'articulation rigoureuse entre la chaîne de traitement abstraite et sa concrétisation logicielle confère à DYNATSIMO "
        "une robustesse scientifique et opérationnelle éprouvée. L'intégration de pipelines de mise à jour incrémentielle "
        "(détection automatique des nouveaux mois publiés, synchronisation PostgreSQL et actualisation des visualisations React) "
        "en fait un outil pérenne et évolutif pour la gestion anticipée des risques agro-climatiques dans le Sud de Madagascar."
    )
    
    # Sauvegarde
    doc.save(output_path)
    print(f"Document généré avec succès : {output_path}")

if __name__ == "__main__":
    output_file = os.path.join(os.getcwd(), "Chaines_de_Traitement_DYNATSIMO.docx")
    generate_document(output_file)
