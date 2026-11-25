"""Risks and mitigations page. Respect docs/constraints.md."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def _risk_table() -> pd.DataFrame:
    """Risk register from docs/ProblemStatement.txt R8 and PRD section 12."""
    return pd.DataFrame([
        {
            "risk": "Public corpus bias over-represents complaints",
            "likelihood": "High", "severity": "High", "impact": "High",
            "mitigation": "Bias report, continuity-vs-experience split, interview validation.",
            "early_warning": "T8 dominates despite interview contradiction.",
            "label": "Evidence", "color": "#E08A00",
        },
        {
            "risk": "Silent non-returners absent from public data",
            "likelihood": "High", "severity": "High", "impact": "High",
            "mitigation": "State limitation explicitly; recruit non-returners in interviews.",
            "early_warning": "Findings rely only on people who posted reviews.",
            "label": "Evidence", "color": "#E08A00",
        },
        {
            "risk": "Fabricated or weak evidence",
            "likelihood": "Medium", "severity": "High", "impact": "High",
            "mitigation": "No-fabrication rule; TODO placeholders; QA blockers; no invented labels or quotes.",
            "early_warning": "Missing labels, interviews, or tests near deadline.",
            "label": "Integrity", "color": "#B00020",
        },
        {
            "risk": "Incorrect or unnecessary AI recommendations",
            "likelihood": "Medium", "severity": "High", "impact": "High",
            "mitigation": "Golden-set evaluation, tool-choice checks, confidence thresholds, no-action routes.",
            "early_warning": "High UC_CATEGORY rate on vague or low-confidence inputs.",
            "label": "AI quality", "color": "#B00020",
        },
        {
            "risk": "Incomplete or outdated public information",
            "likelihood": "Medium", "severity": "Medium", "impact": "Medium",
            "mitigation": "Show source links and access dates; label confidence; use non-UC-specific reference facts.",
            "early_warning": "Unsourced or stale planning-card content.",
            "label": "Evidence", "color": "#E08A00",
        },
        {
            "risk": "MVP nudges unnecessary bookings",
            "likelihood": "Medium", "severity": "High", "impact": "High",
            "mitigation": "DIY/local/wait routes, anti-nudge metrics, no booking CTA, no-action recognition.",
            "early_warning": "Rising booking-intent language in tool traces or low 'matched real need' feedback.",
            "label": "Trust", "color": "#E08A00",
        },
        {
            "risk": "Low adoption or poor user experience",
            "likelihood": "Medium", "severity": "Medium", "impact": "Medium",
            "mitigation": "Keep flow short; task-based testing with >=3 users; iterate on observed friction.",
            "early_warning": "Users abandon before step 3; low calendar/reflection completion.",
            "label": "Adoption", "color": "#2C6EAA",
        },
        {
            "risk": "Over-reliance on AI",
            "likelihood": "Medium", "severity": "Medium", "impact": "Medium",
            "mitigation": "Deterministic fallback, transparent rationale, human-labelled validation, review before accepting outputs.",
            "early_warning": "Team accepts AI output without checking evidence.",
            "label": "Process", "color": "#2C6EAA",
        },
        {
            "risk": "PII leakage in corpus, interviews, or logs",
            "likelihood": "Low", "severity": "High", "impact": "High",
            "mitigation": "PII redaction, schema validation, QA scan, no documents collected.",
            "early_warning": "QA PII scan hits; free text contains phone/address.",
            "label": "Privacy", "color": "#B00020",
        },
        {
            "risk": "Streamlit Cloud ephemeral storage",
            "likelihood": "Medium", "severity": "Medium", "impact": "Medium",
            "mitigation": "In-memory downloads; regenerate from source; commit final deliverables.",
            "early_warning": "Generated files missing after redeploy.",
            "label": "Delivery", "color": "#2C6EAA",
        },
        {
            "risk": "Category or city behaviour differences invalidate segment",
            "likelihood": "Medium", "severity": "Medium", "impact": "Medium",
            "mitigation": "Vary category, city tier, household type, and booking frequency in interviews.",
            "early_warning": "One category or one city dominates all findings.",
            "label": "Segment", "color": "#2C6EAA",
        },
    ])


def render() -> None:
    st.title("Risks")
    st.caption("Risks, likelihood, severity, mitigations, and early-warning signals. Color + label (not color-only).")

    df = _risk_table()
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(
                f"<div style='border-left:6px solid {r['color']}; padding-left:12px;'>"
                f"<strong>{r['label']}</strong> · <strong>{r['risk']}</strong></div>",
                unsafe_allow_html=True,
            )
            st.write(
                f"**Likelihood:** {r['likelihood']}  |  **Severity:** {r['severity']}  |  "
                f"**Impact:** {r['impact']}"
            )
            st.write(f"**Mitigation:** {r['mitigation']}")
            st.write(f"**Early-warning signal:** {r['early_warning']}")

    st.subheader("Risk register (table)")
    st.dataframe(df.drop(columns=["color"]), width="stretch", hide_index=True)


render()
