"""Metric decomposition page. Respect docs/constraints.md (C4, C5)."""

from __future__ import annotations

import base64

import pandas as pd
import streamlit as st

from src import config


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-9.png"


def _header_html() -> str:
    """Inline the HCA-LOGO-9 mark beside the page title."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="Home Care Assistant logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "Metric Breakdown</h1>"
        "</div>"
    )


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("Metric decomposition using only customer self-report or public data. No internal UC data.")

    st.subheader("Exact metric definition")
    st.info(config.METRIC_DEFINITION)

    st.subheader("Business metric → product outcomes → customer behaviours → measurable indicators")
    chain = [
        ("Business metric", "90-day repeat completion rate for eligible anchor customers"),
        ("Product outcomes", "Need recognition, mental availability, category clarity, choice confidence, frictionless completion"),
        ("Customer behaviours", "D1–D6: what the customer actually does or decides"),
        ("Measurable indicators", "Customer self-report (interviews) or public traces only — no internal UC data"),
    ]
    for label, detail in chain:
        st.markdown(f"**{label}:** {detail}")

    tree = pd.DataFrame([
        {
            "stage": f"{d['id']} · {d['stage']}",
            "customer_behaviour": d["question"],
            "product_outcome": d["product_outcome"],
            "measurable_indicator": d["measurable_indicator"],
            "influenceable": "Yes" if d.get("influenceable") else "No",
        }
        for d in config.DECOMPOSITION
    ])
    st.dataframe(tree, width="stretch", hide_index=True)

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
