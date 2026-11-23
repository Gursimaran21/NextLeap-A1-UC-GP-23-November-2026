"""User research page. Respect docs/constraints.md (C6, C7)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import config, research


PROTOCOL = [
    "Tell me about the last Urban Company service you used. What prompted it?",
    "After that service, did any other home need come up in the next 90 days?",
    "If yes: did you book through UC, use someone local, DIY, or do nothing? Why?",
    "If no: was there no need, or was there a need you didn't act on?",
    "When a need comes up, how do you decide what to do first?",
    "Did you know UC offered the category you needed? What made you think of / not think of UC?",
    "What would have made it easier to plan or act on the next home need?",
]


def render() -> None:
    st.title("User Research")
    st.caption("5–6 anonymized interviews. No PII, no screenshots, no invoices, no personal documents.")

    st.subheader("Interview protocol")
    for i, q in enumerate(PROTOCOL, start=1):
        st.markdown(f"{i}. {q}")
    st.info("Anonymity: respondents are labeled R01–R06. No names, phone numbers, addresses, screenshots, invoices, or personal documents.")

    st.subheader("Respondent table")
    try:
        df = research.load_interviews()
    except Exception as e:
        st.error(f"Interview data validation error: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No interviews loaded yet. Add anonymized rows to data/interviews.csv (R01–R06).")
        st.dataframe(research.interview_template(), use_container_width=True, hide_index=True)
    else:
        show_cols = [c for c in ["respondent_id", "category", "returner_90d", "total_bookings", "city_tier", "theme_code"] if c in df.columns]
        st.dataframe(df[show_cols], use_container_width=True, hide_index=True)
        st.metric("Respondents", df["respondent_id"].nunique())
        st.metric("Returners (90d)", int((df["returner_90d"] == "yes").sum()) if "returner_90d" in df.columns else 0)

    st.subheader("Synthesis: validates vs challenges AI findings")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Validates (placeholder)**")
        st.markdown(
            """
            - [Fill after interviews] Users report forgetting next need after service closure.
            - [Fill] Local/WhatsApp defaults appear for small/urgent tasks.
            - [Fill] Category awareness/decision confidence gaps exist.
            """
        )
    with c2:
        st.markdown("**Challenges / nuances (placeholder)**")
        st.markdown(
            """
            - [Fill after interviews] Some non-return is genuine no-need, not a gap.
            - [Fill] Experience issues may co-exist but are not the primary target.
            - [Fill] Users may resist proactive nudges if perceived as salesy.
            """
        )

    st.caption("Interview count target: 5–6. Keep evidence anonymized and public-safe.")


render()
