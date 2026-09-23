import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ---------------------------------------------------------
# CONSTANTES DE COULEURS MODERNES & DESIGN PROFESSIONNEL
# ---------------------------------------------------------
NAVY_DEEP = RGBColor(11, 23, 44)       # #0B172C Fond sombre élégant
NAVY_CARD = RGBColor(19, 38, 68)       # #132644 Carte fond sombre
NAVY_CARD_BORDER = RGBColor(37, 72, 122)

BG_LIGHT = RGBColor(245, 247, 250)     # #F5F7FA Fond clair
CARD_WHITE = RGBColor(255, 255, 255)   # #FFFFFF
CARD_LIGHT_BORDER = RGBColor(226, 232, 240)

PRIMARY_BLUE = RGBColor(15, 76, 129)   # #0F4C81 Bleu roi profond
LIGHT_BLUE = RGBColor(239, 246, 255)   # #EFF6FF Bleu pastel
TEAL_ACCENT = RGBColor(13, 148, 136)   # #0D9488 Sarcelle dynamique
TEAL_LIGHT = RGBColor(230, 255, 250)   # #E6FFFA
TEAL_BORDER = RGBColor(94, 234, 212)

AMBER_ACCENT = RGBColor(217, 119, 6)   # #D97706 Ambre chaleureux
AMBER_LIGHT = RGBColor(254, 243, 199)  # #FEF3C7
AMBER_BORDER = RGBColor(252, 211, 77)

CORAL_ACCENT = RGBColor(225, 29, 72)   # #E11D48 Corail alerte
CORAL_LIGHT = RGBColor(255, 241, 242)

TEXT_MAIN = RGBColor(30, 41, 59)       # #1E293B Texte principal
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B Texte secondaire
TEXT_WHITE = RGBColor(255, 255, 255)
TEXT_SOFT_WHITE = RGBColor(226, 232, 240)


def create_visual_presentation(output_path):
    prs = Presentation()
    # 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def set_slide_bg(slide, color):
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = color

    def add_pill_badge(slide, left, top, width, height, text, bg_color, text_color, font_size=11.5):
        badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        badge.fill.solid()
        badge.fill.fore_color.rgb = bg_color
        badge.line.fill.background()
        tf = badge.text_frame
        tf.word_wrap = False
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        p.text = text
        p.font.name = "Segoe UI"
        p.font.size = Pt(font_size)
        p.font.bold = True
        p.font.color.rgb = text_color
        return badge

    def add_card(slide, left, top, width, height, bg_color, border_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.fill.background()
        return card

    def add_slide_header(slide, title, category, timing="11h25 – 11h40"):
        # Top banner pills
        add_pill_badge(slide, Inches(0.8), Inches(0.3), Inches(3.4), Inches(0.36), f"🌍 DYNATSIMO • {category.upper()}", TEAL_LIGHT, TEAL_ACCENT, font_size=11)
        add_pill_badge(slide, Inches(10.3), Inches(0.3), Inches(2.2), Inches(0.36), f"⏱️ {timing}", AMBER_LIGHT, AMBER_ACCENT, font_size=11.5)

        # Title (Increased size: 24pt)
        tx_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.75))
        tf_title = tx_title.text_frame
        tf_title.word_wrap = True
        p = tf_title.paragraphs[0]
        p.text = title
        p.font.name = "Segoe UI"
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = PRIMARY_BLUE

    # =========================================================================
    # SLIDE 1 : COUVERTURE HERO (GRANDS TITRES & KPI)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, NAVY_DEEP)

    # Accent Top Line
    top_line = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_line.fill.solid()
    top_line.fill.fore_color.rgb = TEAL_ACCENT
    top_line.line.fill.background()

    # Main Hero Container
    add_card(s1, Inches(0.8), Inches(0.65), Inches(11.733), Inches(4.3), NAVY_CARD, NAVY_CARD_BORDER)

    # Badges
    add_pill_badge(s1, Inches(1.2), Inches(1.05), Inches(2.4), Inches(0.38), "🌍 PROJET DYNATSIMO", RGBColor(16, 185, 129), NAVY_DEEP, font_size=11.5)
    add_pill_badge(s1, Inches(3.8), Inches(1.05), Inches(3.0), Inches(0.38), "🌧️ MODULE PLUVIOMÉTRIE", RGBColor(14, 165, 233), NAVY_DEEP, font_size=11.5)
    add_pill_badge(s1, Inches(9.6), Inches(1.05), Inches(2.5), Inches(0.38), "⏱️ 11h25 – 11h40 (15 min)", AMBER_LIGHT, AMBER_ACCENT, font_size=11.5)

    # Hero Titles (Increased size: 32pt & 17pt)
    tx_hero = s1.shapes.add_textbox(Inches(1.2), Inches(1.6), Inches(10.9), Inches(3.2))
    tf_hero = tx_hero.text_frame
    tf_hero.word_wrap = True
    
    p = tf_hero.paragraphs[0]
    p.text = "Présentation de l'Application & Débat Opérationnel"
    p.font.name = "Segoe UI"
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE
    p.space_after = Pt(10)

    p2 = tf_hero.add_paragraph()
    p2.text = "Objectiver le ciblage géographique, adapter l'appui et suivre l'impact agro-climatique réel dans le Grand Sud de Madagascar."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(17)
    p2.font.color.rgb = TEXT_SOFT_WHITE
    p2.space_after = Pt(16)

    p3 = tf_hero.add_paragraph()
    p3.text = "👤 Intervenant : Fandresena (en interaction avec PAH pour l'accroche)"
    p3.font.name = "Segoe UI"
    p3.font.size = Pt(15)
    p3.font.bold = True
    p3.font.color.rgb = TEAL_ACCENT

    # 3 Stat Cards at Bottom (Values: 28pt, Titles: 12pt, Desc: 11pt)
    kpis = [
        ("225", "COMMUNES SUIVIES", "Androy, Anosy & Atsimo-Andrefana", TEAL_ACCENT),
        ("45 ans", "SÉRIES HISTORIQUES", "Données CHIRPS (1981–2026)", PRIMARY_BLUE),
        ("15 min", "DÉMO & DÉBAT", "Ciblage, usage de l'aide & suivi réel", AMBER_ACCENT)
    ]

    for idx, (val, title, desc, col) in enumerate(kpis):
        left_pos = Inches(0.8 + idx * 4.0)
        card = add_card(s1, left_pos, Inches(5.15), Inches(3.733), Inches(1.8), CARD_WHITE)
        
        # Color accent strip on left
        strip = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(5.15), Inches(0.14), Inches(1.8))
        strip.fill.solid()
        strip.fill.fore_color.rgb = col
        strip.line.fill.background()

        tx = s1.shapes.add_textbox(left_pos + Inches(0.25), Inches(5.25), Inches(3.3), Inches(1.6))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = "Segoe UI"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(1)

        p_t = tf.add_paragraph()
        p_t.text = title
        p_t.font.name = "Segoe UI"
        p_t.font.size = Pt(11.5)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_MUTED
        p_t.space_after = Pt(2)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.name = "Segoe UI"
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 2 : ACCROCHE DUO (FANDRESENA & PAH) - 2 MIN
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s2, BG_LIGHT)
    add_slide_header(s2, "Accroche : Du Défi Terrain à la Décision Basée sur les Données", "Séquence 1 (2 min)")

    # Left Card : PAH
    add_card(s2, Inches(0.8), Inches(1.55), Inches(5.65), Inches(4.35), CARD_WHITE, CARD_LIGHT_BORDER)
    h_strip_pah = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.55), Inches(5.65), Inches(0.5))
    h_strip_pah.fill.solid()
    h_strip_pah.fill.fore_color.rgb = CORAL_LIGHT
    h_strip_pah.line.fill.background()
    
    tx_pah_h = s2.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.2), Inches(0.4))
    p = tx_pah_h.text_frame.paragraphs[0]
    p.text = "🚨 L'INTERPELLATION TERRAIN — PAH"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CORAL_ACCENT

    tx_pah = s2.shapes.add_textbox(Inches(1.05), Inches(2.15), Inches(5.15), Inches(3.6))
    tf = tx_pah.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "« Sur le terrain, quand la saison des pluies est tardive ou déficitaire, comment sait-on exactement quelles communes sont les plus durement touchées sans attendre les premiers signaux de détresse ? »"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14.5)
    p.font.italic = True
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "⚡ Risques sans données factuelles :\n• Choix de ciblage contestés par les communautés\n• Réponse tardive en réaction à la crise\n• Manque de visibilité sur les poches arides"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.color.rgb = RGBColor(185, 28, 28)

    # Right Card : FANDRESENA
    add_card(s2, Inches(6.88), Inches(1.55), Inches(5.65), Inches(4.35), CARD_WHITE, CARD_LIGHT_BORDER)
    h_strip_fan = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.88), Inches(1.55), Inches(5.65), Inches(0.5))
    h_strip_fan.fill.solid()
    h_strip_fan.fill.fore_color.rgb = TEAL_LIGHT
    h_strip_fan.line.fill.background()
    
    tx_fan_h = s2.shapes.add_textbox(Inches(7.1), Inches(1.6), Inches(5.2), Inches(0.4))
    p = tx_fan_h.text_frame.paragraphs[0]
    p.text = "💡 LA RÉPONSE DYNATSIMO — FANDRESENA"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT

    tx_fan = s2.shapes.add_textbox(Inches(7.15), Inches(2.15), Inches(5.15), Inches(3.6))
    tf = tx_fan.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "« C’est tout l’enjeu de DYNATSIMO : transformer 45 ans d’observations satellitaires en indicateurs spatiaux clairs pour objectiver nos arbitrages et anticiper les chocs dans le Grand Sud. »"
    p.font.name = "Segoe UI"
    p.font.size = Pt(14.5)
    p.font.italic = True
    p.font.bold = True
    p.font.color.rgb = TEXT_MAIN
    p.space_after = Pt(12)

    p = tf.add_paragraph()
    p.text = "✨ Bénéfices immédiats pour les projets :\n• Cartographie précise des cumuls & anomalies\n• Détection précoce du démarrage effectif des pluies\n• Justification technique transparente et auditable"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.color.rgb = TEAL_ACCENT

    # Bottom Summary Banner (Increased font: 13.5pt)
    add_card(s2, Inches(0.8), Inches(6.05), Inches(11.733), Inches(1.0), NAVY_DEEP)
    tx_bot = s2.shapes.add_textbox(Inches(1.1), Inches(6.15), Inches(11.1), Inches(0.8))
    tf_bot = tx_bot.text_frame
    p = tf_bot.paragraphs[0]
    p.text = "🎯 OBJECTIF DE LA SESSION (15 MIN)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    p2 = tf_bot.add_paragraph()
    p2.text = "1. Découvrir les fonctions clés du module Pluviométrie   |   2. Confronter l'outil aux défis de ciblage et de suivi."
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(13.5)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 3 : DÉMO LIVE — 3 VUES STRATÉGIQUES (6 MIN)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s3, BG_LIGHT)
    add_slide_header(s3, "Démonstration Live : 3 Vues Clés pour Prendre des Décisions", "Séquence 2 (6 min)")

    demo_cards = [
        ("01", "CARTOGRAPHIE & GRADIENT", "Onglet Cartographie",
         "• Révèle le gradient Est-Ouest (900 mm Anosy vs <350 mm Androy)\n• Isohyètes 50 mm & anomalies communales\n• Détection immédiate des poches de déficit",
         "« Élimine les estimations subjectives pour prioriser les zones »",
         PRIMARY_BLUE, LIGHT_BLUE),
        
        ("02", "SAISON DES PLUIES", "Onglet Statistiques",
         "• Date réelle de démarrage des pluies\n• Détection des faux départs de semis\n• Évaluation des ruptures en cours de cycle",
         "« Une pluie tardive de 45j compromet la récolte même si le cumul est bon »",
         TEAL_ACCENT, TEAL_LIGHT),
        
        ("03", "CLIMATOLOGIE & ANOMALIES", "Onglet Vue d'ensemble",
         "• Comparaison directe avec 1981–2026\n• Qualification de la sévérité du choc\n• Séries continues pour situer les crises",
         "« Permet d'ajuster le dimensionnement de l'aide à l'intensité du choc »",
         AMBER_ACCENT, AMBER_LIGHT)
    ]

    for idx, (num, title, tab, bullets, quote, col, bg_col) in enumerate(demo_cards):
        left_pos = Inches(0.8 + idx * 4.0)
        card = add_card(s3, left_pos, Inches(1.55), Inches(3.733), Inches(4.55), CARD_WHITE, CARD_LIGHT_BORDER)
        
        # Header Box with number
        h_box = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, left_pos, Inches(1.55), Inches(3.733), Inches(0.75))
        h_box.fill.solid()
        h_box.fill.fore_color.rgb = col
        h_box.line.fill.background()

        tx_h = s3.shapes.add_textbox(left_pos + Inches(0.18), Inches(1.58), Inches(3.35), Inches(0.65))
        tf_h = tx_h.text_frame
        p = tf_h.paragraphs[0]
        p.text = f"[{num}] {title}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        
        p_sub = tf_h.add_paragraph()
        p_sub.text = f"📍 {tab}"
        p_sub.font.name = "Segoe UI"
        p_sub.font.size = Pt(10)
        p_sub.font.color.rgb = TEXT_SOFT_WHITE

        # Content (Bullets font: 12.5pt)
        tx_c = s3.shapes.add_textbox(left_pos + Inches(0.18), Inches(2.4), Inches(3.35), Inches(2.4))
        tf_c = tx_c.text_frame
        tf_c.word_wrap = True
        
        p = tf_c.paragraphs[0]
        p.text = bullets
        p.font.name = "Segoe UI"
        p.font.size = Pt(12.5)
        p.font.color.rgb = TEXT_MAIN
        p.space_after = Pt(8)

        # Quote box (Impact text: 11.5pt)
        q_box = add_card(s3, left_pos + Inches(0.18), Inches(4.75), Inches(3.35), Inches(1.25), bg_col, col)
        tx_q = s3.shapes.add_textbox(left_pos + Inches(0.22), Inches(4.8), Inches(3.25), Inches(1.15))
        tf_q = tx_q.text_frame
        tf_q.word_wrap = True
        p_q = tf_q.paragraphs[0]
        p_q.text = f"💡 Impact :\n{quote}"
        p_q.font.name = "Segoe UI"
        p_q.font.size = Pt(11.5)
        p_q.font.bold = True
        p_q.font.italic = True
        p_q.font.color.rgb = col

    # Bottom Tip (Font size: 12.5pt)
    add_pill_badge(s3, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.65), "🖥️ DÉMO DISPONIBLE SUR http://localhost:5173 • COUVERTURE 225 COMMUNES DU GRAND SUD", RGBColor(224, 242, 254), PRIMARY_BLUE, font_size=12)

    # =========================================================================
    # SLIDE 4 : DÉBAT 1 — CHOIX DE CIBLAGE (2 MIN)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s4, BG_LIGHT)
    add_slide_header(s4, "Échange 1 : Quels choix de ciblage posent le plus de difficultés ?", "Débat 1/3 (2 min)")

    # Left Card
    add_card(s4, Inches(0.8), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_l = s4.shapes.add_textbox(Inches(1.1), Inches(1.75), Inches(5.1), Inches(3.2))
    tf = tx_l.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "⚠️ LES DILEMMES DU CIBLAGE CLASSIQUE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = CORAL_ACCENT
    p.space_after = Pt(10)

    p = tf.add_paragraph()
    p.text = "• Tension entre ciblage géographique (communes prioritaires) et ciblage catégoriel (ménages vulnérables).\n• Risques de contestations locales et de pressions lors de la sélection des bénéficiaires.\n• Budgets limités imposant des arbitrages délicats."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Right Card
    add_card(s4, Inches(6.88), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_r = s4.shapes.add_textbox(Inches(7.18), Inches(1.75), Inches(5.1), Inches(3.2))
    tf = tx_r.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "✨ L'APPORT DÉCISIF DE DYNATSIMO"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(10)

    p = tf.add_paragraph()
    p.text = "• Données satellitaires neutres, vérifiables et auditables à l'échelle de 225 communes.\n• Dépolitisation du choix des zones d'intervention grâce à la mesure du déficit pluviométrique.\n• Plaidoyer transparent auprès des autorités et bailleurs."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Interactive Debate Box at Bottom (Question size: 15.5pt)
    add_card(s4, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.75), AMBER_LIGHT, AMBER_ACCENT)
    tx_q1 = s4.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(1.5))
    tf_q1 = tx_q1.text_frame
    tf_q1.word_wrap = True
    
    p = tf_q1.paragraphs[0]
    p.text = "🗣️ QUESTION & RELANCE POUR LA SALLE :"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    p.space_after = Pt(4)

    p2 = tf_q1.add_paragraph()
    p2.text = "« Dans vos projets, comment arbitrez-vous quand une commune entière est affectée par la sécheresse mais que vos capacités ne permettent de cibler qu'une fraction des ménages ? »"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 5 : DÉBAT 2 — QUI UTILISE / TRAVAILLE / BÉNÉFICIE ? (2 MIN)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s5, BG_LIGHT)
    add_slide_header(s5, "Échange 2 : Qui utilise l'appui, fournit le travail et en bénéficie ?", "Débat 2/3 (2 min)")

    # Left Card
    add_card(s5, Inches(0.8), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_l2 = s5.shapes.add_textbox(Inches(1.1), Inches(1.75), Inches(5.1), Inches(3.2))
    tf2 = tx_l2.text_frame
    tf2.word_wrap = True
    
    p = tf2.paragraphs[0]
    p.text = "👥 DYNAMIQUES SOCIALES & CHARGE DE TRAVAIL"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(10)

    p = tf2.add_paragraph()
    p.text = "• Les femmes et les jeunes fournissent la majeure partie du travail agricole pénible (semis, désherbage, corvées d'eau).\n• Le contrôle de la récolte, des semences et des revenus monétaires est souvent concentré chez le chef de ménage.\n• Décalage fréquent entre charge de travail et bénéfices."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Right Card
    add_card(s5, Inches(6.88), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_r2 = s5.shapes.add_textbox(Inches(7.18), Inches(1.75), Inches(5.1), Inches(3.2))
    tf2_r = tx_r2.text_frame
    tf2_r.word_wrap = True
    
    p = tf2_r.paragraphs[0]
    p.text = "🌧️ CROISEMENT AVEC LE CHOC PLUVIOMÉTRIQUE"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(10)

    p = tf2_r.add_paragraph()
    p.text = "• En période de sécheresse, la corvée d'eau des femmes explose (perte d'heures productives aux champs).\n• La crise précipite la vente d'actifs et la déscolarisation précoce des enfants.\n• DYNATSIMO permet de corréler le déficit pluviométrique aux vulnérabilités intra-ménages."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Interactive Debate Box at Bottom (Question size: 15.5pt)
    add_card(s5, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.75), AMBER_LIGHT, AMBER_ACCENT)
    tx_q2 = s5.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(1.5))
    tf_q2 = tx_q2.text_frame
    tf_q2.word_wrap = True
    
    p = tf_q2.paragraphs[0]
    p.text = "🗣️ QUESTION & RELANCE POUR LA SALLE :"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    p.space_after = Pt(4)

    p2 = tf_q2.add_paragraph()
    p2.text = "« Lorsque vous distribuez un appui (intrants ou cash), observez-vous un décalage entre les personnes qui travaillent la parcelle et celles qui en retirent les bénéfices ? Comment adapter l'appui ? »"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 6 : DÉBAT 3 — QUE SUIT-ON APRÈS L'ATTRIBUTION DE L'AIDE ? (2 MIN)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s6, BG_LIGHT)
    add_slide_header(s6, "Échange 3 : Que suit-on après l'attribution de l'aide ?", "Débat 3/3 (2 min)")

    # Left Card
    add_card(s6, Inches(0.8), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_l3 = s6.shapes.add_textbox(Inches(1.1), Inches(1.75), Inches(5.1), Inches(3.2))
    tf3 = tx_l3.text_frame
    tf3.word_wrap = True
    
    p = tf3.paragraphs[0]
    p.text = "📦 LE SUIVI CLASSIQUE (INDICATEURS DE MOYENS)"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE
    p.space_after = Pt(10)

    p = tf3.add_paragraph()
    p.text = "• Suivi rigoureux des réalisations logistiques : tonnes de semences livrées, montants de cash distribués, listes de bénéficiaires émargées.\n• Mais manque d'indicateurs sur la réussite agronomique réelle après distribution.\n• Risque d'imputer un échec aux bénéficiaires alors qu'une sécheresse post-semis a tout détruit."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Right Card
    add_card(s6, Inches(6.88), Inches(1.55), Inches(5.65), Inches(3.55), CARD_WHITE, CARD_LIGHT_BORDER)
    tx_r3 = s6.shapes.add_textbox(Inches(7.18), Inches(1.75), Inches(5.1), Inches(3.2))
    tf3_r = tx_r3.text_frame
    tf3_r.word_wrap = True
    
    p = tf3_r.paragraphs[0]
    p.text = "🛰️ LE DOUBLE SUIVI SATELLITAIRE DYNATSIMO"
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = TEAL_ACCENT
    p.space_after = Pt(10)

    p = tf3_r.add_paragraph()
    p.text = "• 1. Suivi de la pluie effective post-distribution (CHIRPS) pour valider si le semis a reçu de l'eau.\n• 2. Suivi de la reprise végétale (NDVI Landsat/Sentinel) pour mesurer la vitalité réelle de la biomasse.\n• Évaluation d'impact objective sans mobiliser d'enquêtes lourdes et coûteuses."
    p.font.name = "Segoe UI"
    p.font.size = Pt(13)
    p.font.color.rgb = TEXT_MAIN

    # Interactive Debate Box at Bottom (Question size: 15.5pt)
    add_card(s6, Inches(0.8), Inches(5.25), Inches(11.733), Inches(1.75), AMBER_LIGHT, AMBER_ACCENT)
    tx_q3 = s6.shapes.add_textbox(Inches(1.1), Inches(5.35), Inches(11.1), Inches(1.5))
    tf_q3 = tx_q3.text_frame
    tf_q3.word_wrap = True
    
    p = tf_q3.paragraphs[0]
    p.text = "🗣️ QUESTION & RELANCE POUR LA SALLE :"
    p.font.name = "Segoe UI"
    p.font.size = Pt(12.5)
    p.font.bold = True
    p.font.color.rgb = AMBER_ACCENT
    p.space_after = Pt(4)

    p2 = tf_q3.add_paragraph()
    p2.text = "« Suivez-vous uniquement le taux de distribution, ou mesurez-vous aussi les conditions agro-climatiques réelles après la distribution pour évaluer l'impact ? »"
    p2.font.name = "Segoe UI"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_MAIN

    # =========================================================================
    # SLIDE 7 : SYNTHÈSE & PERSPECTIVES (DARK FINALE)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s7, NAVY_DEEP)

    # Accent Top Line
    top_line7 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
    top_line7.fill.solid()
    top_line7.fill.fore_color.rgb = TEAL_ACCENT
    top_line7.line.fill.background()

    # Title & Badge
    add_pill_badge(s7, Inches(0.8), Inches(0.35), Inches(3.0), Inches(0.38), "✨ SYNTHÈSE OPÉRATIONNELLE", TEAL_ACCENT, NAVY_DEEP, font_size=12)
    
    tx_s7 = s7.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.75))
    p = tx_s7.text_frame.paragraphs[0]
    p.text = "DYNATSIMO : Une Boussole à Chaque Étape du Cycle de Projet"
    p.font.name = "Segoe UI"
    p.font.size = Pt(25)
    p.font.bold = True
    p.font.color.rgb = TEXT_WHITE

    # 3 Workflow Pillar Cards
    pillars = [
        ("EN AMONT", "Ciblage Objectif",
         "• Identifier les 225 communes en stress hydrique avéré\n• Dépolitiser le choix géographique des interventions\n• Dimensionner l'assistance selon la sévérité du choc",
         PRIMARY_BLUE, RGBColor(29, 78, 216)),
        
        ("EN COURS", "Adaptation & Calendrier",
         "• Suivre le démarrage effectif de la saison des pluies\n• Alerter sur les faux départs et ruptures de cycle\n• Ajuster le calendrier logistique des distributions",
         TEAL_ACCENT, RGBColor(16, 185, 129)),
        
        ("EN AVAL", "Mesure d'Impact Réel",
         "• Corréler pluie effective et réponse végétale (NDVI)\n• Évaluer le succès agronomique post-attribution\n• Produire des preuves tangibles pour les bailleurs",
         AMBER_ACCENT, RGBColor(245, 158, 11))
    ]

    for idx, (phase, role, text, col, col_light) in enumerate(pillars):
        left_pos = Inches(0.8 + idx * 4.0)
        card = add_card(s7, left_pos, Inches(1.7), Inches(3.733), Inches(4.45), NAVY_CARD, NAVY_CARD_BORDER)
        
        # Header Badge inside card
        add_pill_badge(s7, left_pos + Inches(0.25), Inches(1.95), Inches(2.0), Inches(0.36), phase, col, NAVY_DEEP, font_size=12)

        tx = s7.shapes.add_textbox(left_pos + Inches(0.25), Inches(2.45), Inches(3.233), Inches(3.5))
        tf = tx.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = role
        p.font.name = "Segoe UI"
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = TEXT_WHITE
        p.space_after = Pt(12)

        p_b = tf.add_paragraph()
        p_b.text = text
        p_b.font.name = "Segoe UI"
        p_b.font.size = Pt(13)
        p_b.font.color.rgb = TEXT_SOFT_WHITE

    # Bottom Callout / Thank you (Increased font: 16pt)
    tx_end = s7.shapes.add_textbox(Inches(0.8), Inches(6.35), Inches(11.733), Inches(0.7))
    tf_end = tx_end.text_frame
    p_end = tf_end.paragraphs[0]
    p_end.alignment = PP_ALIGN.CENTER
    p_end.text = "🤝 Merci pour vos contributions ! Place à la suite des travaux de l'atelier."
    p_end.font.name = "Segoe UI"
    p_end.font.size = Pt(16)
    p_end.font.bold = True
    p_end.font.color.rgb = TEAL_ACCENT

    prs.save(output_path)
    print(f"Presentation with large fonts saved to: {output_path}")

if __name__ == "__main__":
    out_file_primary = os.path.abspath("Presentation_DYNATSIMO_Pluviometrie_Grandes_Polices.pptx")
    create_visual_presentation(out_file_primary)
    
    # Try updating the original name as well if not locked
    out_file_orig = os.path.abspath("Presentation_DYNATSIMO_Pluviometrie_11h25-11h40.pptx")
    try:
        create_visual_presentation(out_file_orig)
    except PermissionError:
        print("Note: Original file is open in PowerPoint. New version saved to:", out_file_primary)

