#!/usr/bin/env python3
"""
Genera el PDF maestro del Benchmark CODEC-CORTEX con ReportLab.

Compila:
- Caratula + TOC
- scientific_report.md (parseado a ReportLab Paragraphs)
- claim_matrix.md
- regression_report.md
- metric_discovery_report.md
- comparative_analysis.md
- Diagramas embebidos (PNG)

Salida: /home/z/my-project/download/benchmark-cortex/Benchmark_CODEC_CORTEX_v1.0.pdf
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

FONT_DIR = "/usr/share/fonts"
pdfmetrics.registerFont(TTFont("NotoSerifSC", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf"))
pdfmetrics.registerFont(TTFont("NotoSerifSC-Bold", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf"))
pdfmetrics.registerFont(TTFont("NotoSerifSC-Light", f"{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Light.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", f"{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf"))
registerFontFamily(
    "NotoSerifSC",
    normal="NotoSerifSC",
    bold="NotoSerifSC-Bold",
    italic="NotoSerifSC",
    boldItalic="NotoSerifSC-Bold",
)

# ---------------------------------------------------------------------------
# Palette (HCORTEX-inspired, professional scientific)
# ---------------------------------------------------------------------------

# Colors based on palette.cascade idea: blue primary, with semantic accents
PRIMARY = colors.HexColor("#1E40AF")   # dark blue
ACCENT = colors.HexColor("#2563EB")    # blue
SUCCESS = colors.HexColor("#16A34A")   # green
WARNING = colors.HexColor("#F59E0B")   # amber
DANGER = colors.HexColor("#DC2626")    # red
INK = colors.HexColor("#0F172A")       # near black
SLATE = colors.HexColor("#475569")     # slate
MUTED = colors.HexColor("#94A3B8")     # muted
BG_SOFT = colors.HexColor("#F8FAFC")   # very light
BG_CODE = colors.HexColor("#F1F5F9")   # code bg
BORDER = colors.HexColor("#E2E8F0")    # light border
TABLE_HEADER = colors.HexColor("#1E40AF")
TABLE_HEADER_TEXT = colors.white

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------

def build_styles():
    base = getSampleStyleSheet()
    s = {}
    s["Title"] = ParagraphStyle("Title", parent=base["Title"],
                                 fontName="NotoSerifSC-Bold", fontSize=26,
                                 textColor=PRIMARY, alignment=TA_CENTER,
                                 spaceAfter=14, leading=32)
    s["Subtitle"] = ParagraphStyle("Subtitle", parent=base["Normal"],
                                    fontName="NotoSerifSC", fontSize=14,
                                    textColor=SLATE, alignment=TA_CENTER,
                                    spaceAfter=10, leading=18)
    s["H1"] = ParagraphStyle("H1", parent=base["Heading1"],
                              fontName="NotoSerifSC-Bold", fontSize=20,
                              textColor=PRIMARY, spaceBefore=18, spaceAfter=10,
                              leading=26, keepWithNext=True)
    s["H2"] = ParagraphStyle("H2", parent=base["Heading2"],
                              fontName="NotoSerifSC-Bold", fontSize=15,
                              textColor=ACCENT, spaceBefore=14, spaceAfter=6,
                              leading=20, keepWithNext=True)
    s["H3"] = ParagraphStyle("H3", parent=base["Heading3"],
                              fontName="NotoSerifSC-Bold", fontSize=12,
                              textColor=INK, spaceBefore=10, spaceAfter=4,
                              leading=16, keepWithNext=True)
    s["Body"] = ParagraphStyle("Body", parent=base["BodyText"],
                                fontName="NotoSerifSC", fontSize=10,
                                textColor=INK, alignment=TA_JUSTIFY,
                                spaceAfter=6, leading=14)
    s["BodyLeft"] = ParagraphStyle("BodyLeft", parent=s["Body"], alignment=TA_LEFT)
    s["Bullet"] = ParagraphStyle("Bullet", parent=s["Body"], leftIndent=15,
                                  bulletIndent=5, spaceAfter=3)
    s["Code"] = ParagraphStyle("Code", parent=base["Code"],
                                fontName="DejaVuMono", fontSize=8.5,
                                textColor=INK, backColor=BG_CODE,
                                borderColor=BORDER, borderWidth=0.5,
                                borderPadding=4, leftIndent=8, rightIndent=8,
                                spaceBefore=4, spaceAfter=8, leading=11)
    s["Caption"] = ParagraphStyle("Caption", parent=base["Italic"],
                                   fontName="NotoSerifSC", fontSize=9,
                                   textColor=SLATE, alignment=TA_CENTER,
                                   spaceAfter=10, spaceBefore=2, leading=12)
    s["Quote"] = ParagraphStyle("Quote", parent=s["Body"],
                                 leftIndent=15, rightIndent=15,
                                 fontName="NotoSerifSC", fontSize=10,
                                 textColor=SLATE, spaceAfter=8, leading=14,
                                 backColor=BG_SOFT, borderColor=ACCENT,
                                 borderWidth=0, borderPadding=8)
    s["TableCell"] = ParagraphStyle("TableCell", parent=base["Normal"],
                                     fontName="NotoSerifSC", fontSize=8.5,
                                     textColor=INK, alignment=TA_LEFT, leading=11)
    s["TableHeader"] = ParagraphStyle("TableHeader", parent=base["Normal"],
                                       fontName="NotoSerifSC-Bold", fontSize=9,
                                       textColor=TABLE_HEADER_TEXT, alignment=TA_CENTER, leading=11)
    s["TOCEntry1"] = ParagraphStyle("TOCEntry1", parent=base["Normal"],
                                     fontName="NotoSerifSC-Bold", fontSize=11,
                                     textColor=INK, leftIndent=0, spaceAfter=4, leading=15)
    s["TOCEntry2"] = ParagraphStyle("TOCEntry2", parent=base["Normal"],
                                     fontName="NotoSerifSC", fontSize=10,
                                     textColor=SLATE, leftIndent=18, spaceAfter=2, leading=13)
    s["CoverMeta"] = ParagraphStyle("CoverMeta", parent=base["Normal"],
                                     fontName="NotoSerifSC", fontSize=10,
                                     textColor=SLATE, alignment=TA_CENTER, leading=14)
    s["CoverHero"] = ParagraphStyle("CoverHero", parent=base["Normal"],
                                     fontName="NotoSerifSC-Bold", fontSize=32,
                                     textColor=PRIMARY, alignment=TA_CENTER, leading=40)
    s["CoverSub"] = ParagraphStyle("CoverSub", parent=base["Normal"],
                                    fontName="NotoSerifSC", fontSize=14,
                                    textColor=SLATE, alignment=TA_CENTER, leading=18,
                                    spaceAfter=8)
    s["CoverTag"] = ParagraphStyle("CoverTag", parent=base["Normal"],
                                    fontName="NotoSerifSC", fontSize=9,
                                    textColor=ACCENT, alignment=TA_CENTER, leading=12)
    return s


STYLES = build_styles()


# ---------------------------------------------------------------------------
# Markdown -> ReportLab flowables (simplified parser)
# ---------------------------------------------------------------------------

def md_to_flowables(md_text: str, images_dir: Path) -> List:
    """Convierte texto Markdown a flowables de ReportLab.

    Soporta:
    - # ## ### headings
    - tablas markdown | a|b |
    - bloques de codigo ``` ```
    - imagenes ![alt](path)
    - listas con - o *
    - blockquotes >
    - parrafos
    """
    flow = []
    lines = md_text.split("\n")
    i = 0
    in_code = False
    code_buf = []
    table_buf = []
    in_table = False

    while i < len(lines):
        line = lines[i]

        # Code fence
        if line.strip().startswith("```"):
            if in_code:
                # Close code block
                code_text = "\n".join(code_buf)
                # escape HTML special chars
                code_text = code_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                flow.append(Paragraph(code_text, STYLES["Code"]))
                code_buf = []
                in_code = False
            else:
                # Flush any table
                if in_table:
                    _flush_table(flow, table_buf)
                    table_buf = []
                    in_table = False
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        # Table detection: line contains | and next line is separator |---|
        if "|" in line and line.strip().startswith("|") and i + 1 < len(lines) and re.match(r'^\s*\|[\s\-:|]+\|?\s*$', lines[i + 1]):
            if not in_table:
                in_table = True
                table_buf = []
            # Skip header content (we'll capture it)
            table_buf.append(line)
            i += 1
            # Skip separator
            if i < len(lines) and re.match(r'^\s*\|[\s\-:|]+\|?\s*$', lines[i]):
                i += 1
            # Collect table rows
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_buf.append(lines[i])
                i += 1
            _flush_table(flow, table_buf)
            table_buf = []
            in_table = False
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.+)$', line)
        if m:
            level = len(m.group(1))
            text = _inline_format(m.group(2).strip())
            if level == 1:
                flow.append(Paragraph(text, STYLES["H1"]))
            elif level == 2:
                flow.append(Paragraph(text, STYLES["H2"]))
            else:
                flow.append(Paragraph(text, STYLES["H3"]))
            i += 1
            continue

        # Image
        m = re.match(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if m:
            alt = m.group(1)
            img_path = m.group(2)
            # Resolve relative path
            if not img_path.startswith("/"):
                img_full = images_dir / img_path
            else:
                img_full = Path(img_path)
            if img_full.exists():
                # Add image scaled to fit page width
                from PIL import Image as PILImage
                try:
                    with PILImage.open(img_full) as im:
                        iw, ih = im.size
                    max_w = 16 * cm
                    max_h = 19 * cm
                    ratio = min(max_w / iw * 72 / 96, max_h / ih * 72 / 96)
                    # ReportLab Image uses points; convert from pixels at 96 DPI
                    w_pt = iw * 72 / 96
                    h_pt = ih * 72 / 96
                    if w_pt > max_w:
                        ratio = max_w / w_pt
                        w_pt *= ratio
                        h_pt *= ratio
                    if h_pt > max_h:
                        ratio = max_h / h_pt
                        w_pt *= ratio
                        h_pt *= ratio
                    flow.append(Image(str(img_full), width=w_pt, height=h_pt))
                    if alt:
                        flow.append(Paragraph(f"<i>{alt}</i>", STYLES["Caption"]))
                except Exception as e:
                    flow.append(Paragraph(f"[Image error: {img_path}: {e}]", STYLES["Body"]))
            else:
                flow.append(Paragraph(f"[Image not found: {img_path}]", STYLES["Body"]))
            i += 1
            continue

        # Blockquote
        if line.strip().startswith(">"):
            quote_text = line.strip()[1:].strip()
            # Collect multi-line quotes
            while i + 1 < len(lines) and lines[i + 1].strip().startswith(">"):
                i += 1
                quote_text += " " + lines[i].strip()[1:].strip()
            flow.append(Paragraph(_inline_format(quote_text), STYLES["Quote"]))
            i += 1
            continue

        # Bullet list
        if re.match(r'^\s*[-*]\s+', line):
            bullet_text = re.sub(r'^\s*[-*]\s+', '', line)
            flow.append(Paragraph("• " + _inline_format(bullet_text), STYLES["Bullet"]))
            i += 1
            continue

        # Numbered list
        m = re.match(r'^\s*(\d+)\.\s+(.+)$', line)
        if m:
            num = m.group(1)
            text = m.group(2)
            flow.append(Paragraph(f"{num}. " + _inline_format(text), STYLES["Bullet"]))
            i += 1
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            flow.append(Spacer(1, 6))
            flow.append(Table([[""]], colWidths=[16 * cm], rowHeights=[1],
                              style=TableStyle([("LINEABOVE", (0, 0), (-1, 0), 0.5, BORDER)])))
            flow.append(Spacer(1, 6))
            i += 1
            continue

        # Empty line
        if not line.strip():
            i += 1
            continue

        # Regular paragraph (collect multi-line)
        para_lines = [line]
        while i + 1 < len(lines) and lines[i + 1].strip() and not _is_block_start(lines[i + 1]):
            i += 1
            para_lines.append(lines[i])
        text = " ".join(para_lines)
        flow.append(Paragraph(_inline_format(text), STYLES["Body"]))
        i += 1

    return flow


def _is_block_start(line: str) -> bool:
    """Verifica si una linea inicia un nuevo bloque (heading, table, code, list)."""
    s = line.strip()
    if not s:
        return True
    if re.match(r'^#{1,6}\s', s):
        return True
    if s.startswith("|"):
        return True
    if s.startswith("```"):
        return True
    if s.startswith(">"):
        return True
    if re.match(r'^\s*[-*]\s+', s):
        return True
    if re.match(r'^\s*\d+\.\s+', s):
        return True
    if s.startswith("!["):
        return True
    if s in ("---", "***", "___"):
        return True
    return False


def _inline_format(text: str) -> str:
    """Convierte **bold**, *italic*, `code` inline a tags ReportLab."""
    # Escape & < > first
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Italic (single * not **)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font face="DejaVuMono">\1</font>', text)
    return text


def _flush_table(flow: List, table_buf: List[str]):
    """Convierte lineas markdown table a un Table de ReportLab."""
    if not table_buf:
        return
    rows = []
    for line in table_buf:
        # Remove leading/trailing |
        s = line.strip()
        if s.startswith("|"):
            s = s[1:]
        if s.endswith("|"):
            s = s[:-1]
        cells = [c.strip() for c in s.split("|")]
        rows.append(cells)

    if not rows:
        return

    # Determine col count
    max_cols = max(len(r) for r in rows)
    # Pad rows
    for r in rows:
        while len(r) < max_cols:
            r.append("")

    # Build Paragraphs for cells
    data = []
    for i, row in enumerate(rows):
        style = STYLES["TableHeader"] if i == 0 else STYLES["TableCell"]
        cells = [Paragraph(_inline_format(c), style) for c in row]
        data.append(cells)

    # Compute column widths: proportional to content but bounded
    available = 16 * cm
    if max_cols > 6:
        # Many columns: equal width with small padding
        col_widths = [available / max_cols] * max_cols
        cell_font_size = 7
        cell_padding = 2
    else:
        col_widths = []
        for col_idx in range(max_cols):
            max_len = max(len(str(rows[r][col_idx])) for r in range(len(rows)))
            col_widths.append(max(max_len, 5))
        total = sum(col_widths)
        col_widths = [w / total * available for w in col_widths]
        col_widths = [min(w, 7 * cm) for w in col_widths]
        if sum(col_widths) < available:
            scale = available / sum(col_widths)
            col_widths = [w * scale for w in col_widths]
        cell_font_size = 8
        cell_padding = 4

    # Override cell style with smaller font for many-column tables
    if max_cols > 6:
        data = []
        for i, row in enumerate(rows):
            style = ParagraphStyle("TCsmall", parent=STYLES["TableHeader"] if i == 0 else STYLES["TableCell"],
                                    fontSize=cell_font_size, leading=cell_font_size + 2)
            cells = [Paragraph(_inline_format(c), style) for c in row]
            data.append(cells)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER),
        ("TEXTCOLOR", (0, 0), (-1, 0), TABLE_HEADER_TEXT),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), cell_font_size),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
        ("TOPPADDING", (0, 0), (-1, 0), 5),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_SOFT]),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), cell_padding),
        ("RIGHTPADDING", (0, 0), (-1, -1), cell_padding),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 6))


# ---------------------------------------------------------------------------
# Page templates
# ---------------------------------------------------------------------------

class BenchmarkDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        super().__init__(filename, **kw)
        page_w, page_h = A4
        margin = 1.8 * cm
        # Cover frame: full page
        cover_frame = Frame(0, 0, page_w, page_h,
                            leftPadding=margin, rightPadding=margin,
                            topPadding=margin, bottomPadding=margin,
                            id="cover", showBoundary=0)
        # Body frame
        body_frame = Frame(margin, margin + 1.2 * cm,
                           page_w - 2 * margin, page_h - 2 * margin - 2 * cm,
                           id="body", showBoundary=0)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=self._cover_bg),
            PageTemplate(id="Body", frames=[body_frame], onPage=self._body_header),
        ])

    def _cover_bg(self, canvas, doc):
        page_w, page_h = A4
        canvas.saveState()
        # Soft background
        canvas.setFillColor(BG_SOFT)
        canvas.rect(0, 0, page_w, page_h, fill=1, stroke=0)
        # Top color band
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, page_h - 1.5 * cm, page_w, 1.5 * cm, fill=1, stroke=0)
        # Bottom thin band
        canvas.setFillColor(ACCENT)
        canvas.rect(0, 0, page_w, 0.4 * cm, fill=1, stroke=0)
        # Decorative side line
        canvas.setStrokeColor(ACCENT)
        canvas.setLineWidth(2)
        canvas.line(1.5 * cm, 2 * cm, 1.5 * cm, page_h - 2 * cm)
        canvas.restoreState()

    def _body_header(self, canvas, doc):
        page_w, page_h = A4
        canvas.saveState()
        # Header bar
        canvas.setFillColor(PRIMARY)
        canvas.rect(0, page_h - 1.2 * cm, page_w, 1.2 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("NotoSerifSC-Bold", 9)
        canvas.drawString(1.8 * cm, page_h - 0.8 * cm, "Benchmark CODEC-CORTEX v1.0.0")
        canvas.setFont("NotoSerifSC", 9)
        canvas.drawRightString(page_w - 1.8 * cm, page_h - 0.8 * cm, "Informe científico")
        # Footer
        canvas.setFillColor(SLATE)
        canvas.setFont("NotoSerifSC", 8)
        canvas.drawString(1.8 * cm, 0.8 * cm, "Fidel Ernesto Lozada A. · MIT License")
        canvas.drawRightString(page_w - 1.8 * cm, 0.8 * cm, f"Página {doc.page}")
        # Footer line
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(1.8 * cm, 1.2 * cm, page_w - 1.8 * cm, 1.2 * cm)
        canvas.restoreState()


# ---------------------------------------------------------------------------
# Build PDF
# ---------------------------------------------------------------------------

def build_cover() -> List:
    flow = []
    flow.append(Spacer(1, 3 * cm))
    flow.append(Paragraph("Benchmark Científico", STYLES["CoverTag"]))
    flow.append(Spacer(1, 0.5 * cm))
    flow.append(Paragraph("CODEC-CORTEX", STYLES["CoverHero"]))
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("Evaluación de Preservación de Evidencia<br/>bajo Compresión Contextual", STYLES["CoverSub"]))
    flow.append(Spacer(1, 2 * cm))

    # Summary card
    summary_data = [
        [Paragraph("<b>Versión</b>", STYLES["TableCell"]),
         Paragraph("1.0.0", STYLES["TableCell"])],
        [Paragraph("<b>Fecha</b>", STYLES["TableCell"]),
         Paragraph("2026-06-28", STYLES["TableCell"])],
        [Paragraph("<b>CODEC-CORTEX</b>", STYLES["TableCell"]),
         Paragraph("v0.3.0 (CLI 1.1.9, 222 tests)", STYLES["TableCell"])],
        [Paragraph("<b>Corpus</b>", STYLES["TableCell"]),
         Paragraph("L2-multidominio (10 dominios, 50 artefactos)", STYLES["TableCell"])],
        [Paragraph("<b>Métodos</b>", STYLES["TableCell"]),
         Paragraph("11 (4 posicionales + 1 semántico + 1 query-dep + 3 CODEC + 2 ablations)", STYLES["TableCell"])],
        [Paragraph("<b>Escenarios</b>", STYLES["TableCell"]),
         Paragraph("11 (full + 4 reduced-window + 6 adversariales)", STYLES["TableCell"])],
        [Paragraph("<b>Total runs</b>", STYLES["TableCell"]),
         Paragraph("4 840 (determinísticos, reproducibles)", STYLES["TableCell"])],
        [Paragraph("<b>Fase LLM</b>", STYLES["TableCell"]),
         Paragraph("No ejecutada (protocolo §11.2)", STYLES["TableCell"])],
        [Paragraph("<b>Autor</b>", STYLES["TableCell"]),
         Paragraph("Fidel Ernesto Lozada A.", STYLES["TableCell"])],
        [Paragraph("<b>Licencia</b>", STYLES["TableCell"]),
         Paragraph("MIT", STYLES["TableCell"])],
    ]
    t = Table(summary_data, colWidths=[4 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BG_SOFT),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(t)

    flow.append(Spacer(1, 2 * cm))
    flow.append(Paragraph("Informe en formato HCORTEX · Método científico objetivo y transversal", STYLES["CoverMeta"]))
    flow.append(Paragraph("Reproducible: hashes SHA-256 + scripts versionados + manifest", STYLES["CoverMeta"]))
    return flow


def build_toc() -> List:
    flow = []
    flow.append(Paragraph("Tabla de Contenidos", STYLES["H1"]))
    flow.append(Spacer(1, 0.4 * cm))

    toc_entries = [
        ("1. Informe Científico Principal", 1, 1),
        ("   1.0 Resumen ejecutivo", 2, 1),
        ("   1.1 Introducción y contexto", 2, 1),
        ("   1.2 Método científico", 2, 1),
        ("   1.3 Resultados", 2, 1),
        ("   1.4 Análisis comparativo transversal", 2, 1),
        ("   1.5 Diagramas explicativos", 2, 1),
        ("   1.6 Discusión", 2, 1),
        ("   1.7 Reproducibilidad", 2, 1),
        ("   1.8 Conclusiones", 2, 1),
        ("2. Matriz de Claims", 1, 1),
        ("3. Reporte de Regresión", 1, 1),
        ("4. Reporte de Descubrimiento de Métricas", 1, 1),
        ("5. Análisis Comparativo Transversal", 1, 1),
    ]
    for entry, level, _ in toc_entries:
        style = STYLES["TOCEntry1"] if level == 1 else STYLES["TOCEntry2"]
        flow.append(Paragraph(entry, style))

    flow.append(Spacer(1, 0.8 * cm))
    flow.append(Paragraph("Artefactos reproducibles adjuntos", STYLES["H2"]))
    flow.append(Paragraph("• <b>corpus/</b>: 50 artefactos (10 .cortex + 40 alternativas) con hashes SHA-256", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>runs/</b>: scored_tasks.csv (4 840 filas), summary_tasks.csv, scenario_results.json, derived_metrics.json", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>methods/</b>: method_registry.json con 11 métodos", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>metrics/</b>: metric_registry.json con 15 métricas canónicas", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>diagrams/</b>: 10 PNG matplotlib + 7 PUML + 7 SVG", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>scripts/</b>: build_corpus.py, run_benchmark.py, generate_diagrams.py, prerender_hcortex.py", STYLES["Bullet"]))
    flow.append(Paragraph("• <b>manifest.json</b>: versión, entorno, totales", STYLES["Bullet"]))
    return flow


def main():
    out_pdf = "/home/z/my-project/download/benchmark-cortex/Benchmark_CODEC_CORTEX_v1.0.pdf"
    reports_dir = Path("/home/z/my-project/download/benchmark-cortex/reports")
    images_dir = Path("/home/z/my-project/download/benchmark-cortex")  # images referenced as "diagrams/xxx.png"

    doc = BenchmarkDocTemplate(
        out_pdf,
        pagesize=A4,
        title="Benchmark CODEC-CORTEX v1.0.0",
        author="Z.ai · Benchmark Harness",
        subject="Informe científico de evaluación de preservación de evidencia bajo compresión contextual",
        creator="Z.ai · benchmark_harness.py + reportlab",
    )

    flow = []

    # Cover
    flow.extend(build_cover())
    flow.append(NextPageTemplate("Body"))
    flow.append(PageBreak())

    # TOC
    flow.extend(build_toc())
    flow.append(PageBreak())

    # Reports
    reports = [
        ("scientific_report.md", "1. Informe Científico Principal"),
        ("claim_matrix.md", "2. Matriz de Claims"),
        ("regression_report.md", "3. Reporte de Regresión"),
        ("metric_discovery_report.md", "4. Reporte de Descubrimiento de Métricas"),
        ("comparative_analysis.md", "5. Análisis Comparativo Transversal"),
    ]

    for fname, section_title in reports:
        flow.append(Paragraph(section_title, STYLES["H1"]))
        flow.append(Spacer(1, 0.3 * cm))
        md_text = (reports_dir / fname).read_text(encoding="utf-8")
        # Strip HTML comments
        md_text = re.sub(r'<!--[^>]*-->', '', md_text)
        flowables = md_to_flowables(md_text, images_dir)
        flow.extend(flowables)
        flow.append(PageBreak())

    print(f"Building PDF with {len(flow)} flowables...")
    doc.build(flow)
    print(f"PDF written: {out_pdf}")

    # Size
    size_kb = Path(out_pdf).stat().st_size / 1024
    print(f"  Size: {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
