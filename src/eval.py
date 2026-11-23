"""Golden-set evaluation and evidence log generation.

Respect docs/constraints.md (C10).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from . import config, taxonomy
from .export import md_to_pdf

GOLDEN_COLUMNS = ["item_id", "text", "human_primary_theme", "human_return_signal", "human_note"]


def _is_labelled(value: object) -> bool:
    v = str(value or "").strip()
    return v != "" and v.upper() != "TODO"


def load_golden(path: str | Path | None = None) -> pd.DataFrame:
    """Load golden set. If incomplete/missing, generate a 20-row template."""
    config.ensure_dirs()
    gpath = Path(path) if path else config.GOLDEN
    if gpath.exists():
        df = pd.read_csv(gpath)
    else:
        df = pd.DataFrame(columns=GOLDEN_COLUMNS)

    for col in GOLDEN_COLUMNS:
        if col not in df.columns:
            df[col] = ""
    df = df[GOLDEN_COLUMNS].copy()
    df["item_id"] = df["item_id"].astype(str).str.strip()
    df["text"] = df["text"].astype(str).fillna("").str.strip()
    df["human_primary_theme"] = df["human_primary_theme"].fillna("").astype(str).str.strip()
    df["human_return_signal"] = df["human_return_signal"].fillna("").astype(str).str.strip()
    df["human_note"] = df["human_note"].fillna("").astype(str).str.strip()

    labelled = df[df["human_primary_theme"].map(_is_labelled)]
    if len(df) < config.GOLDEN_N or len(labelled) < config.GOLDEN_N:
        template = _generate_template()
        template.to_csv(gpath, index=False)
        print(
            f"Golden template written to {gpath} with {len(template)} rows. "
            "Fill human_primary_theme/human_return_signal/human_note manually. "
            "Do NOT fabricate labels."
        )
        return template
    return df


def _generate_template() -> pd.DataFrame:
    """Create a 20-row labelling template from sample/available corpus."""
    from .ingest import build_sample_corpus, load_corpus

    sample_path = config.DATA_DIR / "public_corpus_sample.csv"
    if not sample_path.exists():
        build_sample_corpus(sample_path, write=True)
    try:
        corpus = load_corpus(sample_path)
    except Exception:
        corpus = build_sample_corpus(sample_path, write=True)

    # Pick diverse rows across sources where possible.
    picks = []
    for _, grp in corpus.groupby("source_class"):
        picks.append(grp.head(4))
    diverse = pd.concat(picks, ignore_index=True).drop_duplicates(subset=["text"])
    if len(diverse) < config.GOLDEN_N:
        diverse = corpus.drop_duplicates(subset=["text"])
    diverse = diverse.head(config.GOLDEN_N).copy()
    template = pd.DataFrame({
        "item_id": diverse.get("item_id", pd.Series([f"G{i:03d}" for i in range(1, len(diverse)+1)])).astype(str),
        "text": diverse.get("text", "").astype(str),
        "human_primary_theme": ["TODO"] * len(diverse),
        "human_return_signal": ["TODO"] * len(diverse),
        "human_note": [""] * len(diverse),
    })
    return template[GOLDEN_COLUMNS]


def evaluate(themed_df: pd.DataFrame, golden_df: pd.DataFrame) -> dict[str, Any]:
    """Evaluate engine labels against human-labelled golden set."""
    gold = golden_df.copy()
    for col in GOLDEN_COLUMNS:
        if col not in gold.columns:
            gold[col] = ""
    gold = gold[GOLDEN_COLUMNS]
    labelled = gold[gold["human_primary_theme"].map(_is_labelled)].copy()
    if len(labelled) < config.GOLDEN_N:
        return {
            "status": "incomplete",
            "n_labelled": int(len(labelled)),
            "n_required": config.GOLDEN_N,
            "agreement_pct": None,
            "return_signal_agreement_pct": None,
            "per_theme": {},
            "confusion_matrix": [],
            "labels": [],
            "disagreements": [],
            "message": "Golden set not fully labelled. Fill TODO labels manually; no scores fabricated.",
        }

    merged = themed_df.merge(labelled, on="item_id", suffixes=("_engine", "_human"), how="inner")
    if merged.empty:
        # Fallback merge on text if ids don't align.
        merged = themed_df.merge(labelled, on="text", suffixes=("_engine", "_human"), how="inner")
    if merged.empty:
        return {
            "status": "error",
            "n_labelled": int(len(labelled)),
            "n_required": config.GOLDEN_N,
            "agreement_pct": None,
            "message": "No overlapping rows between themed corpus and golden set. Check item_id/text alignment.",
            "disagreements": [],
        }

    pred = merged["primary_theme"].astype(str)
    truth = merged["human_primary_theme"].astype(str)
    labels = config.THEME_CODES
    agreement = round(100 * accuracy_score(truth, pred), 1)
    cm = confusion_matrix(truth, pred, labels=labels).tolist()
    report = classification_report(truth, pred, labels=labels, output_dict=True, zero_division=0)

    rs_pred = merged["return_signal"].astype(str) if "return_signal" in merged.columns else pd.Series(["unclear"] * len(merged))
    rs_truth = merged["human_return_signal"].astype(str)
    rs_labelled = rs_truth.map(_is_labelled)
    rs_agreement = round(100 * accuracy_score(rs_truth[rs_labelled], rs_pred[rs_labelled]), 1) if rs_labelled.any() else None

    disagreements = []
    mismatch = merged[pred != truth]
    for _, r in mismatch.iterrows():
        disagreements.append({
            "item_id": r.get("item_id", ""),
            "text": r.get("text", "")[:240],
            "engine_label": r.get("primary_theme", ""),
            "human_label": r.get("human_primary_theme", ""),
            "human_note": r.get("human_note", ""),
        })

    per_theme = {k: v for k, v in report.items() if k in labels}
    return {
        "status": "ok",
        "n_labelled": int(len(labelled)),
        "n_evaluated": int(len(merged)),
        "agreement_pct": agreement,
        "return_signal_agreement_pct": rs_agreement,
        "per_theme": per_theme,
        "confusion_matrix": cm,
        "labels": labels,
        "disagreements": disagreements,
    }


def corrections() -> list[dict[str, str]]:
    """Seed correction placeholders. Replace with real disagreements after labelling."""
    return [
        {
            "item_id": "TODO_1",
            "ai_output": "TODO: engine label/output",
            "human_correction": "TODO: human-corrected label",
            "why_it_was_wrong": "TODO: explain the mismatch from the text.",
            "what_we_changed_in_the_prompt": "TODO: prompt/taxonomy/rule change.",
        },
        {
            "item_id": "TODO_2",
            "ai_output": "TODO: engine label/output",
            "human_correction": "TODO: human-corrected label",
            "why_it_was_wrong": "TODO: explain the mismatch from the text.",
            "what_we_changed_in_the_prompt": "TODO: prompt/taxonomy/rule change.",
        },
    ]


def render_evidence_md(
    results: dict[str, Any],
    eval_result: dict[str, Any],
    correction_items: list[dict[str, str]],
    sources: list[dict[str, Any]] | None = None,
) -> str:
    """Render evidence log markdown with required sections."""
    corpus = results.get("corpus", {})
    agg = results.get("aggregate", {})
    bias = results.get("bias_report", {})
    src_rows = sources or []
    if not src_rows:
        # derive from items
        items = results.get("items", [])
        by_src: dict[str, int] = {}
        for it in items:
            s = str(it.get("source", "unknown"))
            by_src[s] = by_src.get(s, 0) + 1
        src_rows = [{"source": k, "count": v} for k, v in sorted(by_src.items())]

    lines = []
    lines.append("# AI Evidence Log — Urban Company Graduation Project")
    lines.append("")
    lines.append("> Public document. Respect docs/constraints.md. No PII.")
    lines.append("")
    lines.append("## Sources & Volume")
    lines.append("")
    lines.append("| Source | Items |")
    lines.append("|---|---:|")
    for row in src_rows:
        lines.append(f"| {row.get('source','')} | {row.get('count',0)} |")
    lines.append("")
    lines.append(f"- Total items loaded: **{corpus.get('rows_loaded', 0)}**")
    lines.append(f"- Total items kept after cleaning/redaction: **{corpus.get('rows_kept', 0)}**")
    lines.append(f"- PII redactions: **{corpus.get('redactions', 0)}**")
    lines.append(f"- Illustrative sample used: **{corpus.get('illustrative', False)}**")
    lines.append("")

    lines.append("## Theme Taxonomy")
    lines.append("")
    for t in config.THEMES:
        lines.append(f"- **{t['code']} — {t['name']}**: {t['meaning']}")
    lines.append("")

    lines.append("## Golden Set Agreement")
    lines.append("")
    lines.append(f"- Status: **{eval_result.get('status')}**")
    lines.append(f"- Labelled rows: **{eval_result.get('n_labelled', 0)} / {eval_result.get('n_required', config.GOLDEN_N)}**")
    lines.append(f"- Overall agreement: **{eval_result.get('agreement_pct', 'N/A')}%**")
    lines.append(f"- Return-signal agreement: **{eval_result.get('return_signal_agreement_pct', 'N/A')}%**")
    lines.append("")
    if eval_result.get("disagreements"):
        lines.append("### Disagreements")
        lines.append("")
        lines.append("| Item | Engine | Human | Note |")
        lines.append("|---|---|---|---|")
        for d in eval_result["disagreements"][:20]:
            note = str(d.get('human_note','')).replace('|','/')
            lines.append(f"| {d.get('item_id','')} | {d.get('engine_label','')} | {d.get('human_label','')} | {note} |")
        lines.append("")
    if eval_result.get("confusion_matrix"):
        lines.append("### Confusion Matrix (rows=human, cols=engine)")
        lines.append("")
        labels = eval_result.get("labels", [])
        lines.append("| Human \\ Engine | " + " | ".join(labels) + " |")
        lines.append("|---|" + "|".join(["---:"] * len(labels)) + "|")
        for i, row in enumerate(eval_result["confusion_matrix"]):
            lines.append(f"| {labels[i]} | " + " | ".join(str(x) for x in row) + " |")
        lines.append("")

    lines.append("## Corrections (AI output rejected/corrected)")
    lines.append("")
    for c in correction_items:
        lines.append(f"### {c.get('item_id','TODO')}")
        lines.append(f"- **AI output:** {c.get('ai_output','')}")
        lines.append(f"- **Human correction:** {c.get('human_correction','')}")
        lines.append(f"- **Why it was wrong:** {c.get('why_it_was_wrong','')}")
        lines.append(f"- **What changed:** {c.get('what_we_changed_in_the_prompt','')}")
        lines.append("")

    lines.append("## Bias Handling")
    lines.append("")
    lines.append(f"- Source mix: {bias.get('source_mix', {})}")
    lines.append(f"- Complaint-heavy share: {bias.get('complaint_heavy_pct', 0)}% ({bias.get('complaint_heavy_count', 0)} items)")
    lines.append(f"- Silent-nonreturner proxy count: {bias.get('silent_nonreturner_proxy_count', 0)}")
    lines.append(f"- Limitation: {bias.get('limitation', '')}")
    lines.append("")

    lines.append("## Limitations")
    lines.append("")
    lines.append("- Public data over-represents vocal and negative experiences; quiet non-returners are under-observed.")
    lines.append("- Illustrative sample data, if used, is for workflow demonstration only and must be replaced with real public evidence before submission.")
    lines.append("- LLM coding is probabilistic; golden-set review and human corrections are required.")
    lines.append("- This evidence log does not include PII and must not include screenshots, invoices, addresses, phone numbers, or personal documents.")
    return "\n".join(lines)


def export(results: dict[str, Any], eval_result: dict[str, Any], correction_items: list[dict[str, str]] | None = None) -> dict[str, str]:
    """Write evidence log markdown and PDF."""
    config.ensure_dirs()
    corr = correction_items if correction_items is not None else corrections()
    md = render_evidence_md(results, eval_result, corr)
    config.EVIDENCE_MD.write_text(md, encoding="utf-8")
    pdf_path = md_to_pdf(md, config.EVIDENCE_PDF)
    return {"md": str(config.EVIDENCE_MD), "pdf": str(pdf_path)}


if __name__ == "__main__":
    from . import engine

    config.ensure_dirs()
    sample = config.DATA_DIR / "public_corpus_sample.csv"
    if not sample.exists():
        from .ingest import build_sample_corpus

        build_sample_corpus(sample, write=True)
    golden = load_golden()
    results = engine.run(sample, llm=None)
    themed = pd.DataFrame(results["items"])
    ev = evaluate(themed, golden)
    print(json.dumps(ev, indent=2)[:4000])