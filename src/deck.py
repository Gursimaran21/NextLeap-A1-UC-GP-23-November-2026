"""Deck content and PDF export. Respect docs/constraints.md (C1, C8, C10)."""

from __future__ import annotations

from pathlib import Path

from . import config

SLIDES: list[dict] = [
    {
        "n": 1,
        "title": "One in three repeat bookings is decided in the 90 days after the first service, not during it",
        "key_message": "Repeat continuity is a post-service decision window; the MVP targets that window without incentives or transactions.",
        "bullets": [
            "Urban Company · Consumer Growth · Nov 2026",
            "Business metric: share of eligible customers who complete another booking within 90 days of a completed anchor booking.",
            "Anchor: first completed core-category booking in anchor month; excludes InstaHelp, redos, warranty, refunds.",
            "About 84% of net transaction value comes from repeat customers (given context).",
        ],
        "visual": "title_metric",
        "footnote_links": ["docs/constraints.md", "outputs/discovery_results.json"],
        "source_refs": ["Brief metric definition"],
    },
    {
        "n": 2,
        "title": "The 90-day repeat rate is six customer decisions, only four of which the product can influence",
        "key_message": "Decompose the metric into D1–D6; focus on influencable customer-side decisions.",
        "bullets": [
            "D1 Need incidence (limited influence) · D2 Need recognition · D3 Mental availability · D4 Category consideration · D5 Choice vs alternatives · D6 Frictionless completion.",
            "Measurement uses customer self-report or public data only; no internal UC data.",
            "Focus: D2–D5 where planning, awareness, and decision confidence can help.",
        ],
        "visual": "decomposition_flow",
        "footnote_links": ["views/4_Metric_Decomposition.py"],
        "source_refs": ["config.DECOMPOSITION"],
    },
    {
        "n": 3,
        "title": "Our discovery engine codes public conversations into 11 opportunity themes and corrects for two known biases",
        "key_message": "A transparent AI discovery engine turns public feedback into coded themes with human validation and bias handling.",
        "bullets": [
            "1) Ingest public sources (CSV/paste) with source URL/class/date; block logged-in UC/app paths.",
            "2) Redact PII and dedupe; keep provenance.",
            "3) Code with fixed T1–T11 taxonomy (LLM when available, deterministic fallback otherwise).",
            "4) Aggregate theme shares, continuity vs experience split, bias report, opportunity ranking.",
            "5) Validate with 20-item golden set, human corrections, and evidence log.",
            "Inputs: public reviews/posts/transcripts. Outputs: coded items, theme table, bias report, evidence log.",
        ],
        "visual": "engine_flow",
        "footnote_links": ["outputs/evidence_log.md", "outputs/discovery_results.json"],
        "source_refs": ["src/engine.py", "src/eval.py"],
    },
    {
        "n": 4,
        "title": "Real app-store reviews are dominated by experience complaints; continuity signals are rare in public traces",
        "key_message": "The known public-data bias is confirmed on real reviews: silent non-returners leave little trace, so primary research must carry the continuity hypothesis.",
        "bullets": [
            "Corpus: 465 real App Store (India) reviews collected 2026-11-23 with full provenance (public RSS; no logged-in UC access).",
            "Deterministic offline coding: continuity themes T1-T7 about 1%, experience/price/redo controls about 25%, short praise or unclassified about 74%.",
            "Implication: public traces under-represent planning/continuity gaps; interviews and golden-set validation are required, not optional.",
            "T9 price/offer excluded from solutioning (C1); T10 redo/refund excluded from metric counting (C5).",
        ],
        "visual": "theme_bar",
        "footnote_links": ["outputs/discovery_results.json", "outputs/evidence_log.md"],
        "source_refs": ["Public corpus (App Store India, real)"],
    },
    {
        "n": 5,
        "title": "Six planned interviews, split between returners and non-returners, will test the continuity hypothesis in customers' own words",
        "key_message": "Primary research is designed to validate continuity gaps while surfacing genuine no-need and trust nuances.",
        "bullets": [
            "Anonymized R01-R06 interviews; no PII/screenshots/invoices/documents.",
            "Protocol targets: post-service closure, local/WhatsApp defaults, decision confidence, genuine no-need.",
            "Status: pending - placeholders in data/interviews.csv until real interviews are recorded; synthesis will compare against engine findings.",
        ],
        "visual": "interview_quotes",
        "footnote_links": ["data/interviews.csv", "views/5_User_Research.py"],
        "source_refs": ["Primary interviews (placeholder until filled)"],
    },
    {
        "n": 6,
        "title": "We chose metro households who used one core category once and then went quiet",
        "key_message": "The target segment is narrow, observable through self-report, and aligned with the 90-day repeat metric.",
        "bullets": [
            "Segment: urban renters/families in metros, one core-category booking, no second booking within 90 days.",
            "Core categories: Deep Cleaning, AC Service, Plumbing, Salon (focus); excludes InstaHelp.",
            "Behavioral wedge: planning/recognition/decision confidence, not service-quality-only and not C1 incentives.",
        ],
        "visual": "segment_card",
        "footnote_links": ["views/6_Problem_Definition.py"],
        "source_refs": ["config.SEGMENT_NAME"],
    },
    {
        "n": 7,
        "title": "The root cause is a missing handoff from 'job done' to 'what's next for my home'",
        "key_message": "Customers lack a calm post-service continuity system, so genuine next needs drift to memory, local defaults, or inaction.",
        "bullets": [
            "Root cause hypothesis: closure + planning + decision-confidence gaps.",
            "Workarounds: ad hoc memory, neighbours/family, WhatsApp/local vendors, DIY, ignore until urgent.",
            "Not solving: C1 price/compensation changes, booking/account actions, or service-quality-only framing.",
        ],
        "visual": "problem_statement",
        "footnote_links": ["views/6_Problem_Definition.py"],
        "source_refs": ["Discovery + interviews"],
    },
    {
        "n": 8,
        "title": "A Home Care Companion builds the next need before it becomes urgent, and honestly says when not to book",
        "key_message": "The MVP is a customer-side planning and routing companion: calendar, need decider, reflection - no transactions.",
        "bullets": [
            "Step 1 profile (no PII) → Step 2 90-day calendar (public basis + source).",
            "Step 3 Need Decider routes to DIY/local/UC category info/wait/immediate help with reason + clarifying questions.",
            "Step 4 post-service reflection creates private downloadable checklist; 2-question feedback.",
            "Guardrail: 'Nothing here books anything.' No booking/messaging/account actions.",
        ],
        "visual": "mvp_flow",
        "footnote_links": ["views/1_MVP.py"],
        "source_refs": ["src/mvp.py"],
    },
    {
        "n": 9,
        "title": "Three return-user tests are planned; observations and iteration changes will be recorded before submission",
        "key_message": "Lightweight testing will validate task completion and surface trust/clarity improvements before scaling.",
        "bullets": [
            "3 return-user tasks: plan calendar, route vague/clear needs, reflect/download checklist.",
            "Expected tool traces logged in outputs/tool_trace.jsonl for audit.",
            "Success metrics panel: 90-day repeat rate (business), calendar engagement, decider resolution, checklist download (leading), false-urgency/no-need respect (guardrails).",
            "Status: pending - observations and next-iteration changes to be filled in views/7_MVP_Testing.py after real tests.",
        ],
        "visual": "testing_metrics",
        "footnote_links": ["views/7_MVP_Testing.py", "views/8_Success_Metrics.py", "outputs/tool_trace.jsonl"],
        "source_refs": ["MVP testing plan"],
    },
    {
        "n": 10,
        "title": "Success is a higher 90-day repeat rate with no increase in unnecessary bookings",
        "key_message": "Scale only if continuity improves while trust and no-need guardrails hold.",
        "bullets": [
            "Primary: eligible 90-day repeat completion rate, excluding InstaHelp/redo/warranty/refund.",
            "Guardrails: non-UC route rate, no-need rate, 2-week 'did I actually need it?' follow-up; no false urgency.",
            "Risks panel: false need creation, unsafe routing, PII leakage, public-data bias, low adoption, metric gaming - each with mitigation and early warning.",
            "Decision rule: iterate if leading indicators improve and guardrails hold; pause if trust/safety guardrails regress.",
        ],
        "visual": "risks_guardrails",
        "footnote_links": ["views/8_Success_Metrics.py", "views/9_Risks.py"],
        "source_refs": ["config.METRIC_DEFINITION"],
    },
]


def _all_deck_text() -> str:
    parts = []
    for s in SLIDES:
        parts.append(str(s.get("title", "")))
        parts.append(str(s.get("key_message", "")))
        for b in s.get("bullets", []):
            parts.append(str(b))
        for f in s.get("footnote_links", []):
            parts.append(str(f))
        for r in s.get("source_refs", []):
            parts.append(str(r))
    return "\n".join(parts)


def build_pdf(out_path: str | Path | None = None) -> Path:
    """Build 10-slide A4 landscape PDF. Enforces C8 QA checks."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, KeepTogether
    except Exception as e:  # pragma: no cover
        raise RuntimeError("reportlab is required for deck PDF export") from e

    out = Path(out_path) if out_path else config.DECK_PDF
    out.parent.mkdir(parents=True, exist_ok=True)

    # QA: filename
    assert out.name == config.DECK_PDF_NAME, f"Deck filename must be {config.DECK_PDF_NAME}"

    # QA: fellow name absent (do not print it)
    fellow = str(getattr(config, "FELLOW_NAME_TO_EXCLUDE", "") or "").strip()
    if fellow:
        assert fellow.lower() not in _all_deck_text().lower(), "Fellow name must not appear in deck text"

    # QA: 10 slides
    assert len(SLIDES) <= config.DECK_MAX_SLIDES, "Deck exceeds 10 slides"

    styles = getSampleStyleSheet()
    ink = colors.HexColor(config.PALETTE["ink"])
    teal = colors.HexColor(config.PALETTE["teal"])
    grey = colors.HexColor(config.PALETTE["grey"])
    light = colors.HexColor(config.PALETTE["light"])

    title_style = ParagraphStyle("DeckTitle", parent=styles["Heading1"], fontSize=22, leading=26, textColor=ink, spaceAfter=8)
    body_style = ParagraphStyle("DeckBody", parent=styles["Normal"], fontSize=14, leading=18, textColor=ink, spaceAfter=6)
    small_style = ParagraphStyle("DeckSmall", parent=styles["Normal"], fontSize=14, leading=17, textColor=grey, spaceAfter=4)
    foot_style = ParagraphStyle("DeckFoot", parent=styles["Normal"], fontSize=14, leading=16, textColor=grey)

    page_counter = {"n": 0}

    def draw_footer(canvas, doc):
        page_counter["n"] += 1
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(grey)
        canvas.drawRightString(landscape(A4)[0] - 14 * mm, 10 * mm, f"Page {page_counter['n']} / {len(SLIDES)}")
        canvas.drawString(14 * mm, 10 * mm, "Public prototype · No bookings · No account access")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(out), pagesize=landscape(A4),
        leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=16 * mm,
    )

    def esc(t: str) -> str:
        return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    story = []
    for i, s in enumerate(SLIDES):
        story.append(Paragraph(esc(s["title"]), title_style))
        story.append(Paragraph(f"<font color='{config.PALETTE['teal']}'><b>Key message:</b></font> {esc(s['key_message'])}", body_style))
        story.append(Spacer(1, 2 * mm))
        for b in s.get("bullets", []):
            story.append(Paragraph(f"• {esc(b)}", body_style))
        story.append(Spacer(1, 2 * mm))
        refs = " | ".join(s.get("footnote_links", []) + s.get("source_refs", []))
        if refs:
            story.append(Paragraph(f"<i>Sources: {esc(refs)}</i>", foot_style))
        if i < len(SLIDES) - 1:
            story.append(PageBreak())

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)

    # QA: page count and size
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(str(out)).pages)
    except Exception:
        pages = page_counter["n"]
    size_mb = out.stat().st_size / (1024 * 1024)
    assert pages <= config.DECK_MAX_SLIDES, f"Deck has {pages} pages; max is {config.DECK_MAX_SLIDES}"
    assert size_mb < config.MAX_PDF_MB, f"Deck is {size_mb:.2f}MB; max is {config.MAX_PDF_MB}MB"
    return out


if __name__ == "__main__":
    p = build_pdf()
    try:
        from pypdf import PdfReader
        pages = len(PdfReader(str(p)).pages)
    except Exception:
        pages = "unknown"
    size_mb = p.stat().st_size / (1024 * 1024)
    print(f"Built {p} | pages={pages} | size={size_mb:.2f}MB")
