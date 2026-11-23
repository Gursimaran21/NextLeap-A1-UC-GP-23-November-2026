"""Metric decomposition and opportunity scoring.

Respect docs/constraints.md (C1, C4, C5).
"""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from . import config

# Map opportunity themes to decomposition stages.
THEME_TO_STAGE = {
    "T1_POST_SERVICE_CLOSURE": "D3",
    "T2_NEED_RECOGNITION": "D2",
    "T3_MENTAL_AVAILABILITY": "D3",
    "T4_CATEGORY_AWARENESS": "D4",
    "T5_LOCAL_WHATSAPP_DEFAULT": "D5",
    "T6_DECISION_CONFIDENCE": "D2",
    "T7_PLANNING_SEASONALITY": "D2",
    "T8_EXPERIENCE_QUALITY": "D6",
    "T9_PRICE_OFFER": "D5",
    "T10_REDO_REFUND": "D6",
    "T11_UNCLASSIFIED": "D6",
}

# Customer-side influenceability (0-5). T9 is out of scope by C1.
INFLUENCEABILITY = {
    "T1_POST_SERVICE_CLOSURE": 4,
    "T2_NEED_RECOGNITION": 4,
    "T3_MENTAL_AVAILABILITY": 4,
    "T4_CATEGORY_AWARENESS": 5,
    "T5_LOCAL_WHATSAPP_DEFAULT": 3,
    "T6_DECISION_CONFIDENCE": 4,
    "T7_PLANNING_SEASONALITY": 4,
    "T8_EXPERIENCE_QUALITY": 2,
    "T9_PRICE_OFFER": 0,  # cannot influence via discounts/pricing (C1)
    "T10_REDO_REFUND": 1,
    "T11_UNCLASSIFIED": 0,
}

METRIC_LINK = {
    "D1": 1,
    "D2": 5,
    "D3": 5,
    "D4": 4,
    "D5": 4,
    "D6": 3,
}


def decompose() -> list[dict[str, Any]]:
    """Return D1..D6 chain with plain-language fields."""
    out = []
    for d in config.DECOMPOSITION:
        out.append({
            "id": d["id"],
            "stage": d["stage"],
            "question_customer_can_answer": d["question"],
            "public_data_proxy": d["public_proxy"],
            "influenceable": "Y" if d["influenceable"] else "N",
            "why": d["notes"],
            "publicly_measurable": "Y" if d["publicly_measurable"] else "N",
        })
    return out


def map_to_metric(stage: str) -> str:
    """Explain how moving a stage affects 90-day repeat without false needs."""
    stage = str(stage).upper()
    mapping = {
        "D1": "Need incidence is mostly exogenous; the product should not create false needs. Measure it via self-reported needs in 90 days.",
        "D2": "If customers recognize real home needs earlier, they can plan or act within the 90-day window, increasing repeat bookings without inventing needs.",
        "D3": "If UC is top-of-mind when a real need arises, customers are more likely to return to UC within 90 days instead of drifting away.",
        "D4": "If customers know UC covers the category they need, a real need is more likely to convert into a UC booking within 90 days.",
        "D5": "If customers choose UC over local/DIY alternatives for a real need, repeat share rises; this must be driven by confidence/clarity, not discounts (C1).",
        "D6": "Reducing completion friction can prevent drop-off for customers who already intend to book, but it must not be framed as the only root cause.",
    }
    return mapping.get(stage, "Stage not mapped.")


def _reach_score(share_pct: float) -> int:
    # share_pct 0-100 -> 0-5
    if share_pct <= 0:
        return 0
    if share_pct < 5:
        return 1
    if share_pct < 10:
        return 2
    if share_pct < 20:
        return 3
    if share_pct < 35:
        return 4
    return 5


def _evidence_strength(share_pct: float, interviews_summary: dict[str, Any] | None) -> int:
    # Public evidence from share; add interview boost if provided.
    base = 1 if share_pct <= 0 else 2 if share_pct < 10 else 3 if share_pct < 25 else 4
    boost = 0
    if interviews_summary:
        supported = interviews_summary.get("supported_themes", []) or []
        if isinstance(supported, list) and supported:
            boost = 1
    return min(5, base + boost)


def score_opportunities(discovery: dict[str, Any], interviews_summary: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Score and rank opportunities from discovery output."""
    agg = discovery.get("aggregate", {}) if isinstance(discovery, dict) else {}
    dist = agg.get("theme_distribution", [])
    rows = []
    for t in dist:
        code = str(t.get("code"))
        share = float(t.get("share_pct", 0) or 0)
        stage = THEME_TO_STAGE.get(code, "D6")
        influence = INFLUENCEABILITY.get(code, 0)
        metric_link = METRIC_LINK.get(stage, 2)
        evidence = _evidence_strength(share, interviews_summary)
        reach = _reach_score(share)

        excluded = code == "T9_PRICE_OFFER"
        reason_excluded = "Out of scope by C1: cannot use discounts/pricing/incentives." if excluded else ""
        score = 0 if excluded or influence == 0 else reach * influence * metric_link * evidence

        rows.append({
            "theme_code": code,
            "theme_name": t.get("name", ""),
            "share_pct": share,
            "stage": stage,
            "reach_0_5": reach,
            "influenceability_0_5": influence,
            "metric_link_0_5": metric_link,
            "evidence_strength_0_5": evidence,
            "score": score,
            "excluded": excluded,
            "exclusion_reason": reason_excluded,
            "metric_explanation": map_to_metric(stage),
        })

    rows.sort(key=lambda r: (r["excluded"], -r["score"], -r["share_pct"]))
    for i, r in enumerate(rows, start=1):
        r["rank"] = i
    return rows


def opportunities_dataframe(discovery: dict[str, Any], interviews_summary: dict[str, Any] | None = None) -> pd.DataFrame:
    """Return ranked opportunities as a DataFrame ready for Altair charts."""
    rows = score_opportunities(discovery, interviews_summary)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["label"] = df["theme_code"] + " — " + df["theme_name"]
    df["status"] = df["excluded"].map(lambda x: "Excluded (C1/out of scope)" if x else "Candidate")
    return df


if __name__ == "__main__":
    config.ensure_dirs()
    if config.DISCOVERY_JSON.exists():
        discovery = json.loads(config.DISCOVERY_JSON.read_text(encoding="utf-8"))
    else:
        from . import engine

        discovery = engine.run(config.DATA_DIR / "public_corpus_sample.csv", llm=None)
    df = opportunities_dataframe(discovery)
    cols = ["rank", "theme_code", "share_pct", "stage", "reach_0_5", "influenceability_0_5", "metric_link_0_5", "evidence_strength_0_5", "score", "excluded"]
    print(df[cols].to_string(index=False))