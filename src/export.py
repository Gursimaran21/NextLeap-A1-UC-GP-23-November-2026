"""Export helpers for markdown/PDF artifacts.

Respect docs/constraints.md.
"""

from __future__ import annotations

from pathlib import Path


def _build_md_story(md_text: str):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, Preformatted, Spacer

    def escape(text: str) -> str:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    styles = getSampleStyleSheet()
    if "BodySmall" not in styles:
        styles.add(ParagraphStyle(name="BodySmall", parent=styles["Normal"], fontSize=10, leading=13))
    if "MdH1" not in styles:
        styles.add(ParagraphStyle(name="MdH1", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#12212B")))
    if "MdH2" not in styles:
        styles.add(ParagraphStyle(name="MdH2", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#0B6E4F")))
    if "MdH3" not in styles:
        styles.add(ParagraphStyle(name="MdH3", parent=styles["Heading3"], fontSize=11, leading=14, textColor=colors.HexColor("#12212B")))

    story = []
    for raw_line in md_text.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            story.append(Spacer(1, 4 * mm))
            continue
        if line.startswith("# "):
            story.append(Paragraph(escape(line[2:].strip()), styles["MdH1"]))
        elif line.startswith("## "):
            story.append(Paragraph(escape(line[3:].strip()), styles["MdH2"]))
        elif line.startswith("### "):
            story.append(Paragraph(escape(line[4:].strip()), styles["MdH3"]))
        elif line.startswith("|"):
            story.append(Preformatted(line, styles["BodySmall"]))
        elif line.startswith("- "):
            story.append(Paragraph("• " + escape(line[2:].strip()), styles["BodySmall"]))
        else:
            story.append(Paragraph(escape(line), styles["BodySmall"]))
    if not story:
        story.append(Paragraph("Empty document", styles["Normal"]))
    return story


def md_to_pdf_bytes(md_text: str) -> bytes:
    """Render markdown-like text to PDF bytes (ephemeral-disk friendly)."""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "reportlab is required for PDF export. Install requirements.txt or use MD export."
        ) from e

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )
    doc.build(_build_md_story(md_text))
    return buf.getvalue()


def md_to_pdf(md_text: str, out_path: str | Path) -> Path:
    """Write a simple PDF from markdown-like text.

    This is a lightweight renderer for evidence logs; deck PDF uses src/deck.py.
    """
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(md_to_pdf_bytes(md_text))
    return out