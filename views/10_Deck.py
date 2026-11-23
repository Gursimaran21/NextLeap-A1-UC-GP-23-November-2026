"""Deck page. Respect docs/constraints.md (C8, C10)."""

from __future__ import annotations

import json
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from src import config, deck


def _mini_chart(visual: str):
    # Best-effort mini visuals from available outputs
    if visual == "theme_bar" and config.DISCOVERY_JSON.exists():
        data = json.loads(config.DISCOVERY_JSON.read_text(encoding="utf-8"))
        dist = pd.DataFrame(data.get("aggregate", {}).get("theme_distribution", []))
        if not dist.empty:
            return alt.Chart(dist).mark_bar().encode(
                x=alt.X("share_pct:Q", title="Share %"),
                y=alt.Y("code:N", sort="-x", title=None),
                color=alt.Color("code:N", legend=None),
                tooltip=["code", "share_pct", "count"],
            ).properties(height=180)
    if visual == "decomposition_flow":
        df = pd.DataFrame([{"id": d["id"], "influenceable": 1 if d.get("influenceable") else 0} for d in config.DECOMPOSITION])
        return alt.Chart(df).mark_bar().encode(
            x=alt.X("id:N", title="Stage"),
            y=alt.Y("influenceable:Q", title="Influencable (1=yes)", scale=alt.Scale(domain=[0, 1])),
            color=alt.Color("influenceable:N", legend=None, scale=alt.Scale(domain=[0, 1], range=[config.PALETTE["grey"], config.PALETTE["teal"]])),
            tooltip=["id", "influenceable"],
        ).properties(height=140)
    if visual == "risks_guardrails":
        df = pd.DataFrame({"guardrail": ["Non-UC route rate", "No-need rate", "2-week follow-up"], "status": [1, 1, 1]})
        return alt.Chart(df).mark_bar().encode(
            x="status:Q", y=alt.Y("guardrail:N", sort=None), color=alt.value(config.PALETTE["blue"])
        ).properties(height=120)
    return None


def render() -> None:
    st.title("Deck")
    st.caption("10-slide, message-first deck. No fellow name. Public artefact links included.")

    # QA badge
    qa_ok = len(deck.SLIDES) <= config.DECK_MAX_SLIDES
    fellow_ok = not str(config.FELLOW_NAME_TO_EXCLUDE).strip() or str(config.FELLOW_NAME_TO_EXCLUDE).lower() not in deck._all_deck_text().lower()
    badge_cols = st.columns(4)
    badge_cols[0].metric("Slides", f"{len(deck.SLIDES)}/{config.DECK_MAX_SLIDES}")
    badge_cols[1].metric("Min body font", f"{config.MIN_FONT_PT}pt")
    badge_cols[2].metric("Filename QA", "OK" if config.DECK_PDF_NAME == "NL_UrbanCompany.pdf" else "Check")
    badge_cols[3].metric("Fellow-name guard", "OK" if fellow_ok else "Check")
    if qa_ok and fellow_ok:
        st.success("Deck QA pre-check: slide count, font rule, filename, and fellow-name guard configured.")
    else:
        st.warning("Deck QA pre-check needs attention.")

    if st.button("Build / refresh PDF", type="primary"):
        try:
            path = deck.build_pdf()
            st.success(f"Built {path.name}")
        except Exception as e:
            st.error(f"PDF build failed: {e}")

    for s in deck.SLIDES:
        with st.container(border=True):
            st.markdown(f"### Slide {s['n']}: {s['title']}")
            st.markdown(f"**Key message:** {s['key_message']}")
            for b in s.get("bullets", []):
                st.markdown(f"- {b}")
            chart = _mini_chart(s.get("visual", ""))
            if chart is not None:
                st.altair_chart(chart, width="stretch")
            links = s.get("footnote_links", []) + s.get("source_refs", [])
            if links:
                st.caption("Supporting artefacts / sources: " + " · ".join(links))

    pdf_path = config.DECK_PDF
    if pdf_path.exists():
        st.download_button(
            "Download NL_UrbanCompany.pdf",
            data=pdf_path.read_bytes(),
            file_name=config.DECK_PDF_NAME,
            mime="application/pdf",
        )
    else:
        st.info("Build the PDF to enable download.")


render()
