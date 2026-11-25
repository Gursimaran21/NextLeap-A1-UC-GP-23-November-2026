"""Map the eight Part 1 discovery questions to observable evidence.

Every row reports only what is present in the current coded corpus. When no
direct evidence exists the status says so explicitly; nothing is inferred or
invented. Respect docs/constraints.md (C3, C4, C5).
"""

from __future__ import annotations

from typing import Any

from . import config

_QUESTION_SPECS = [
    {
        "id": "Q1",
        "question": "What do customers expect once a booking is complete?",
        "themes": ["T1_POST_SERVICE_CLOSURE", "T3_MENTAL_AVAILABILITY"],
        "note": "Coded continuity themes only; explicit expectation statements require interviews.",
    },
    {
        "id": "Q2",
        "question": "How do they decide a home service is needed, and when?",
        "themes": ["T2_NEED_RECOGNITION", "T7_PLANNING_SEASONALITY"],
        "note": "Keyword/rule proxy for timing; no timing study in public reviews.",
    },
    {
        "id": "Q3",
        "question": "Who or what do they use when the same or a different need arises?",
        "themes": ["T5_LOCAL_WHATSAPP_DEFAULT", "T4_CATEGORY_AWARENESS", "T3_MENTAL_AVAILABILITY"],
        "note": "Alternatives are visible only when customers explicitly mention them.",
    },
    {
        "id": "Q4",
        "question": "Why did they or did they not book again, in their own words?",
        "themes": [],
        "return_signals": ["returned", "did_not_return"],
        "note": "Requires explicit return-signal text; silent non-returners are not observable here.",
    },
    {
        "id": "Q5",
        "question": "What do they do outside the app: local providers, neighbours, family, WhatsApp?",
        "themes": ["T5_LOCAL_WHATSAPP_DEFAULT"],
        "note": "Local/WhatsApp proxy only; interviews needed for depth.",
    },
    {
        "id": "Q6",
        "question": "What separates returners from non-returners in their own accounts?",
        "themes": [],
        "return_signals": ["returned", "did_not_return"],
        "note": "Public return signals are sparse; not a validated returner/non-returner comparison.",
    },
    {
        "id": "Q7",
        "question": "How do patterns differ by category, city, household type, and discovery channel?",
        "themes": [],
        "segmentation": True,
        "note": "Stratification is computed only where a field is populated in the corpus.",
    },
    {
        "id": "Q8",
        "question": "What unmet needs emerge consistently across conversations?",
        "themes": [],
        "top_themes": True,
        "note": "Theme shares from the current single-source corpus; not cross-source validation.",
    },
]


def _quotes(items: list[dict[str, Any]], limit: int = 2) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in items:
        q = str(item.get("exact_quote", "") or "").strip()
        if q:
            out.append({
                "quote": q,
                "item_id": str(item.get("item_id", "")),
                "source": str(item.get("source", "")),
                "theme": str(item.get("primary_theme", "")),
            })
        if len(out) >= limit:
            break
    return out


def _segmentation_coverage(agg: dict[str, Any]) -> dict[str, float]:
    seg = agg.get("segmentation_coverage", {})
    if not isinstance(seg, dict):
        return {}
    return {
        str(k): float(v.get("coverage_pct", 0) or 0)
        for k, v in seg.items()
        if isinstance(v, dict)
    }


def build_question_report(results: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one evidence row per Part 1 discovery question."""
    items = [i for i in results.get("items", []) if isinstance(i, dict)]
    agg = results.get("aggregate", {}) or {}
    total = max(1, len(items))
    rows: list[dict[str, Any]] = []

    for spec in _QUESTION_SPECS:
        themes = set(str(x) for x in spec.get("themes", []))
        signals = set(str(x) for x in spec.get("return_signals", []))
        matching = [
            i for i in items
            if (themes and str(i.get("primary_theme", "")) in themes)
            or (signals and str(i.get("return_signal", "")) in signals)
        ]

        detail = ""
        if spec.get("segmentation"):
            cov = _segmentation_coverage(agg)
            detail = ", ".join(f"{k}={v}%" for k, v in sorted(cov.items()))
            matching = [i for i in items if cov and any(
                str(i.get(field, "") or "").strip() for field in ("city", "category", "household_type", "first_found_uc")
            )]
        elif spec.get("top_themes"):
            top = [t for t in agg.get("theme_distribution", []) if str(t.get("code")) != "T11_UNCLASSIFIED"][:3]
            detail = ", ".join(f"{t['code']}={t['share_pct']}%" for t in top)
            codes = {str(t.get("code")) for t in top}
            matching = [i for i in items if str(i.get("primary_theme", "")) in codes]
        elif signals:
            counts = agg.get("return_signal_crosstab", [])
            detail = "; ".join(
                f"{r.get('return_signal')}: {r.get('count')}"
                for r in counts if str(r.get("return_signal", "")) in signals
            ) or "no return-signal rows"

        status = "Evidence found" if matching else "No direct evidence in current corpus"
        rows.append({
            "id": spec["id"],
            "question": spec["question"],
            "matching_items": len(matching),
            "share_pct": round(100 * len(matching) / total, 1),
            "status": status,
            "detail": detail,
            "note": spec["note"],
            "example_quotes": _quotes(matching),
        })
    return rows


def question_report_dataframe(results: dict[str, Any]):
    """Compact DataFrame for the Streamlit page."""
    import pandas as pd

    rows = build_question_report(results)
    return pd.DataFrame([
        {
            "ID": r["id"],
            "Discovery question": r["question"],
            "Items": r["matching_items"],
            "Share %": r["share_pct"],
            "Status": r["status"],
            "Detail": r["detail"],
        }
        for r in rows
    ])
