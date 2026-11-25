"""Discovery engine: code corpus items, aggregate, and report biases.

Respect docs/constraints.md.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from . import config, taxonomy

SCHEMA_KEYS = {
    "primary_theme",
    "secondary_theme",
    "return_signal",
    "sentiment",
    "bias_flag",
    "confidence",
    "rationale",
    "quote_worthy",
    "exact_quote",
}
SENTIMENTS = {"positive", "neutral", "negative", "mixed"}


def _clean_quote(text: str, max_len: int = 140) -> str:
    q = " ".join(str(text or "").split()).strip()
    return q[:max_len].strip()


def _heuristic_sentiment(text: str) -> str:
    t = text.lower()
    pos = any(w in t for w in ["good", "great", "smooth", "trusted", "fine", "decent", "excellent"])
    neg = any(w in t for w in ["bad", "poor", "late", "rude", "mess", "avoid", "issue", "refund", "warranty"])
    if pos and neg:
        return "mixed"
    if neg:
        return "negative"
    if pos:
        return "positive"
    return "neutral"


def _heuristic_return_signal(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["booked again", "came back", "returned", "used again", "repeat"]):
        return "returned"
    if any(w in t for w in [
        "never booked", "didn't book", "did not book", "went back to local", "moved to local",
        "forgot", "stopped using", "never came back", "didn't come back", "did not come back",
        "avoid the app", "didn't return", "did not return",
    ]):
        return "did_not_return"
    return "unclear"


def _heuristic_bias_flag(text: str, source_class: str) -> str:
    t = text.lower()
    if source_class in taxonomy.COMPLAINT_HEAVY_SOURCES and _heuristic_sentiment(t) == "negative":
        return "bad_experience_overrepresented"
    if any(w in t for w in [
        "forgot", "never thought", "went back to local", "moved to local", "didn't think of",
        "didn't remember", "never came back", "didn't come back", "stopped using", "quietly stopped",
    ]):
        return "silent_nonreturner_proxy"
    return "none"


def deterministic_code(text: str, source_class: str = "other") -> dict[str, Any]:
    t = str(text or "").lower()
    scores: dict[str, int] = {str(theme["code"]): 0 for theme in config.THEMES}

    def add(code: str, pts: int = 1) -> None:
        scores[code] = scores.get(code, 0) + pts

    # Keyword hits from config
    for theme in config.THEMES:
        code = str(theme["code"])
        for k in [str(x).lower() for x in theme.get("keywords", [])]:
            if k and k in t:
                add(code, 1)

    # Regex/phrase rules (fallback quality matters when no LLM key is set).
    if any(p in t for p in ["what to book next", "no follow-up", "no follow up", "no reason to open the app again", "nothing else to book", "after service i had no idea"]):
        add("T1_POST_SERVICE_CLOSURE", 3)
    if any(p in t for p in ["didn't know when", "did not know when", "right frequency", "when to service", "before they break down", "didn't realize", "missed"]):
        add("T2_NEED_RECOGNITION", 3)
    if any(p in t for p in ["forgot the app", "forgot about urban company", "forgot about them", "didn't remember", "did not remember", "not top of mind", "remembered later"]):
        add("T3_MENTAL_AVAILABILITY", 3)
    if any(p in t for p in ["didn't know they also do", "did not know they do", "didn't know uc", "didn't know urban company had", "not aware", "until i watched"]):
        add("T4_CATEGORY_AWARENESS", 3)
    if any(p in t for p in ["local plumber", "local help", "local handyman", "local electrician", "society group", "whatsapp", "neighbor", "neighbour", "family recommended", "building handyman"]):
        add("T5_LOCAL_WHATSAPP_DEFAULT", 3)
    if any(p in t for p in ["not sure if i should call a professional", "diy", "do it myself", "unsure what service", "not sure what service"]):
        add("T6_DECISION_CONFIDENCE", 3)
    if any(p in t for p in ["before summer", "before monsoon", "every year", "seasonal", "diwali", "planned upkeep", "regular maintenance"]):
        add("T7_PLANNING_SEASONALITY", 2)
    if any(p in t for p in ["bad service", "poor quality", "late and left a mess", "rude", "damaged", "unprofessional", "rescheduling made me avoid"]):
        add("T8_EXPERIENCE_QUALITY", 3)
    if any(p in t for p in ["discount", "coupon", "cashback", "membership", "too expensive", "price"]):
        add("T9_PRICE_OFFER", 3)
    if any(p in t for p in ["refund", "refunded", "warranty issue", "redo", "came back to fix"]):
        add("T10_REDO_REFUND", 3)

    # Disambiguation: quality issue should beat closure when complaint is explicit.
    if scores["T8_EXPERIENCE_QUALITY"] >= 3 and scores["T1_POST_SERVICE_CLOSURE"] <= 2:
        scores["T1_POST_SERVICE_CLOSURE"] = max(0, scores["T1_POST_SERVICE_CLOSURE"] - 1)

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    primary = ranked[0][0] if ranked and ranked[0][1] > 0 else "T11_UNCLASSIFIED"
    secondary = ranked[1][0] if len(ranked) > 1 and ranked[1][1] > 0 and ranked[1][0] != primary else ""
    conf = 0.35 if primary == "T11_UNCLASSIFIED" else min(0.92, 0.45 + 0.08 * ranked[0][1])

    quote_worthy = len(t.strip()) >= 30
    return {
        "primary_theme": primary,
        "secondary_theme": secondary,
        "return_signal": _heuristic_return_signal(t),
        "sentiment": _heuristic_sentiment(t),
        "bias_flag": _heuristic_bias_flag(t, source_class),
        "confidence": round(conf, 2),
        "rationale": f"Deterministic rule-based coding assigned {primary} based on visible text cues.",
        "quote_worthy": quote_worthy,
        "exact_quote": _clean_quote(text) if quote_worthy else "",
    }


def _validate_item(item: dict[str, Any], text: str, source_class: str) -> dict[str, Any]:
    base = deterministic_code(text, source_class)
    if not isinstance(item, dict):
        return base
    out = dict(base)
    for k in SCHEMA_KEYS:
        if k in item:
            out[k] = item[k]
    if out.get("primary_theme") not in taxonomy.VALID_THEME_CODES:
        out["primary_theme"] = base["primary_theme"]
    if out.get("secondary_theme") not in taxonomy.VALID_THEME_CODES and out.get("secondary_theme") != "":
        out["secondary_theme"] = ""
    if out.get("return_signal") not in config.RETURN_SIGNALS:
        out["return_signal"] = base["return_signal"]
    if out.get("sentiment") not in SENTIMENTS:
        out["sentiment"] = base["sentiment"]
    if out.get("bias_flag") not in config.BIAS_FLAGS:
        out["bias_flag"] = base["bias_flag"]
    try:
        out["confidence"] = float(out.get("confidence", base["confidence"]))
    except Exception:
        out["confidence"] = base["confidence"]
    out["confidence"] = max(0.0, min(1.0, out["confidence"]))
    out["rationale"] = str(out.get("rationale", base["rationale"])).strip() or base["rationale"]
    out["quote_worthy"] = bool(out.get("quote_worthy", False))
    out["exact_quote"] = _clean_quote(out.get("exact_quote", "")) if out["quote_worthy"] else ""
    return out


def code_item(text: str, llm: Any = None, source_class: str = "other") -> dict[str, Any]:
    """Code a single text item into the fixed schema."""
    system = (
        "You are a rigorous qualitative coding assistant. "
        "Use only the provided theme codes. Do not invent themes. "
        "Ground every label in the text. Respect docs/constraints.md."
    )
    prompt = f"""
Code the following public feedback item.

THEME DEFINITIONS:
{taxonomy.theme_prompt_block()}

RETURN SIGNALS: returned, did_not_return, unclear.
BIAS FLAGS: bad_experience_overrepresented, silent_nonreturner_proxy, none.
SENTIMENT: positive, neutral, negative, mixed.

Return JSON with keys:
primary_theme, secondary_theme, return_signal, sentiment, bias_flag, confidence, rationale, quote_worthy, exact_quote.

Rules:
- primary_theme must be one of the fixed theme codes.
- secondary_theme must be a fixed theme code or "".
- rationale must be one sentence grounded in the text.
- exact_quote must be verbatim, <=140 chars, and only when quote_worthy is true; else "".
- confidence is 0 to 1.

ITEM:
{text}
""".strip()
    raw = llm.generate_json(system, prompt, temperature=0.0) if llm and hasattr(llm, "generate_json") else None
    return _validate_item(raw or {}, text, source_class)


def code_corpus(df: pd.DataFrame, llm: Any = None, progress: Any = None) -> pd.DataFrame:
    """Code all rows in a corpus DataFrame."""
    if df is None or df.empty:
        return pd.DataFrame()
    out = df.copy()
    records = []
    total = len(out)
    for i, row in enumerate(out.to_dict(orient="records"), start=1):
        text = str(row.get("text", ""))
        source_class = str(row.get("source_class", "other"))
        coded = code_item(text, llm=llm, source_class=source_class)
        records.append(coded)
        if progress:
            try:
                progress(i, total)
            except Exception:
                pass
    coded_df = pd.DataFrame(records)
    for col in SCHEMA_KEYS:
        if col not in coded_df.columns:
            coded_df[col] = ""
    return pd.concat([out.reset_index(drop=True), coded_df.reset_index(drop=True)], axis=1)


def _segmentation(df: pd.DataFrame, col: str, total: int) -> dict[str, Any]:
    """Stratify by an optional field; report zero coverage instead of hiding it."""
    if col not in df.columns:
        return {"coverage_pct": 0.0, "rows": [], "note": f"{col} not present in corpus schema"}
    values = df[col].fillna("").astype(str).str.strip()
    populated = df[values != ""]
    if populated.empty:
        return {"coverage_pct": 0.0, "rows": [], "note": f"{col} not captured in current corpus"}
    rows = (
        populated.groupby([col, "primary_theme"]).size().reset_index(name="count")
        .sort_values([col, "count"], ascending=[True, False])
        .rename(columns={col: "value"})
        .to_dict(orient="records")
    )
    return {
        "coverage_pct": round(100 * len(populated) / max(1, total), 1),
        "rows": rows,
        "note": f"{len(populated)} rows carry {col}",
    }


def aggregate(df: pd.DataFrame) -> dict[str, Any]:
    """Aggregate coded corpus into discovery metrics."""
    if df is None or df.empty:
        return {"total_items": 0}

    total = len(df)
    theme_counts = df["primary_theme"].value_counts().to_dict()
    theme_rows = []
    for t in config.THEMES:
        code = str(t["code"])
        count = int(theme_counts.get(code, 0))
        theme_rows.append({
            "code": code,
            "name": t["name"],
            "count": count,
            "share_pct": round(100 * count / total, 1) if total else 0.0,
        })

    by_source = (
        df.groupby(["source_class", "primary_theme"]).size().reset_index(name="count")
        .sort_values(["source_class", "count"], ascending=[True, False])
        .to_dict(orient="records")
    )
    by_category = (
        df.groupby(["category", "primary_theme"]).size().reset_index(name="count")
        .sort_values(["category", "count"], ascending=[True, False])
        .to_dict(orient="records")
        if "category" in df.columns else []
    )
    return_signal_ct = (
        df.groupby(["primary_theme", "return_signal"]).size().reset_index(name="count").to_dict(orient="records")
    )
    bias_counts = df["bias_flag"].value_counts().to_dict() if "bias_flag" in df.columns else {}
    seg = {
        "city": _segmentation(df, "city", total),
        "category": _segmentation(df, "category", total),
        "household_type": _segmentation(df, "household_type", total),
        "first_found_uc": _segmentation(df, "first_found_uc", total),
    }

    quotes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for _, r in df.iterrows():
        code = str(r.get("primary_theme", ""))
        quote = str(r.get("exact_quote", "")).strip()
        if quote and len(quotes[code]) < 3:
            quotes[code].append({
                "item_id": r.get("item_id", ""),
                "quote": quote,
                "return_signal": r.get("return_signal", "unclear"),
                "source": r.get("source", ""),
            })

    continuity = int(df["primary_theme"].isin(taxonomy.CONTINUITY_THEMES).sum())
    experience = int(df["primary_theme"].isin(taxonomy.EXPERIENCE_CONTROL_THEMES).sum())
    other = total - continuity - experience

    return {
        "total_items": total,
        "theme_distribution": theme_rows,
        "by_source_class": by_source,
        "by_category": by_category,
        "segmentation_coverage": {k: v["coverage_pct"] for k, v in seg.items()},
        "segmentation": seg,
        "return_signal_crosstab": return_signal_ct,
        "bias_counts": bias_counts,
        "top_quotes_by_theme": quotes,
        "continuity_vs_experience": {
            "continuity_count": continuity,
            "continuity_pct": round(100 * continuity / total, 1) if total else 0.0,
            "experience_control_count": experience,
            "experience_control_pct": round(100 * experience / total, 1) if total else 0.0,
            "other_count": other,
            "other_pct": round(100 * other / total, 1) if total else 0.0,
        },
    }


def bias_report(df: pd.DataFrame) -> dict[str, Any]:
    """Report sampling/interpretation bias signals."""
    if df is None or df.empty:
        return {"total_items": 0}
    total = len(df)
    source_mix = df["source_class"].value_counts().to_dict() if "source_class" in df.columns else {}
    complaint_heavy = df["source_class"].isin(taxonomy.COMPLAINT_HEAVY_SOURCES).sum() if "source_class" in df.columns else 0
    silent_proxy = (df["bias_flag"] == "silent_nonreturner_proxy").sum() if "bias_flag" in df.columns else 0
    return {
        "total_items": total,
        "source_mix": source_mix,
        "complaint_heavy_count": int(complaint_heavy),
        "complaint_heavy_pct": round(100 * complaint_heavy / total, 1) if total else 0.0,
        "silent_nonreturner_proxy_count": int(silent_proxy),
        "limitation": (
            "Public posts over-represent vocal/negative experiences, and customers who quietly never "
            "return leave little or no public trace. Interview evidence is required to correct this blind spot."
        ),
    }


def run(corpus_path: str | Path | None = None, llm: Any = None, out_path: str | Path | None = None) -> dict[str, Any]:
    """Run discovery engine on corpus; write to out_path (canonical by default)."""
    config.ensure_dirs()
    from .ingest import load_corpus  # local import to avoid cycles

    df = load_corpus(corpus_path)
    coded = code_corpus(df, llm=llm)
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "corpus": {
            "rows_loaded": df.attrs.get("rows_loaded", len(df)),
            "rows_kept": len(df),
            "redactions": df.attrs.get("redactions", 0),
            "sources_count": df.attrs.get("sources_count", 0),
            "min_date": df.attrs.get("min_date"),
            "max_date": df.attrs.get("max_date"),
            "illustrative": bool(df["is_illustrative"].any()) if "is_illustrative" in df.columns else False,
        },
        "aggregate": aggregate(coded),
        "bias_report": bias_report(coded),
        "items": coded.to_dict(orient="records"),
    }
    out = Path(out_path) if out_path else config.DISCOVERY_JSON
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


if __name__ == "__main__":
    config.ensure_dirs()
    sample = config.DATA_DIR / "public_corpus_sample.csv"
    if config.CORPUS.exists():
        corpus_path = config.CORPUS
        out_path = config.DISCOVERY_JSON
    else:
        if not sample.exists():
            from .ingest import build_sample_corpus

            build_sample_corpus(sample, write=True)
        corpus_path = sample
        # Demo runs must never overwrite canonical real-corpus evidence.
        out_path = config.OUTPUTS_DIR / "discovery_results_sample.json"
        print("Real corpus unavailable; using illustrative sample in a separate output file.")
    res = run(corpus_path, llm=None, out_path=out_path)
    rows = res["aggregate"]["theme_distribution"]
    print("Theme distribution:")
    for r in sorted(rows, key=lambda x: x["count"], reverse=True):
        if r["count"] > 0:
            print(f"{r['code']}: {r['count']} ({r['share_pct']}%)")