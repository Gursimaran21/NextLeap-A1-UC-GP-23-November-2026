"""Urban Company Graduation Project - Streamlit router.

Respect docs/constraints.md. MVP is the default/root page.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

# Mirror Streamlit Cloud secrets into environment for src.llm.
try:
    for _k in ("GEMINI_API_KEY", "GEMINI_MODEL"):
        if _k not in os.environ and _k in st.secrets:
            os.environ[_k] = str(st.secrets[_k])
except Exception:
    pass

from src import config

st.set_page_config(
    page_title="Urban Company - Home Care Companion",
    page_icon="🏠",
    layout="wide",
)
config.ensure_dirs()


LOGO_PATH = Path(__file__).resolve().parent / "assets" / "uc_logo_1.jpg"

# Places the Urban Company logo at the left of the top nav, before the page links.
st.logo(str(LOGO_PATH), size="large")

st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-size: 16px; color: #12212B; background: #FFFFFF; }
      .block-container { padding-top: 6.5rem !important; padding-bottom: 2rem; }
      a, button, input, textarea, [role="tab"] { outline-color: #500C6B !important; }
      a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible {
        outline: 3px solid #500C6B !important;
        outline-offset: 2px;
      }
      .stAlert { border-radius: 8px; }
      .small-muted { color: #6B7A83; font-size: 0.9rem; }
      [data-testid="stProgress"] [data-testid="stProgressBarTrack"] > div {
        background-color: #500C6B !important;
      }
      [data-testid="stTopNavLink"],
      [data-testid="stTopNavDropdownLink"],
      [data-testid="stTopNavSection"] {
        background-color: #EBDFF0 !important;
      }
      [data-testid="stTopNavLink"],
      [data-testid="stTopNavDropdownLink"],
      [data-testid="stTopNavSection"],
      [data-testid="stTopNavLink"] *,
      [data-testid="stTopNavDropdownLink"] *,
      [data-testid="stTopNavSection"] * {
        color: #500C6B !important;
      }
      [data-testid="stTopNavLink"]:hover,
      [data-testid="stTopNavDropdownLink"]:hover,
      [data-testid="stTopNavSection"]:hover {
        background-color: #D9C6E0 !important;
      }
      [data-testid="stTopNavLink"][aria-current="page"] {
        background-color: #500C6B !important;
      }
      [data-testid="stTopNavLink"][aria-current="page"] * {
        color: #FFFFFF !important;
      }
      [data-testid="stHeader"] .rc-overflow {
        position: absolute !important;
        left: 50% !important;
        top: 50% !important;
        transform: translate(-50%, -50%) !important;
        justify-content: center !important;
        width: max-content !important;
        max-width: calc(100% - 26rem) !important;
        margin: 0 !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        scrollbar-width: none !important;
      }
      [data-testid="stHeader"] .rc-overflow::-webkit-scrollbar {
        display: none !important;
      }
      [data-testid="stHeader"] .rc-overflow-item {
        display: block !important;
        flex: 0 0 auto !important;
        position: static !important;
      }
      [data-testid="stHeader"] .rc-overflow-item-rest {
        display: none !important;
      }
      [data-testid="stTopNavLink"],
      [data-testid="stTopNavDropdownLink"] {
        padding-left: 0.35rem !important;
        padding-right: 0.35rem !important;
        font-size: 0.78rem !important;
        gap: 0.25rem !important;
      }
      [data-testid="stTopNavLink"] span,
      [data-testid="stTopNavDropdownLink"] span {
        font-size: 0.78rem !important;
      }
      [data-testid="stHeader"] {
        position: relative !important;
        min-height: 5.5rem !important;
        background-color: transparent !important;
        border-bottom: none !important;
      }
      .stLogo,
      [data-testid="stLogo"] {
        height: 4.5rem !important;
        width: auto !important;
        max-width: 12rem !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

pages = [
    st.Page("views/1_MVP.py", title="Home Care Companion", icon="🏠", default=True),
    st.Page("views/2_Discovery_Engine.py", title="Discovery Engine", icon="🔍"),
    st.Page("views/3_Evidence_Log.py", title="Evidence Log", icon="🧾"),
    st.Page("views/4_Metric_Decomposition.py", title="Metric Breakdown", icon="🧮"),
    st.Page("views/5_User_Research.py", title="User Research", icon="🎙️"),
    st.Page("views/6_Problem_Definition.py", title="Problem Definition", icon="🎯"),
    st.Page("views/7_MVP_Testing.py", title="MVP Testing", icon="🧪"),
    st.Page("views/8_Success_Metrics.py", title="Success Metrics", icon="📏"),
    st.Page("views/9_Risks.py", title="Risks", icon="⚠️"),
    st.Page("views/10_Deck.py", title="Deck", icon="📊"),
]

pg = st.navigation(pages, position="top")
pg.run()

st.markdown(
    """
    <div style="margin-top:2rem; padding:14px 18px; background:#F7F1F9; border:1px solid #E6D9EA;
                border-radius:12px; text-align:center; color:#52606A; font-size:0.82rem; line-height:1.5;">
      <strong style="color:#500C6B;">Urban Company - Home Care Companion</strong> · NextLeap Graduation Project · Nov 2026 · PMF Cohort 52<br>
      Public prototype · No bookings · No account access · Public information only · No personal details
    </div>
    """,
    unsafe_allow_html=True,
)