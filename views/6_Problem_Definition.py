"""Problem definition page. Respect docs/constraints.md (C1)."""

from __future__ import annotations

import base64

import streamlit as st

from src import config


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-11.png"


def _header_html() -> str:
    """Inline the HCA-LOGO-11 mark beside the page title."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="Home Care Assistant logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "Problem Definition</h1>"
        "</div>"
    )


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("Customer-side continuity problem. Not a bad-experience problem. Not an offer/pricing problem.")

    st.subheader("Evolution chain")
    steps = [
        "Business Metric",
        "Product Outcomes",
        "AI Discovery",
        "Primary Research",
        "Problem Definition",
        "MVP/Test",
    ]
    cols = st.columns(len(steps))
    for i, (col, s) in enumerate(zip(cols, steps)):
        col.markdown(f"**{i+1}. {s}**")
        if i < len(steps) - 1:
            col.caption("→")
    st.info(
        "Business Metric → Product Outcomes → AI Discovery → Primary Research → Problem Definition → MVP/Test. "
        "Each step narrows from metric movement to a testable customer-side problem."
    )

    st.error("Explicit callout: This is **not** a bad-experience/quality-only problem, and **not** an offer/discount/pricing problem (C1).")

    st.subheader("Structured problem statement")
    st.markdown(
        f"""
        **Segment:** {config.SEGMENT_NAME}

        **Scenario:** After completing one core-category service, the customer manages home needs over the next 90 days without a clear planning/decision aid. When another need arises, they may not recognize it, may not think of Urban Company, or may default to local/DIY options.

        **Product outcome:** Increase the share of eligible customers who complete another core-category booking within 90 days of the anchor booking, excluding InstaHelp, redos, warranty, and refunds.

        **Root cause (hypothesis):** Post-service closure and home-care planning gaps reduce need recognition, mental availability, and decision confidence.

        **Current workarounds:** Remembering ad hoc, asking neighbours/family, WhatsApp/local vendors, DIY, or ignoring until urgent.

        **User value:** A calm, trustworthy way to anticipate, understand, and route home needs - without pressure, spam, or transactions.

        **Business sense:** Repeat bookings drive a large share of NTV (~{config.REPEAT_NTV_PCT}% from repeat customers, as given). Improving continuity for genuine needs can increase repeat completion while respecting trust.
        """
    )

    st.info(
        "Evidence status: segment and product outcome come from the metric and discovery stages. "
        "Journey scenario, root cause, workarounds, and user value await interview validation "
        "(see views/5_User_Research.py)."
    )

    st.subheader("What we are not solving")
    st.markdown(
        """
        - No discounts/coupons/membership/pricing/professional-pay changes.
        - No booking, messaging, or account actions in MVP.
        - No bad-experience-only framing; quality issues are control/guardrail signals, not the core wedge.
        """
    )


render()
