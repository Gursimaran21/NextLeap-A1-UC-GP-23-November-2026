"""Risks and mitigations page. Respect docs/constraints.md."""

from __future__ import annotations

import pandas as pd
import streamlit as st


def _risk_table() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "risk": "False need creation / pushy nudges",
            "likelihood": "Medium",
            "impact": "High",
            "mitigation": "No-need/wait routes, confidence labels, anti-nudge guardrails, no booking CTAs.",
            "early_warning": "Rising non-UC-to-UC conversion pressure complaints; low 'matched real need' feedback.",
            "label": "Trust",
            "color": "#E08A00",
        },
        {
            "risk": "Wrong or unsafe routing",
            "likelihood": "Medium",
            "impact": "High",
            "mitigation": "Deterministic safety rules, clarifying questions, immediate-help route, human review of golden tasks.",
            "early_warning": "Golden-task routing errors; user reports of unsafe/misaligned advice.",
            "label": "Safety",
            "color": "#B00020",
        },
        {
            "risk": "PII leakage in user inputs or logs",
            "likelihood": "Low",
            "impact": "High",
            "mitigation": "No PII fields, redaction in ingest, local-only checklist, QA checks.",
            "early_warning": "QA PII scan hits; user enters phone/address in free text.",
            "label": "Privacy",
            "color": "#B00020",
        },
        {
            "risk": "Bias from public vocal-negative data",
            "likelihood": "High",
            "impact": "Medium",
            "mitigation": "Bias report, source mix, golden set review, interviews as counterweight.",
            "early_warning": "Overrepresentation of T8/T9; low silent-nonreturner coverage.",
            "label": "Evidence",
            "color": "#E08A00",
        },
        {
            "risk": "Low adoption / perceived as extra work",
            "likelihood": "Medium",
            "impact": "Medium",
            "mitigation": "Keep flow short, clear value in Step 2/3, optional reflection, no login.",
            "early_warning": "High drop-off after Step 1; low calendar/reflection completion.",
            "label": "Adoption",
            "color": "#2C6EAA",
        },
        {
            "risk": "Metric gaming / wrong success signal",
            "likelihood": "Low",
            "impact": "Medium",
            "mitigation": "Use guardrails (no-need rate, non-UC route rate, 2-week follow-up), exclude redo/refund/warranty.",
            "early_warning": "Repeat rate up but user trust/fit scores down.",
            "label": "Measurement",
            "color": "#2C6EAA",
        },
    ])


def render() -> None:
    st.title("Risks")
    st.caption("Risks, mitigations, and early-warning signals. Color + label (not color-only).")

    df = _risk_table()
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(
                f"<div style='border-left:6px solid {r['color']}; padding-left:12px;'>"
                f"<strong>{r['label']}</strong> · <strong>{r['risk']}</strong></div>",
                unsafe_allow_html=True,
            )
            st.write(f"**Likelihood:** {r['likelihood']}  |  **Impact:** {r['impact']}")
            st.write(f"**Mitigation:** {r['mitigation']}")
            st.write(f"**Early-warning signal:** {r['early_warning']}")

    st.subheader("Risk register (table)")
    st.dataframe(df.drop(columns=["color"]), width="stretch", hide_index=True)


render()
