import os
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

def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
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

def add_callout_box(doc, title, text, speaker=None, bg_color="F1F5F9", border_color="0284C7"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=200, right=180)
    
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
    run_t = p.add_run(f"📌 {title}")
    run_t.bold = True
    run_t.font.name = "Calibri"
    run_t.font.size = Pt(11)
    run_t.font.color.rgb = RGBColor(15, 76, 129)
    
    if speaker:
        p_sp = cell.add_paragraph()
        p_sp.paragraph_format.space_before = Pt(2)
        p_sp.paragraph_format.space_after = Pt(2)
        run_sp = p_sp.add_run(f"🗣️ {speaker} :")
        run_sp.bold = True
        run_sp.font.name = "Calibri"
        run_sp.font.size = Pt(10.5)
        run_sp.font.color.rgb = RGBColor(30, 41, 59)
    
    p_body = cell.add_paragraph()
    p_body.paragraph_format.space_before = Pt(2)
    p_body.paragraph_format.space_after = Pt(2)
    run_b = p_body.add_run(f"« {text} »" if speaker else text)
    run_b.italic = True if speaker else False
    run_b.font.name = "Calibri"
    run_b.font.size = Pt(10.5)
    run_b.font.color.rgb = RGBColor(51, 65, 85)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def build_docx(filename):
    doc = Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
    
    # Styles
    PRIMARY = RGBColor(15, 76, 129)     # Deep Navy #0F4C81
    SECONDARY = RGBColor(13, 148, 136)  # Teal #0D9488
    DARK_TEXT = RGBColor(30, 41, 59)    # Slate #1E293B
    MUTED = RGBColor(100, 116, 139)     # Gray #64748B
    
    # Header Title
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(2)
    title_run = title_p.add_run("FICHE D'ANIMATION & PRÉSENTATION")
    title_run.font.name = "Calibri"
    title_run.font.size = Pt(22)
    title_run.font.bold = True
    title_run.font.color.rgb = PRIMARY
    
    # Subtitle
    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(12)
    sub_run = sub_p.add_run("Application DYNATSIMO — Module Pluviométrie & Aide à la Décision")
    sub_run.font.name = "Calibri"
    sub_run.font.size = Pt(14)
    sub_run.font.bold = True
    sub_run.font.color.rgb = SECONDARY
    
    # Info Banner Table
    info_tbl = doc.add_table(rows=2, cols=2)
    info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_tbl.autofit = False
    
    info_data = [
        [("⏰ Horaire :", " 11h25 – 11h40 (Durée : 15 min)"), ("👤 Intervenants :", " Fandresena (en interaction avec PAH)")],
        [("🌍 Périmètre :", " Grand Sud (Androy, Anosy, Atsimo-Andrefana)"), ("🎯 Cœur de sujet :", " Pluviométrie, ciblage, usage & suivi post-aide")]
    ]
    
    for r_idx, row in enumerate(info_tbl.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(3.25)
            set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            lbl, val = info_data[r_idx][c_idx]
            r_lbl = p.add_run(lbl)
            r_lbl.bold = True
            r_lbl.font.size = Pt(9.5)
            r_lbl.font.color.rgb = PRIMARY
            r_val = p.add_run(val)
            r_val.font.size = Pt(9.5)
            r_val.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # ----------------------------------------------------
    # SECTION 1 : MINUTAGE
    # ----------------------------------------------------
    h1 = doc.add_paragraph()
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    r_h1 = h1.add_run("1. Chronogramme & Déroulé Minuté (15 min)")
    r_h1.font.name = "Calibri"
    r_h1.font.size = Pt(14)
    r_h1.font.bold = True
    r_h1.font.color.rgb = PRIMARY
    
    table = doc.add_table(rows=5, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table, color="CBD5E1")
    
    headers = ["Horaire", "Durée", "Séquence & Thématique", "Objectif Opérationnel"]
    widths = [Inches(1.1), Inches(0.8), Inches(2.3), Inches(2.3)]
    
    for i, h_text in enumerate(headers):
        cell = table.cell(0, i)
        cell.width = widths[i]
        set_cell_background(cell, "0F4C81")
        set_cell_margins(cell, top=120, bottom=120, left=120, right=120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        run = p.add_run(h_text)
        run.bold = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    data = [
        ("11h25 – 11h27", "2 min", "1. Accroche interactive (Fandresena & PAH)", "Poser le problème terrain : comment décider sans indicateurs fiables ?"),
        ("11h27 – 11h33", "6 min", "2. Démo Live DYNATSIMO (Pluviométrie)", "Démontrer la valeur des 3 vues clés (Carto, Saisons, Anomalies)."),
        ("11h33 – 11h39", "6 min", "3. Échanges & Débat avec la salle", "Traiter les 3 questions opérationnelles (Ciblage, Bénéficiaires, Suivi)."),
        ("11h39 – 11h40", "1 min", "4. Synthèse & Clôture", "Fixer les messages clés et la valeur ajoutée de la plateforme.")
    ]
    
    for row_idx, row_data in enumerate(data, start=1):
        bg = "FFFFFF" if row_idx % 2 == 1 else "F8FAFC"
        for col_idx, text in enumerate(row_data):
            cell = table.cell(row_idx, col_idx)
            cell.width = widths[col_idx]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=100, bottom=100, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            run = p.add_run(text)
            run.font.size = Pt(9.5)
            if col_idx == 0 or col_idx == 1:
                run.bold = True
                run.font.color.rgb = PRIMARY
            else:
                run.font.color.rgb = DARK_TEXT

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # ----------------------------------------------------
    # SECTION 2 : GUIDE D'ANIMATION PAS À PAS
    # ----------------------------------------------------
    h2 = doc.add_paragraph()
    h2.paragraph_format.space_before = Pt(14)
    h2.paragraph_format.space_after = Pt(6)
    r_h2 = h2.add_run("2. Guide d'Animation & Script Détaillé")
    r_h2.font.name = "Calibri"
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = PRIMARY

    # Séquence 1
    doc.add_heading("Séquence 1 : Accroche interactive en duo (11h25 – 11h27)", level=2)
    
    add_callout_box(
        doc,
        title="Interpellation de départ — Contexte terrain",
        speaker="PAH",
        text="Sur le terrain, quand la saison des pluies est tardive ou déficitaire, comment sait-on exactement quelles communes ou zones sont les plus durement touchées sans attendre les premiers signaux de détresse ?",
        border_color="0284C7"
    )
    
    add_callout_box(
        doc,
        title="Réponse & Transition vers l'application",
        speaker="Fandresena",
        text="C’est tout l’enjeu de DYNATSIMO : transformer plus de 40 ans de données satellitaires (CHIRPS de 1981 à 2026) en indicateurs spatiaux et temporels clairs pour anticiper, cibler sans biais et suivre l’impact réel de nos interventions dans le Grand Sud.",
        border_color="0D9488"
    )

    # Séquence 2
    doc.add_heading("Séquence 2 : Démonstration de l'application (11h27 – 11h33)", level=2)
    
    p_demo_intro = doc.add_paragraph()
    p_demo_intro.paragraph_format.space_after = Pt(6)
    r_di = p_demo_intro.add_run("Présenter 3 vues stratégiques en reliant chaque fonction à une prise de décision opérationnelle :")
    r_di.font.size = Pt(10.5)
    r_di.font.color.rgb = DARK_TEXT

    demo_steps = [
        ("Écran 1 : Cartographie spatiale & Lignes isohyètes (2 min)",
         "Onglet « Cartographie »",
         "Montrer le fort gradient pluviométrique Est-Ouest (plus de 900 mm vers Fort-Dauphin / Anosy, contre moins de 350 mm sur la côte sud-ouest à Ambovombe et Tsihombe). Mettre en évidence les poches de déficit cumulé au niveau des 225 communes.",
         "« La carte élimine les estimations subjectives : elle localise immédiatement les zones en déficit critique pour prioriser nos déploiements. »"),
        
        ("Écran 2 : Qualité et démarrage de la saison des pluies (2 min)",
         "Onglet « Statistiques & Analyses » (Module Saisons)",
         "Analyser la date de début de saison, les faux départs et les ruptures de pluies en cours de cycle cultural.",
         "« Un cumul annuel ne suffit pas : une pluie qui arrive avec 45 jours de retard compromet la récolte, même si le volume total semble normal. »"),
        
        ("Écran 3 : Climatologie historique & Anomalies pluriannuelles (2 min)",
         "Onglet « Vue d'ensemble » / « Anomalies »",
         "Comparer la campagne observée avec l'historique 1981–2026 pour situer la sévérité du choc climatique (sécheresse décennale vs fluctuation habituelle).",
         "« Cela permet d'ajuster le dimensionnement de l'aide en fonction de l'intensité réelle du choc. »")
    ]

    for title, tab, desc, pitch in demo_steps:
        p_step = doc.add_paragraph()
        p_step.paragraph_format.space_before = Pt(6)
        p_step.paragraph_format.space_after = Pt(2)
        r_st = p_step.add_run(f"🔹 {title}")
        r_st.bold = True
        r_st.font.size = Pt(11)
        r_st.font.color.rgb = PRIMARY
        
        p_details = doc.add_paragraph()
        p_details.paragraph_format.left_indent = Inches(0.2)
        p_details.paragraph_format.space_after = Pt(2)
        r_tab = p_details.add_run(f"• Navigation : {tab}\n")
        r_tab.bold = True
        r_tab.font.size = Pt(10)
        r_desc = p_details.add_run(f"• Ce qu'on montre : {desc}\n")
        r_desc.font.size = Pt(10)
        r_pitch = p_details.add_run(f"• Phrase d'impact : {pitch}")
        r_pitch.italic = True
        r_pitch.font.size = Pt(10)
        r_pitch.font.color.rgb = RGBColor(15, 118, 110)

    # Séquence 3
    doc.add_heading("Séquence 3 : Animation du Débat avec les Participants (11h33 – 11h39)", level=2)

    p_deb = doc.add_paragraph()
    p_deb.paragraph_format.space_after = Pt(6)
    p_deb.add_run("Traiter les 3 questions en croisant l'expérience des participants et les fonctionnalités de DYNATSIMO :")

    questions = [
        ("Question 1 : « Quels choix de ciblage posent le plus de difficultés ? »",
         "Dilemmes terrain : Conflit fréquent entre ciblage géographique (choix des communes/fokontany) et ciblage socio-économique (choix des ménages vulnérables). Risque d'incompréhension ou de pressions locales.",
         "Apport de DYNATSIMO : Fournit une base technique neutre, factuelle et auditable (stress hydrique mesuré par satellite), facilitant l'arbitrage et le plaidoyer auprès des autorités locales.",
         "Relance animateur : « Dans vos projets, comment arbitrez-vous quand une commune entière est affectée mais que les ressources ne permettent de cibler qu'une fraction des ménages ? »"),
        
        ("Question 2 : « Qui utilise réellement l’appui, qui fournit le travail et qui en retire les bénéfices ? »",
         "Dilemmes terrain : Dans les programmes de relance agricole ou travaux communautaires (Cash-for-Work), les femmes et les jeunes fournissent souvent la main-d’œuvre agricole principale, mais la décision sur la récolte ou les revenus peut être concentrée chez le chef de ménage.",
         "Lien Pluviométrie : Le déficit de pluie aggrave la corvée d'eau (qui pèse sur les femmes) et précipite la vente des petits ruminants ou d'actifs productifs.",
         "Relance animateur : « Observez-vous des différences dans l'utilisation de l'aide selon que l'on cible la parcelle familiale ou des activités spécifiques portées par les femmes ? »"),
        
        ("Question 3 : « Que suit-on après l’attribution de l’aide ? »",
         "Dilemmes terrain : On trace rigoureusement les distributions (intrants, semences, cash), mais on manque souvent d'indicateurs de suivi sur le succès agronomique réel post-distribution.",
         "Apport de DYNATSIMO : Permet un suivi croisé : vérifier si la reprise pluviométrique (CHIRPS) et la réponse de la biomasse végétale (NDVI Landsat/Sentinel) ont effectivement permis la levée et la croissance des cultures appuyées.",
         "Relance animateur : « Avez-vous déjà constaté des échecs de distribution dus à un arrêt brutal des pluies 15 jours après les semis ? Comment pourrait-on intégrer ce suivi satellite dans vos rapports bailleurs ? »")
    ]

    for q_title, q_ctx, q_app, q_prompt in questions:
        add_callout_box(
            doc,
            title=q_title,
            text=f"{q_ctx}\n\n💡 Solution DYNATSIMO : {q_app}\n\n🗣️ Relance salle : {q_prompt}",
            bg_color="F8FAFC",
            border_color="D97706"
        )

    # Séquence 4
    doc.add_heading("Séquence 4 : Synthèse & Clôture (11h39 – 11h40)", level=2)
    
    add_callout_box(
        doc,
        title="Message de conclusion (Fandresena)",
        speaker="Fandresena",
        text="DYNATSIMO n'est pas seulement un outil de visualisation climatique : c'est un levier d'aide à la décision tout au long du cycle de projet. Il sécurise le ciblage géographique en amont, optimise le calendrier des distributions pendant la campagne, et mesure l'impact agro-climatique réel en aval.",
        border_color="0F4C81"
    )

    # ----------------------------------------------------
    # SECTION 3 : CHECKLIST PRATIQUE
    # ----------------------------------------------------
    h3 = doc.add_paragraph()
    h3.paragraph_format.space_before = Pt(14)
    h3.paragraph_format.space_after = Pt(6)
    r_h3 = h3.add_run("3. Checklist Technique & Conseils pour le Direct")
    r_h3.font.name = "Calibri"
    r_h3.font.size = Pt(14)
    r_h3.font.bold = True
    r_h3.font.color.rgb = PRIMARY

    check_items = [
        ("Préparation écran :", " Ouvrir l'application à l'avance sur http://localhost:5173 sur l'onglet Cartographie avec les calques isohyètes activés."),
        ("Gestion du chrono :", " Garder un œil strict sur le temps (6 min de démo max, 2 min par question lors du débat)."),
        ("Duo Fandresena / PAH :", " Laisser PAH introduire ou reformuler les réactions du public pour dynamiser les échanges et faire le pont avec le terrain.")
    ]

    for lbl, val in check_items:
        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_after = Pt(3)
        p_c.paragraph_format.left_indent = Inches(0.2)
        r1 = p_c.add_run(f"✔️ {lbl}")
        r1.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = SECONDARY
        r2 = p_c.add_run(val)
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT

    doc.save(filename)
    print(f"Document saved successfully: {filename}")

if __name__ == "__main__":
    out_path = os.path.abspath("Presentation_DYNATSIMO_Pluviometrie_11h25-11h40.docx")
    build_docx(out_path)
