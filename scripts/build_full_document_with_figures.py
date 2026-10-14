# -*- coding: utf-8 -*-
"""
Script complet pour générer les figures graphiques (haute définition 300 DPI)
et compiler le document Word officiel : "Chaines_de_Traitement_DYNATSIMO.docx"
avec intégration des figures et explications méthodologiques structurées.
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
# 1. GÉNÉRATION DES FIGURES MATPLOTLIB
# ----------------------------------------------------------------------

def generate_figure_abstraite(output_path):
    fig = plt.figure(figsize=(14, 11), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    # Titre du diagramme
    ax.text(50, 96.5, "CHAÎNE DE TRAITEMENT ABSTRAITE (NIVEAU CONCEPTUEL)",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F4C81',
            fontfamily='sans-serif')
    ax.text(50, 93.8, "Flux Logique & Méthodologique de Transformation des Données Géospatiales",
            ha='center', va='center', fontsize=11, fontstyle='italic', color='#0D9488',
            fontfamily='sans-serif')

    ax.plot([10, 90], [91.5, 91.5], color='#CBD5E1', lw=1.5)

    boxes_data = [
        {
            "num": "1",
            "tag": "ACQUISITION",
            "title": "ACQUISITION & TÉLÉDÉTECTION MULTI-SOURCES",
            "y": 79,
            "bg": "#EFF6FF",
            "border": "#2563EB",
            "items": [
                "• Réflectances optiques multispectrales (Bandes Rouge & Proche Infrarouge PIR)",
                "• Estimations pluviométriques satellitaires (Infrarouge thermique & Réanalyses)",
                "• Référentiel vectoriel des limites administratives (Communes, Districts, Régions)"
            ],
            "in_out": "Entrées : Signaux bruts capteurs   ➔   Sortie : Matrices brutes géoréférencées"
        },
        {
            "num": "2",
            "tag": "PRÉTRAITEMENT",
            "title": "PRÉTRAITEMENT & HARMONISATION SPATIO-TEMPORELLE",
            "y": 62,
            "bg": "#F0FDF4",
            "border": "#16A34A",
            "items": [
                "• Découpage spatial strict sur l'Aire d'Intérêt (AOI Grand Sud de Madagascar)",
                "• Masquage des artéfacts atmosphériques (Nuages, ombres et cirrus via masques QA)",
                "• Reprojection cartographique uniforme (WGS84 EPSG:4326) et normalisation mensuelle"
            ],
            "in_out": "Entrées : Rasters bruts   ➔   Sortie : Rasters corrigés et normalisés par mois"
        },
        {
            "num": "3",
            "tag": "INDICES",
            "title": "CALCUL DES INDICES BIOCLIMATIQUES & STATISTIQUES ZONALES",
            "y": 45,
            "bg": "#FEFCE8",
            "border": "#CA8A04",
            "items": [
                "• Indice de végétation : NDVI = (PIR - Rouge) / (PIR + Rouge) & Santé végétale (VCI, VHI)",
                "• Climatologie de référence trentenaire : Moyenne historique de pluie P_ref (1981–2025)",
                "• Déficits hydriques communaux : Déficit net D_m = P_obs - P_ref (mm) et relatif D% (%)"
            ],
            "in_out": "Entrées : Rasters normalisés   ➔   Sortie : Séries temporelles agrégées par commune"
        },
        {
            "num": "4",
            "tag": "MODÉLISATION",
            "title": "MODÉLISATION SPATIALE CONTINUE & TYPOLOGIE BIO-VÉGÉTALE",
            "y": 28,
            "bg": "#FDF2F8",
            "border": "#DB2777",
            "items": [
                "• Interpolation spatiale continue par IDW (Inverse Distance Weighting, puissance p=2)",
                "• Génération des courbes et champs d'isohyètes (pas régulier de 50 mm de pluie)",
                "• Discrétisation radiométrique de la biomasse en 6 classes d'état de végétation"
            ],
            "in_out": "Entrées : Données zonales   ➔   Sortie : Isolignes isohyètes & Cartes thématiques"
        },
        {
            "num": "5",
            "tag": "DÉCISION",
            "title": "STRUCTURATION RELATIONNELLE & RESTITUTION DÉCISIONNELLE",
            "y": 11,
            "bg": "#F8FAFC",
            "border": "#0F4C81",
            "items": [
                "• Hiérarchisation gigogne multi-échelles (Échelle Commune ➔ District ➔ Région)",
                "• Grille d'évaluation de la sévérité des sécheresses (Déficit Modéré, Sévère, Extrême)",
                "• Restitution dynamique spatio-temporelle (Cartographie choroplèthe, timeline interactive)"
            ],
            "in_out": "Entrées : Modèles spatiaux   ➔   Sortie : Indicateurs d'aide à la décision & Tableaux de bord"
        }
    ]

    for b in boxes_data:
        y_center = b["y"]
        height = 13.2
        width = 86
        x_left = 7
        
        box = FancyBboxPatch((x_left, y_center - height/2), width, height,
                             boxstyle="round,pad=0.6,rounding_size=1.2",
                             facecolor=b["bg"], edgecolor=b["border"], linewidth=2, zorder=2)
        ax.add_patch(box)
        
        badge = FancyBboxPatch((x_left + 1.2, y_center + height/2 - 3.2), 3.2, 2.4,
                               boxstyle="round,pad=0.3,rounding_size=0.6",
                               facecolor=b["border"], edgecolor='none', zorder=3)
        ax.add_patch(badge)
        ax.text(x_left + 2.8, y_center + height/2 - 2.0, b["num"],
                ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF', zorder=4)
        
        ax.text(x_left + 5.5, y_center + height/2 - 2.0, f"PHASE {b['num']} : {b['title']}",
                ha='left', va='center', fontsize=11, fontweight='bold', color=b["border"], zorder=4)
        
        y_text = y_center + 1.6
        for item in b["items"]:
            ax.text(x_left + 3.0, y_text, item,
                    ha='left', va='center', fontsize=8.8, color='#1E293B', zorder=4)
            y_text -= 2.3
            
        sub_box = FancyBboxPatch((x_left + 2.0, y_center - height/2 + 0.6), width - 4.0, 1.9,
                                 boxstyle="round,pad=0.2,rounding_size=0.4",
                                 facecolor='#FFFFFF', edgecolor=b["border"], linewidth=0.8, zorder=3)
        ax.add_patch(sub_box)
        ax.text(x_left + 3.0, y_center - height/2 + 1.55, f"FLUX : {b['in_out']}",
                ha='left', va='center', fontsize=8.0, fontweight='bold', color='#475569', zorder=4)

    arrow_y_pairs = [(72.4, 68.6), (55.4, 51.6), (38.4, 34.6), (21.4, 17.6)]
    for y_top, y_bot in arrow_y_pairs:
        arrow = FancyArrowPatch((50, y_top), (50, y_bot),
                                arrowstyle='simple,head_width=6,head_length=6',
                                facecolor='#0284C7', edgecolor='none', zorder=5)
        ax.add_patch(arrow)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()

def generate_figure_concrete(output_path):
    fig = plt.figure(figsize=(15, 12), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')
    
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')
    
    ax.text(50, 97.0, "CHAÎNE DE TRAITEMENT CONCRÈTE (ARCHITECTURE TECHNIQUE DYNATSIMO)",
            ha='center', va='center', fontsize=15, fontweight='bold', color='#0F4C81',
            fontfamily='sans-serif')
    ax.text(50, 94.3, "Pipeline Logiciel, Formats de Données, Scripts Python/R, PostgreSQL & Front-End React",
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color='#0D9488',
            fontfamily='sans-serif')
    ax.plot([5, 95], [92.2, 92.2], color='#CBD5E1', lw=1.5)

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
        hdr = FancyBboxPatch((cx, 86.5), cw, 4.2,
                             boxstyle="round,pad=0.3,rounding_size=0.8",
                             facecolor=col["color"], edgecolor='none', zorder=2)
        ax.add_patch(hdr)
        ax.text(cx + cw/2, 88.6, col["title"],
                ha='center', va='center', fontsize=9.5, fontweight='bold', color='#FFFFFF', zorder=3)
        
        y_pos = [68, 48, 28, 8]
        for idx, (b_title, b_desc, b_col) in enumerate(col["boxes"]):
            y_c = y_pos[idx]
            h = 16.5
            box = FancyBboxPatch((cx, y_c), cw, h,
                                 boxstyle="round,pad=0.4,rounding_size=0.8",
                                 facecolor=col["bg"], edgecolor=col["color"], linewidth=1.2, zorder=2)
            ax.add_patch(box)
            
            ax.text(cx + 1.0, y_c + h - 2.2, b_title,
                    ha='left', va='center', fontsize=8.5, fontweight='bold', color=col["color"], zorder=3)
            
            ax.text(cx + 1.0, y_c + h/2 - 1.2, b_desc,
                    ha='left', va='center', fontsize=7.2, color='#1E293B', linespacing=1.35, zorder=3)

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

# ----------------------------------------------------------------------
# 2. CONSTRUCTION DU DOCUMENT WORD (.DOCX)
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
    set_cell_margins(cell, top=120, bottom=120, left=160, right=140)
    
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
    p.paragraph_format.space_after = Pt(3)
    r_t = p.add_run(f"Étape {num} : {title}")
    r_t.bold = True
    r_t.font.name = "Calibri"
    r_t.font.size = Pt(11)
    r_t.font.color.rgb = RGBColor(15, 76, 129)
    
    p_b = cell.add_paragraph()
    p_b.paragraph_format.space_before = Pt(0)
    p_b.paragraph_format.space_after = Pt(0)
    r_b = p_b.add_run(description)
    r_b.font.name = "Calibri"
    r_b.font.size = Pt(9.5)
    r_b.font.color.rgb = RGBColor(51, 65, 85)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_complete_word_document(docx_path, img_abs_path, img_cnc_path):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        
    PRIMARY = RGBColor(15, 76, 129)
    SECONDARY = RGBColor(13, 148, 136)
    DARK_TEXT = RGBColor(30, 41, 59)
    MUTED = RGBColor(100, 116, 139)
    
    # ---------------- Titre Principal ----------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(2)
    run_t = p_title.add_run("PROJET DYNATSIMO — CHAÎNES DE TRAITEMENTS")
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(22)
    run_t.bold = True
    run_t.font.color.rgb = PRIMARY
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    run_s = p_sub.add_run("Modélisation Conceptuelle (Abstraite) & Architecture Technique (Concrète)")
    run_s.font.name = "Calibri"
    run_s.font.size = Pt(13)
    run_s.bold = True
    run_s.font.color.rgb = SECONDARY
    
    # Bannière descriptive
    tbl_b = doc.add_table(rows=2, cols=2)
    tbl_b.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_b.autofit = False
    
    b_data = [
        [("Système :", " DYNATSIMO (Suivi Sécheresse & Végétation)"), ("Périmètre :", " Grand Sud de Madagascar (Androy, Anosy, Atsimo-Andrefana)")],
        [("Période analysée :", " 1981 – 2026 (Pluviométrie) & 2000 – 2026 (NDVI)"), ("Composants :", " Figures de flux illustrées + Explications méthodologiques détaillées")]
    ]
    for r_idx, row in enumerate(tbl_b.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(3.4)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            p = cell.paragraphs[0]
            lbl, val = b_data[r_idx][c_idx]
            rl = p.add_run(lbl)
            rl.bold = True
            rl.font.size = Pt(9)
            rl.font.color.rgb = PRIMARY
            rv = p.add_run(val)
            rv.font.size = Pt(9)
            rv.font.color.rgb = DARK_TEXT
    set_table_borders(tbl_b, color="CBD5E1", sz="4")
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    
    # -------------------------------------------------------------
    # SECTION 1 : CHAÎNE DE TRAITEMENT ABSTRAITE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(12)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("1. Chaîne de Traitement Abstraite (Niveau Conceptuel)")
    r_h1.font.name = "Calibri"
    r_h1.font.size = Pt(15)
    r_h1.bold = True
    r_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La chaîne de traitement abstraite illustre la logique théorique et scientifique de transformation des données géospatiales. "
        "Elle formalise le cheminement méthodique allant du signal satellitaire brut jusqu'à l'indicateur d'alerte décisionnel, "
        "indépendamment des technologies logicielles ou langages de programmation."
    )
    
    # Insertion de la Figure 1
    if os.path.exists(img_abs_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(img_abs_path, width=Inches(6.6))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run("Figure 1 : Organigramme conceptuel de la chaîne de traitement abstraite DYNATSIMO")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9.5)
        r_cap.italic = True
        r_cap.font.color.rgb = MUTED
        
    # Explications détaillées post-Figure 1
    p_exp_title = doc.add_paragraph()
    p_exp_title.paragraph_format.space_before = Pt(6)
    p_exp_title.paragraph_format.space_after = Pt(4)
    r_et = p_exp_title.add_run("Explications Méthodologiques Étape par Étape (Figure 1) :")
    r_et.bold = True
    r_et.font.size = Pt(11.5)
    r_et.font.color.rgb = PRIMARY
    
    add_step_card(
        doc,
        num="1",
        title="Acquisition & Télédétection Multi-Sources",
        description="• Réflectance Optique : Captation du rayonnement solaire réfléchi dans le Rouge (absorption chlorophyllienne) et le Proche Infrarouge (forte diffusion cellulaire foliaire).\n"
                    "• Télédétection Pluviométrique : Fusion d'imagerie infrarouge thermique (température des sommets nuageux), de micro-ondes passives et de réanalyses météorologiques.\n"
                    "• Référentiel Administratif : Couche vectorielle délimitant les 121 communes du Grand Sud de Madagascar.",
        border_color="2563EB",
        bg_color="EFF6FF"
    )
    
    add_step_card(
        doc,
        num="2",
        title="Prétraitement & Harmonisation Spatio-Temporelle",
        description="• Découpage Géométrique (Clipping) : Extraction des données raster restreinte aux frontières strictes de la zone d'étude.\n"
                    "• Masquage Radiométrique (Quality Assessment) : Élimination systématique des pixels pollués par les nuages, cirrus et ombres portées.\n"
                    "• Standardisation : Reprojection dans le système géodésique mondial WGS84 (EPSG:4326) et normalisation au pas de temps mensuel (12 matrices régulières par an).",
        border_color="16A34A",
        bg_color="F0FDF4"
    )
    
    add_step_card(
        doc,
        num="3",
        title="Calcul des Variables Bioclimatiques & Statistiques Zonales",
        description="• Indice de Végétation par Différence Normalisée : NDVI = (PIR - Rouge) / (PIR + Rouge), complété par les indices de condition (VCI) et de santé végétale (VHI).\n"
                    "• Normale Climatologique Historique : Calcul de la moyenne mensuelle de référence P_ref sur 45 ans (1981–2025).\n"
                    "• Anomalies & Déficits Hydriques : Calcul du déficit net D_m = P_obs - P_ref (en mm) et du taux d'écart relatif D% = (D_m / P_ref) × 100 pour chaque commune.",
        border_color="CA8A04",
        bg_color="FEFCE8"
    )
    
    add_step_card(
        doc,
        num="4",
        title="Modélisation Spatiale Continue & Typologie Bio-Végétale",
        description="• Interpolation Continue par IDW (Inverse Distance Weighting) : Reconstitution d'un champ continu de précipitations à partir des barycentres communaux avec une décroissance quadratique de la distance (p=2).\n"
                    "• Génération des Isohyètes : Extraction automatique des isolignes de précipitations par intervalles de 50 mm.\n"
                    "• Typologie en 6 Classes de Végétation : Discrétisation de l'espace en 6 classes d'état de la biomasse (Eau <0, Sol nu 0–0.2, Fourré dégradé 0.2–0.4, Fourré arbustif 0.4–0.6, Forêt sèche 0.6–0.8, Végétation très dense >0.8).",
        border_color="DB2777",
        bg_color="FDF2F8"
    )
    
    add_step_card(
        doc,
        num="5",
        title="Structuration Relationnelle & Restitution Décisionnelle",
        description="• Agrégation Multi-Échelles : Consolidation ascendante des indicateurs : Échelle Communale ➔ District ➔ Région ➔ Grand Sud global.\n"
                    "• Évaluation de la Sévérité : Catégorisation en 5 classes de stress hydrique (Déficit Extrême <-50%, Sévère -50% à -25%, Modéré -25% à -10%, Normal -10% à +10%, Excédent >+10%).\n"
                    "• Visualisation Interactive : Cartographie dynamique, lecteur temporel et tableaux de bord d'aide à la décision.",
        border_color="0F4C81",
        bg_color="F8FAFC"
    )
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # SECTION 2 : CHAÎNE DE TRAITEMENT CONCRÈTE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("2. Chaîne de Traitement Concrète (Implémentation Opérationnelle DYNATSIMO)")
    r_h1.font.name = "Calibri"
    r_h1.font.size = Pt(15)
    r_h1.bold = True
    r_h1.font.color.rgb = PRIMARY
    
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "La chaîne de traitement concrète décrit l'architecture technique réelle déployée dans le projet DYNATSIMO. "
        "Elle précise les jeux de données sources, les scripts Python et R développés, les bibliothèques scientifiques, "
        "la base de données PostgreSQL/PostGIS, le serveur cartographique GeoServer et l'interface Web interactive React."
    )
    
    # Insertion de la Figure 2
    if os.path.exists(img_cnc_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        doc.add_picture(img_cnc_path, width=Inches(6.6))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        r_cap = p_cap.add_run("Figure 2 : Architecture technique et flux opérationnels du pipeline DYNATSIMO")
        r_cap.font.name = "Calibri"
        r_cap.font.size = Pt(9.5)
        r_cap.italic = True
        r_cap.font.color.rgb = MUTED
        
    # Explications détaillées post-Figure 2
    p_exp_title2 = doc.add_paragraph()
    p_exp_title2.paragraph_format.space_before = Pt(6)
    p_exp_title2.paragraph_format.space_after = Pt(4)
    r_et2 = p_exp_title2.add_run("Explications Techniques des Composants & Scripts (Figure 2) :")
    r_et2.bold = True
    r_et2.font.size = Pt(11.5)
    r_et2.font.color.rgb = PRIMARY
    
    add_step_card(
        doc,
        num="1",
        title="Sources de Données & Ingestion Automatisée",
        description="• CHIRPS v2.0 (Précipitations) : Téléchargement automatique mensuel des GeoTIFF (.tif.gz) depuis le serveur de l'Université de Californie Santa Barbara (UCSB/CHC) via le script `scripts/download_chirps_monthly_VF.py`.\n"
                    "• MODIS MOD13Q1 / Sentinel-2 / Landsat (Végétation) : Extraction mensuelle via l'API Google Earth Engine (scripts `download_ndvi_modis_monthly_VF.py` et `download_sentinnel_monthly_VF.py`) avec filtrage nuages par masques QA.\n"
                    "• Référentiel Vectoriel : Shapefile `Regions 3/3_region.shp` (121 polygones communaux).",
        border_color="0284C7",
        bg_color="F0F9FF"
    )
    
    add_step_card(
        doc,
        num="2",
        title="Scripts de Modélisation Géospatiale & Traitement",
        description="• Interpolation des Isohyètes : Le script `scripts/isohyette_chirps_VF.py` exécute l'algorithme IDW de SciPy pour calculer une grille interpolée et génère les isolignes 50 mm au format GeoJSON (`public/data/isohyetes/`) et GeoTIFF.\n"
                    "• Classification 6 Classes NDVI : Le script `scripts/export_ndvi_6classes.py` segmente les rasters MODIS en 6 classes, génère les tuiles PNG RGBA transparentes (`public/data/raster/ndvi_modis_6classes/`) et le fichier de métadonnées `ndvi_classes_metadata.json` (319 périodes de 2000 à 2026).\n"
                    "• Extraction des Statistiques Zonales : Les scripts `scripts/import-chirps-and-export.py` et `scripts/export-data.R` calculent les moyennes communales mensuelles et les déficits.",
        border_color="0D9488",
        bg_color="F0FDF4"
    )
    
    add_step_card(
        doc,
        num="3",
        title="Stockage, Base PostgreSQL/PostGIS & Cache JSON",
        description="• Base Relationnelle & Spatiale PostgreSQL/PostGIS : Tables `public.communes` (géométries des 121 communes), `public.precipitation` (123 300 enregistrements mensuels de 1981 à 2026) et `public.ndvi_observations`.\n"
                    "• Serveur GeoServer WMS (Port 8080) : Publication des flux cartographiques WMS de l'espace `donnees_dynatsimo` pour l'affichage raster en tuiles tuilées dynamiques.\n"
                    "• Serveur API REST Python (`scripts/api-server.py`) : API FastAPI (Port 8000) fournissant `/api/data` et les endpoints de synchronisation incrémentielle `/api/sync/*`.\n"
                    "• Cache JSON Public (`public/data/`) : Fichiers statiques légers pour chargement ultra-rapide (overview.json, communes.geojson, anomalies.json, precip-records.json).",
        border_color="7C3AED",
        bg_color="FAF5FF"
    )
    
    add_step_card(
        doc,
        num="4",
        title="Restitution & Interface Interactive React / Vite",
        description="• Cartographie Dynamique Multi-Modes : React-Leaflet gérant l'affichage Choroplèthe, les courbes Isohyètes et les rasters NDVI 6 classes avec curseur d'opacité.\n"
                    "• Lecteur Temporel / Timeline : Contrôleur avec boutons Préc./Lecture/Suiv., vitesse réglable (0.6s à 2.0s) et scrubber.\n"
                    "• Détection Intelligente des Mois Disponibles : L'interface s'ajuste dynamiquement aux mois réellement enregistrés dans la base (ex : Janvier à Août pour 2026).\n"
                    "• Graphiques & Décision : Séries temporelles Recharts, comparaison multi-capteurs (Landsat vs Sentinel vs MODIS) et exportations CSV instantanées.",
        border_color="E11D48",
        bg_color="FFF1F2"
    )
    
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # -------------------------------------------------------------
    # SECTION 3 : TABLEAU DE SYNTHÈSE CROISÉE
    # -------------------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(8)
    h1.paragraph_format.space_after = Pt(4)
    r_h1 = h1.add_run("3. Matrice de Correspondance Synthétique (Figure 1 vs Figure 2)")
    r_h1.font.name = "Calibri"
    r_h1.font.size = Pt(14)
    r_h1.bold = True
    r_h1.font.color.rgb = PRIMARY
    
    tbl_c = doc.add_table(rows=6, cols=3)
    tbl_c.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_c.autofit = False
    
    h_c = ["Phase Abstraite (Figure 1)", "Composant Concret (Figure 2)", "Rôle & Implémentation dans DYNATSIMO"]
    for c_idx, txt in enumerate(h_c):
        cell = tbl_c.cell(0, c_idx)
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(txt)
        r.bold = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    rows_data = [
        ("Phase 1 : Acquisition", "CHIRPS UCSB & Google Earth Engine API", "Téléchargement automatique des rasters 0.05° et 250m"),
        ("Phase 2 : Prétraitements", "Rasterio Mask, QA Bitmask, WGS84", "Découpage sur le Grand Sud et filtrage atmosphérique"),
        ("Phase 3 : Indices Bioclimatiques", "Rasterstats & export-data.R", "Calculs zonaux par commune du NDVI, anomalies D_m et D%"),
        ("Phase 4 : Modélisation Spatiale", "isohyette_chirps_VF.py & export_ndvi_6classes.py", "Interpolation IDW p=2 et reclassification 6 classes RGBA"),
        ("Phase 5 : Restitution Décisionnelle", "React 18, React-Leaflet, Recharts, FastAPI", "Cartographie avec timeline interactive et sélecteur dynamique")
    ]
    
    widths_c = [Inches(1.8), Inches(2.2), Inches(2.8)]
    for r_idx, r_val in enumerate(rows_data, start=1):
        for c_idx, val in enumerate(r_val):
            cell = tbl_c.cell(r_idx, c_idx)
            cell.width = widths_c[c_idx]
            set_cell_background(cell, "FFFFFF" if r_idx % 2 == 1 else "F8FAFC")
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            r.font.color.rgb = DARK_TEXT
            if c_idx == 0:
                r.bold = True
                r.font.color.rgb = PRIMARY
                
    set_table_borders(tbl_c, color="CBD5E1", sz="4")
    
    try:
        doc.save(docx_path)
        print(f"Document complet généré avec succès : {docx_path}")
    except PermissionError:
        alt_path = os.path.join(os.getcwd(), "Chaines_de_Traitement_DYNATSIMO_Figures.docx")
        doc.save(alt_path)
        print(f"Le fichier principal étant ouvert dans Word, le document a été enregistré sous : {alt_path}")

if __name__ == "__main__":
    scratch_dir = os.path.join(os.getcwd(), "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    img_abs = os.path.join(scratch_dir, "figure_chaine_abstraite.png")
    img_cnc = os.path.join(scratch_dir, "figure_chaine_concrete.png")
    
    generate_figure_abstraite(img_abs)
    generate_figure_concrete(img_cnc)
    
    doc_out = os.path.join(os.getcwd(), "Chaines_de_Traitement_DYNATSIMO.docx")
    build_complete_word_document(doc_out, img_abs, img_cnc)
