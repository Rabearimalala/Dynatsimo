import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation(output_path):
    prs = Presentation()
    # 16:9 widescreen format
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6] # blank layout

    # Color Palette
    DARK_BG = RGBColor(10, 25, 47)      # #0A192F Dark Navy
    CARD_DARK = RGBColor(17, 34, 64)    # #112240 Card Navy
    LIGHT_BG = RGBColor(248, 250, 252)  # #F8FAFC Off-white
    PRIMARY = RGBColor(15, 76, 129)     # #0F4C81 Deep Blue
    SECONDARY = RGBColor(13, 148, 136)  # #0D9488 Teal
    ACCENT = RGBColor(217, 119, 6)      # #D97706 Amber
    TEXT_DARK = RGBColor(30, 41, 59)    # #1E293B Slate Dark
    TEXT_MUTED = RGBColor(100, 116, 139)# #64748B Slate Muted
    WHITE = RGBColor(255, 255, 255)
    LIGHT_BLUE = RGBColor(239, 246, 255)# #EFF6FF
    LIGHT_TEAL = RGBColor(240, 253, 250)# #F0FDFA
    LIGHT_AMBER = RGBColor(254, 243, 199)# #FEF3C7

    def add_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_header(slide, title_text, category_text="DYNATSIMO • SESSION PLUVIOMÉTRIE (11h25 – 11h40)"):
        # Header banner/category
        tx_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_cat = tx_cat.text_frame
        tf_cat.word_wrap = True
        p_c = tf_cat.paragraphs[0]
        p_c.text = category_text.upper()
        p_c.font.size = Pt(10)
        p_c.font.bold = True
        p_c.font.color.rgb = SECONDARY
        
        # Main Title
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf_title = tx_title.text_frame
        tf_title.word_wrap = True
        p_t = tf_title.paragraphs[0]
        p_t.text = title_text
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY

    def add_card(slide, left, top, width, height, bg_color, border_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = bg_color
        if border_color:
            shape.line.color.rgb = border_color
            shape.line.width = Pt(1.5)
        else:
            shape.line.fill.background()
        return shape

    # ==========================================
    # SLIDE 1 : Titre & Contexte
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, DARK_BG)
    
    # Decorative shape
    s1_card = add_card(s1, Inches(1.0), Inches(1.2), Inches(11.333), Inches(5.1), CARD_DARK, SECONDARY)
    
    tx_s1 = s1.shapes.add_textbox(Inches(1.5), Inches(1.6), Inches(10.333), Inches(4.3))
    tf_s1 = tx_s1.text_frame
    tf_s1.word_wrap = True
    
    p = tf_s1.paragraphs[0]
    p.text = "🌍 PROJET DYNATSIMO"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = SECONDARY
    p.space_after = Pt(14)
    
    p2 = tf_s1.add_paragraph()
    p2.text = "Présentation de l'Application : Module Pluviométrie"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_after = Pt(10)
    
    p3 = tf_s1.add_paragraph()
    p3.text = "Objectiver le ciblage, adapter l'appui et suivre l'impact agro-climatique dans le Sud"
    p3.font.size = Pt(16)
    p3.font.color.rgb = RGBColor(203, 213, 225)
    p3.space_after = Pt(28)
    
    p4 = tf_s1.add_paragraph()
    p4.text = "⏱️ Session : 11h25 – 11h40 (15 min)   |   👤 Intervenant : Fandresena (en interaction avec PAH)"
    p4.font.size = Pt(12)
    p4.font.bold = True
    p4.font.color.rgb = ACCENT
    
    p5 = tf_s1.add_paragraph()
    p5.text = "📍 Zone d'étude : 225 communes • Régions Androy, Anosy, Atsimo-Andrefana (Données CHIRPS 1981–2026)"
    p5.font.size = Pt(11)
    p5.font.color.rgb = RGBColor(148, 163, 184)
    p5.space_before = Pt(8)

    # Speaker notes s1
    s1.notes_slide.notes_text_frame.text = (
        "Introduction rapide (1 min max) :\n"
        "- Bienvenue à tous pour cette présentation de DYNATSIMO.\n"
        "- Objectif : Montrer comment la donnée pluviométrique et satellitaire répond aux défis réels de ciblage et de suivi de nos programmes."
    )

    # ==========================================
    # SLIDE 2 : Accroche Duo (Fandresena & PAH)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, LIGHT_BG)
    add_header(s2, "Accroche : Du Défi Terrain à la Décision Basée sur les Données")
    
    # Left Card : Question Terrain PAH
    add_card(s2, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), WHITE, PRIMARY)
    tx_pah = s2.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(4.5))
    tf_pah = tx_pah.text_frame
    tf_pah.word_wrap = True
    
    p = tf_pah.paragraphs[0]
    p.text = "🗣️ L'INTERPELLATION TERRAIN (PAH)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(14)
    
    p = tf_pah.add_paragraph()
    p.text = "« Sur le terrain, quand la saison des pluies est tardive ou déficitaire, comment sait-on exactement quelles communes ou zones sont les plus durement touchées sans attendre les premiers signaux de détresse ? »"
    p.font.size = Pt(14)
    p.font.italic = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(18)
    
    p = tf_pah.add_paragraph()
    p.text = "⚠️ Risques sans données factuelles :\n• Ciblage approximatif ou contesté\n• Réponse tardive en mode réactif\n• Manque de visibilité sur les micro-climats"
    p.font.size = Pt(11.5)
    p.font.color.rgb = ACCENT

    # Right Card : Réponse Fandresena / DYNATSIMO
    add_card(s2, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), LIGHT_TEAL, SECONDARY)
    tx_fan = s2.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(4.5))
    tf_fan = tx_fan.text_frame
    tf_fan.word_wrap = True
    
    p = tf_fan.paragraphs[0]
    p.text = "💡 LA RÉPONSE DYNATSIMO (FANDRESENA)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = SECONDARY
    p.space_after = Pt(14)
    
    p = tf_fan.add_paragraph()
    p.text = "« C’est tout l’enjeu de DYNATSIMO : transformer plus de 40 ans de données satellitaires (CHIRPS 1981–2026) en indicateurs spatiaux et temporels clairs pour anticiper, cibler sans biais et suivre l’impact réel de nos interventions. »"
    p.font.size = Pt(14)
    p.font.italic = True
    p.font.color.rgb = TEXT_DARK
    p.space_after = Pt(18)
    
    p = tf_fan.add_paragraph()
    p.text = "📊 Ce que l'outil apporte :\n• Couverture intégrale des 225 communes\n• Analyse fine des déficits et isohyètes\n• Objectivité totale pour dépolitiser les choix"
    p.font.size = Pt(11.5)
    p.font.color.rgb = PRIMARY

    # ==========================================
    # SLIDE 3 : Démonstration Live (3 Vues Clés)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, LIGHT_BG)
    add_header(s3, "Démonstration Live : 3 Vues Stratégiques dans DYNATSIMO (6 min)")
    
    views = [
        ("1. Cartographie & Isohyètes", 
         "Gradient spatial & Déficits", 
         "• Révèle le gradient Est (>900 mm à Fort-Dauphin) vers Ouest (<350 mm à Tsihombe)\n• Identifie les poches de déficit cumulé au niveau communal.",
         "« Élimine les estimations subjectives »",
         PRIMARY, LIGHT_BLUE),
        
        ("2. Saison des Pluies", 
         "Démarrage & Qualité agricole", 
         "• Détecte la date effective de début de saison\n• Analyse les faux départs et ruptures de pluie en pleine croissance.",
         "« Une pluie tardive compromet la récolte »",
         SECONDARY, LIGHT_TEAL),
        
        ("3. Anomalies & Climatologie", 
         "Sévérité du choc historique", 
         "• Compare la campagne en cours aux 40 années d'historique (1981–2026)\n• Qualifie l'ampleur de la sécheresse.",
         "« Ajuster le dimensionnement de l'aide »",
         ACCENT, LIGHT_AMBER)
    ]
    
    for idx, (title, subtitle, bullets, quote, col_prim, col_bg) in enumerate(views):
        left_pos = Inches(0.8 + idx * 4.0)
        add_card(s3, left_pos, Inches(1.7), Inches(3.7), Inches(5.0), col_bg, col_prim)
        
        tx = s3.shapes.add_textbox(left_pos + Inches(0.2), Inches(1.9), Inches(3.3), Inches(4.5))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col_prim
        p.space_after = Pt(2)
        
        p_sub = tf.add_paragraph()
        p_sub.text = subtitle.upper()
        p_sub.font.size = Pt(9.5)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_MUTED
        p_sub.space_after = Pt(12)
        
        p_b = tf.add_paragraph()
        p_b.text = bullets
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = TEXT_DARK
        p_b.space_after = Pt(16)
        
        p_q = tf.add_paragraph()
        p_q.text = f"💡 {quote}"
        p_q.font.size = Pt(11)
        p_q.font.bold = True
        p_q.font.italic = True
        p_q.font.color.rgb = col_prim

    # ==========================================
    # SLIDE 4 : Débat 1 - Choix de ciblage
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, LIGHT_BG)
    add_header(s4, "Échange 1 : Quels choix de ciblage posent le plus de difficultés ?")
    
    # Left Card : Problématique
    add_card(s4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(3.6), WHITE, PRIMARY)
    tx_q1_l = s4.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(3.2))
    tf_q1_l = tx_q1_l.text_frame
    tf_q1_l.word_wrap = True
    
    p = tf_q1_l.paragraphs[0]
    p.text = "🎯 LE DILEMME OPÉRATIONNEL"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(8)
    
    p = tf_q1_l.add_paragraph()
    p.text = "• Arbitrage difficile entre ciblage géographique (communes prioritaires) et ciblage catégoriel (ménages vulnérables).\n• Pressions locales et risques de contestation communautaire lors de la sélection des bénéficiaires.\n• Ressources limitées face à des besoins étendus."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Right Card : Apport DYNATSIMO
    add_card(s4, Inches(6.8), Inches(1.7), Inches(5.7), Inches(3.6), LIGHT_TEAL, SECONDARY)
    tx_q1_r = s4.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(3.2))
    tf_q1_r = tx_q1_r.text_frame
    tf_q1_r.word_wrap = True
    
    p = tf_q1_r.paragraphs[0]
    p.text = "✨ L'APPORT DE DYNATSIMO"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = SECONDARY
    p.space_after = Pt(8)
    
    p = tf_q1_r.add_paragraph()
    p.text = "• Données satellitaires neutres, vérifiables et auditables à l'échelle de 225 communes.\n• Dépolitisation du choix des zones d'intervention grâce à la cartographie du déficit pluviométrique.\n• Justification transparente auprès des bailleurs et des partenaires."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Bottom Question Banner
    add_card(s4, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.3), LIGHT_AMBER, ACCENT)
    tx_q1_b = s4.shapes.add_textbox(Inches(1.1), Inches(5.75), Inches(11.1), Inches(1.0))
    tf_q1_b = tx_q1_b.text_frame
    tf_q1_b.word_wrap = True
    p = tf_q1_b.paragraphs[0]
    p.text = "🗣️ QUESTION À LA SALLE :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    p2 = tf_q1_b.add_paragraph()
    p2.text = "« Dans vos projets, comment combinez-vous aujourd'hui données climatiques et critères ménages pour justifier vos choix de ciblage ? »"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 5 : Débat 2 - Qui utilise / travaille / bénéficie ?
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, LIGHT_BG)
    add_header(s5, "Échange 2 : Qui utilise l'appui, qui fournit le travail et qui en bénéficie ?")
    
    # Left Card
    add_card(s5, Inches(0.8), Inches(1.7), Inches(5.6), Inches(3.6), WHITE, PRIMARY)
    tx_q2_l = s5.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(3.2))
    tf_q2_l = tx_q2_l.text_frame
    tf_q2_l.word_wrap = True
    
    p = tf_q2_l.paragraphs[0]
    p.text = "👥 DYNAMIQUES SOCIALES & INTRA-MÉNAGES"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(8)
    
    p = tf_q2_l.add_paragraph()
    p.text = "• Les femmes et les jeunes fournissent l'essentiel de la main-d'œuvre agricole et des travaux pénibles.\n• La décision sur l'usage de la récolte, des semences ou des revenus du Cash-for-Work est souvent concentrée chez le chef de ménage.\n• Décalage fréquent entre charge de travail et captation des bénéfices."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Right Card
    add_card(s5, Inches(6.8), Inches(1.7), Inches(5.7), Inches(3.6), LIGHT_TEAL, SECONDARY)
    tx_q2_r = s5.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(3.2))
    tf_q2_r = tx_q2_r.text_frame
    tf_q2_r.word_wrap = True
    
    p = tf_q2_r.paragraphs[0]
    p.text = "🌧️ CROISEMENT AVEC LE STRESS PLUVIOMÉTRIQUE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = SECONDARY
    p.space_after = Pt(8)
    
    p = tf_q2_r.add_paragraph()
    p.text = "• En période de déficit pluviométrique, la corvée d'eau des femmes augmente considérablement (temps perdu pour les cultures).\n• La sécheresse oblige à des stratégies d'adaptation négatives (vente d'actifs, déscolarisation).\n• L'outil permet de corréler stress hydrique et vulnérabilité de genre."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Bottom Question Banner
    add_card(s5, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.3), LIGHT_AMBER, ACCENT)
    tx_q2_b = s5.shapes.add_textbox(Inches(1.1), Inches(5.75), Inches(11.1), Inches(1.0))
    tf_q2_b = tx_q2_b.text_frame
    tf_q2_b.word_wrap = True
    p = tf_q2_b.paragraphs[0]
    p.text = "🗣️ QUESTION À LA SALLE :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    p2 = tf_q2_b.add_paragraph()
    p2.text = "« Constatez-vous des écarts sur le terrain entre ceux qui réalisent les travaux soutenus et ceux qui en tirent les gains ? Comment l'adapter ? »"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 6 : Débat 3 - Que suit-on après l'aide ?
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, LIGHT_BG)
    add_header(s6, "Échange 3 : Que suit-on après l'attribution de l'aide ?")
    
    # Left Card
    add_card(s6, Inches(0.8), Inches(1.7), Inches(5.6), Inches(3.6), WHITE, PRIMARY)
    tx_q3_l = s6.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(5.0), Inches(3.2))
    tf_q3_l = tx_q3_l.text_frame
    tf_q3_l.word_wrap = True
    
    p = tf_q3_l.paragraphs[0]
    p.text = "📦 LA LIMITE DU SUIVI CLASSIQUE"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.space_after = Pt(8)
    
    p = tf_q3_l.add_paragraph()
    p.text = "• On suit généralement les indicateurs de réalisation (quantités de semences, montants de cash distribués, nombre de bénéficiaires).\n• Mais on manque souvent de données sur le succès agronomique réel après la distribution.\n• Risque d'attribuer un échec aux bénéficiaires alors qu'une sécheresse post-semis a tout détruit."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Right Card
    add_card(s6, Inches(6.8), Inches(1.7), Inches(5.7), Inches(3.6), LIGHT_TEAL, SECONDARY)
    tx_q3_r = s6.shapes.add_textbox(Inches(7.1), Inches(1.9), Inches(5.1), Inches(3.2))
    tf_q3_r = tx_q3_r.text_frame
    tf_q3_r.word_wrap = True
    
    p = tf_q3_r.paragraphs[0]
    p.text = "🛰️ LE SUIVI CROISÉ DYNATSIMO"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = SECONDARY
    p.space_after = Pt(8)
    
    p = tf_q3_r.add_paragraph()
    p.text = "• Suivi de la pluie effective post-distribution (CHIRPS) pour valider la fenêtre de semis.\n• Suivi de la réponse végétale (NDVI Landsat/Sentinel) pour vérifier la levée et la vitalité des cultures.\n• Évaluation objective de l'efficacité de l'appui sans surcoût d'enquêtes lourdes."
    p.font.size = Pt(11.5)
    p.font.color.rgb = TEXT_DARK

    # Bottom Question Banner
    add_card(s6, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.3), LIGHT_AMBER, ACCENT)
    tx_q3_b = s6.shapes.add_textbox(Inches(1.1), Inches(5.75), Inches(11.1), Inches(1.0))
    tf_q3_b = tx_q3_b.text_frame
    tf_q3_b.word_wrap = True
    p = tf_q3_b.paragraphs[0]
    p.text = "🗣️ QUESTION À LA SALLE :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = ACCENT
    p2 = tf_q3_b.add_paragraph()
    p2.text = "« Quels indicateurs utilisez-vous après distribution pour mesurer si l'appui a réellement profité à la sécurité alimentaire des ménages ? »"
    p2.font.size = Pt(13)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_DARK

    # ==========================================
    # SLIDE 7 : Synthèse & Clôture
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, DARK_BG)
    
    tx_s7_t = s7.shapes.add_textbox(Inches(0.8), Inches(0.6), Inches(11.7), Inches(0.8))
    tf_s7_t = tx_s7_t.text_frame
    p = tf_s7_t.paragraphs[0]
    p.text = "DYNATSIMO : Une Boussole à Chaque Étape du Cycle de Projet"
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = WHITE
    
    pillars = [
        ("EN AMONT", "Ciblage Objectif", "• Détecter les zones en déficit critique\n• Dépolitiser le choix géographique\n• Dimensionner l'aide selon l'anomalie", PRIMARY, LIGHT_BLUE),
        ("EN COURS", "Adaptation & Calendrier", "• Suivre le démarrage réel des pluies\n• Alerter sur les faux départs de saison\n• Synchroniser la logistique avec la météo", SECONDARY, LIGHT_TEAL),
        ("EN AVAL", "Mesure d'Impact Réel", "• Corréler pluie et vigueur végétale (NDVI)\n• Évaluer le succès agro-climatique post-aide\n• Fournir des preuves solides aux bailleurs", ACCENT, LIGHT_AMBER)
    ]
    
    for idx, (step, title, text, col_b, col_bg) in enumerate(pillars):
        left_pos = Inches(0.8 + idx * 4.0)
        add_card(s7, left_pos, Inches(1.6), Inches(3.7), Inches(4.3), CARD_DARK, col_b)
        
        tx = s7.shapes.add_textbox(left_pos + Inches(0.2), Inches(1.8), Inches(3.3), Inches(3.9))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = step
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col_b
        p.space_after = Pt(2)
        
        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = WHITE
        p_t.space_after = Pt(12)
        
        p_b = tf.add_paragraph()
        p_b.text = text
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = RGBColor(203, 213, 225)
    
    # Conclusion message at the bottom
    tx_end = s7.shapes.add_textbox(Inches(0.8), Inches(6.2), Inches(11.7), Inches(0.8))
    tf_end = tx_end.text_frame
    p_end = tf_end.paragraphs[0]
    p_end.alignment = PP_ALIGN.CENTER
    p_end.text = "Merci pour votre attention ! Place à la suite de l'atelier."
    p_end.font.size = Pt(15)
    p_end.font.bold = True
    p_end.font.color.rgb = SECONDARY

    prs.save(output_path)
    print(f"Presentation saved to {output_path}")

if __name__ == "__main__":
    out_file = os.path.abspath("Presentation_DYNATSIMO_Pluviometrie_11h25-11h40.pptx")
    create_presentation(out_file)
