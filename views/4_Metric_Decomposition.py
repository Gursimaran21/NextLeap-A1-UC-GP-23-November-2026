"""Metric decomposition page. Respect docs/constraints.md (C4, C5)."""

from __future__ import annotations

import streamlit as st

from src import config


def render() -> None:
    st.title("Metric Breakdown")
    st.caption("Metric decomposition using only customer self-report or public data. No internal UC data.")

    st.subheader("Exact metric definition")
    st.info(config.METRIC_DEFINITION)

    st.subheader("D1–D6 decomposition")
    for d in config.DECOMPOSITION:
        influ = bool(d.get("influenceable"))
        badge = "🟢 Influencable" if influ else "⚪ Not directly influencable"
        meas = "Public/self-report measurable: limited" if not d.get("publicly_measurable") else "Public/self-report measurable"
        with st.container(border=True):
            st.markdown(f"### {d['id']} · {d['stage']} {badge}")
            st.write(f"**Question:** {d['question']}")
            st.write(f"**Customer can answer:** {d['customer_can_answer']}")
            st.write(f"**Public proxy:** {d['public_proxy']}")
            st.write(f"**How we'd measure (self-report/public only):** {d['customer_can_answer']} / {d['public_proxy']}")
            st.caption(f"{meas} · Notes: {d['notes']}")

    st.subheader("Where to focus")
    st.markdown(
        """
        Focus on **D2–D5**: recognition, mental availability, category consideration, and choice confidence.  
        **D1** is partly exogenous; **D6** overlaps experience/ops but can include customer-side clarity.  
        All solutions must stay customer-side and respect C1/C2.
        """
    )


render()
