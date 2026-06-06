# =============================================================================
# src/skills.py – Skill: Generación de Reporte PDF con ReportLab (FR4.2)
# =============================================================================

import io
import datetime


def generate_pdf_report(score_correct: int, score_incorrect: int) -> bytes:
    """
    Genera un reporte PDF de desempeño académico usando ReportLab.
    FR4.2 / SRS §3.4.2.

    Args:
        score_correct:   Número de respuestas correctas en la sesión.
        score_incorrect: Número de respuestas incorrectas en la sesión.

    Returns:
        Bytes del PDF listo para descarga vía st.download_button.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        HRFlowable,
    )

    # ── Documento ──────────────────────────────────────────────────────────────
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles  = getSampleStyleSheet()
    total   = score_correct + score_incorrect
    pct     = (score_correct / total * 100) if total > 0 else 0.0
    fecha   = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # ── Paleta ICFES ───────────────────────────────────────────────────────────
    ICFES_BLUE   = colors.HexColor("#002B49")
    ICFES_GOLD   = colors.HexColor("#FFCD00")
    ICFES_LIGHT  = colors.HexColor("#E8F4FD")
    NEUTRAL_GREY = colors.HexColor("#CCCCCC")

    # ── Estilos tipográficos ───────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "ICFESTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=ICFES_BLUE,
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "ICFESSubtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=ICFES_BLUE,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "ICFESBody",
        parent=styles["Normal"],
        fontSize=11,
        leading=16,
    )
    footer_style = ParagraphStyle(
        "ICFESFooter",
        parent=styles["Normal"],
        fontSize=8,
        textColor=colors.grey,
    )

    # ── Story ──────────────────────────────────────────────────────────────────
    story = []

    story.append(Paragraph("🎓 Mentor Saber Pro – ICFES", title_style))
    story.append(Paragraph("Reporte de Desempeño Académico", subtitle_style))
    story.append(Paragraph(f"Generado el: {fecha}", body_style))
    story.append(HRFlowable(width="100%", thickness=2, color=ICFES_BLUE))
    story.append(Spacer(1, 0.5 * cm))

    # ── Tabla de puntaje ───────────────────────────────────────────────────────
    data = [
        ["Métrica",                 "Resultado"],
        ["✅ Respuestas Correctas",  str(score_correct)],
        ["❌ Respuestas Incorrectas", str(score_incorrect)],
        ["📊 Total de Preguntas",    str(total)],
        ["📈 Porcentaje de Éxito",   f"{pct:.1f}%"],
    ]

    table = Table(data, colWidths=[10 * cm, 6 * cm])
    table.setStyle(
        TableStyle([
            ("BACKGROUND",     (0, 0), (-1, 0),  ICFES_BLUE),
            ("TEXTCOLOR",      (0, 0), (-1, 0),  colors.white),
            ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
            ("FONTSIZE",       (0, 0), (-1, 0),  13),
            ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",         (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [ICFES_LIGHT, colors.white]),
            ("FONTSIZE",       (0, 1), (-1, -1), 12),
            ("GRID",           (0, 0), (-1, -1), 0.5, NEUTRAL_GREY),
            ("TOPPADDING",     (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING",  (0, 0), (-1, -1), 8),
            ("LEFTPADDING",    (0, 0), (-1, -1), 10),
            ("RIGHTPADDING",   (0, 0), (-1, -1), 10),
        ])
    )
    story.append(table)
    story.append(Spacer(1, 0.8 * cm))

    # ── Diagnóstico textual ────────────────────────────────────────────────────
    if total == 0:
        diagnostico = "Aún no has respondido ninguna pregunta. ¡Anímate a practicar!"
    elif pct >= 80:
        diagnostico = (
            "¡Excelente desempeño! Estás muy bien preparado/a para el examen Saber Pro. "
            "Continúa repasando los temas de mayor dificultad."
        )
    elif pct >= 60:
        diagnostico = (
            "Buen avance. Identifica los temas con más errores y enfócate "
            "en practicar con más simulacros en esas áreas."
        )
    else:
        diagnostico = (
            "Necesitas reforzar los conceptos fundamentales. Te recomendamos "
            "revisar los cuadernillos oficiales del ICFES con el Agente Profesor."
        )

    story.append(Paragraph("<b>Diagnóstico:</b>", body_style))
    story.append(Paragraph(diagnostico, body_style))
    story.append(Spacer(1, 1 * cm))

    # ── Pie de página ──────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=NEUTRAL_GREY))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "Este reporte fue generado automáticamente por Mentor Saber Pro v2.0. "
            "Toda la información proviene del corpus oficial de cuadernillos del ICFES.",
            footer_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
