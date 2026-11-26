"""User research page. Respect docs/constraints.md (C6, C7)."""

from __future__ import annotations

import base64

import pandas as pd
import streamlit as st

from src import config, research


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-10.png"


def _header_html() -> str:
    """Inline the HCA-LOGO-10 mark beside the page title."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="Home Care Assistant logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "User Research</h1>"
        "</div>"
    )


# Mirrors the nine interview areas in docs/ProblemStatement.txt (R3) and
# docs/interview_guide.md. No answers are pre-filled; real quotes are required.
PROTOCOL = [
    "How did you decide to book the initial service, and what prompted it?",
    "How did you discover Urban Company?",
    "What happened after the service was completed?",
    "What did you expect from the service?",
    "What additional household service requirements came up afterwards?",
    "How did you handle those subsequent requirements?",
    "Did you consider Urban Company again when a need arose?",
    "What motivated you to return, or prevented you from returning?",
    "Are household services generally planned, reactive, or avoided until urgent?",
]


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("5–6 anonymized interviews. No PII, no screenshots, no invoices, no personal documents.")

    st.subheader("Interview questionnaire (9 areas, R3)")
    for i, q in enumerate(PROTOCOL, start=1):
        st.markdown(f"{i}. {q}")
    st.info("Anonymity: respondents are labeled R01–R06. No names, phone numbers, addresses, screenshots, invoices, or personal documents.")

    st.subheader("Anonymized respondent profiles")
    try:
        df = research.load_interviews()
    except Exception as e:
        st.error(f"Interview data validation error: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No interviews loaded yet. Add anonymized rows to data/interviews.csv (R01–R06).")
        st.dataframe(research.interview_template(), width="stretch", hide_index=True)
    else:
        show_cols = [c for c in ["respondent_id", "category", "returner_90d", "total_bookings", "city_tier", "theme_code"] if c in df.columns]
        st.dataframe(df[show_cols], width="stretch", hide_index=True)
        st.metric("Respondents", df["respondent_id"].nunique())
        st.metric("Returners (90d)", int((df["returner_90d"] == "yes").sum()) if "returner_90d" in df.columns else 0)

    st.subheader("Findings: validates vs challenges AI discovery")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Validates (pending real interviews)**")
        st.markdown(
            """
            - [Fill after interviews] Users report forgetting the next need after service closure.
            - [Fill] Local/WhatsApp defaults appear for small or urgent tasks.
            - [Fill] Category awareness and decision-confidence gaps exist.
            """
        )
    with c2:
        st.markdown("**Challenges / nuances (pending real interviews)**")
        st.markdown(
            """
            - [Fill after interviews] Some non-return is genuine no-need, not a gap.
            - [Fill] Experience issues may co-exist but are not the primary target.
            - [Fill] Users may resist proactive nudges if they feel sales-led.
            """
        )

    st.subheader("Expected outputs (R3)")
    st.markdown(
        """
        | Output | Status |
        |---|---|
        | Interview questionnaire | Ready above (9 areas) |
        | Anonymized respondent profiles | Schema ready; real rows pending |
        | Interview findings | Pending real interviews |
        | Repeat vs non-repeat comparison | Pending real interviews |
        | Common behavioural patterns | Pending real interviews |
        | Insights validating/challenging AI discovery | Pending real interviews |
        """
    )
    st.caption("Interview count target: 5–6. Keep evidence anonymized and public-safe. Do not fill placeholders with invented quotes.")


render()
