"""Urban Company Graduation Project - Streamlit router.

Respect docs/constraints.md. Urban Company is the default/root page.
"""

from __future__ import annotations

import os

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
    page_title="Insta Talk",
    page_icon="🏠",
    layout="wide",
)
config.ensure_dirs()

st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-size: 16px; color: #12212B; background: #FFFFFF; }
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      a, button, input, textarea, [role="tab"] { outline-color: #500C6B !important; }
      a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible {
        outline: 3px solid #500C6B !important;
        outline-offset: 2px;
      }
      .stAlert { border-radius: 8px; }
      [data-testid="stExpander"] {
        max-width: 840px !important;
      }
      [data-testid="stExpander"] > details > summary {
        background-color: #500C6B !important;
        border-radius: 6px !important;
        min-height: 30px !important;
        padding: 2px 12px !important;
      }
      [data-testid="stExpander"] > details > summary,
      [data-testid="stExpander"] > details > summary * {
        color: #FFFFFF !important;
      }
      [data-testid="stButton"]:has([title="Edit guided answers"]) > button {
        background-color: #500C6B !important;
        border: 1px solid #500C6B !important;
      }
      [data-testid="stButton"]:has([title="Edit guided answers"]) > button,
      [data-testid="stButton"]:has([title="Edit guided answers"]) > button * {
        color: #FFFFFF !important;
      }
      [data-testid="stButton"]:has([title="Reset guided notes"]) > button {
        background-color: #EBDFF0 !important;
        border: 1px solid #D9C6E0 !important;
      }
      [data-testid="stButton"]:has([title="Reset guided notes"]) > button,
      [data-testid="stButton"]:has([title="Reset guided notes"]) > button * {
        color: #500C6B !important;
      }
      [data-testid="stButton"]:has([title="Add as personal note"]) > button {
        background-color: #500C6B !important;
        border: 1px solid #500C6B !important;
      }
      [data-testid="stButton"]:has([title="Add as personal note"]) > button,
      [data-testid="stButton"]:has([title="Add as personal note"]) > button * {
        color: #FFFFFF !important;
      }
      [data-testid="stButton"]:has([title="No need right now"]) > button {
        background-color: #EBDFF0 !important;
        border: 1px solid #D9C6E0 !important;
      }
      [data-testid="stButton"]:has([title="No need right now"]) > button,
      [data-testid="stButton"]:has([title="No need right now"]) > button * {
        color: #500C6B !important;
      }
      [data-testid="stDownloadButton"]:has(button[kind="primary"]) > button {
        background-color: #500C6B !important;
        border: 1px solid #500C6B !important;
      }
      [data-testid="stDownloadButton"]:has(button[kind="primary"]) > button,
      [data-testid="stDownloadButton"]:has(button[kind="primary"]) > button * {
        color: #FFFFFF !important;
      }
      .small-muted { color: #6B7A83; font-size: 0.9rem; }
      [data-testid="stFormSubmitButton"] [data-testid="stBaseButton-secondaryFormSubmit"] {
        background-color: #F1E4F5 !important;
        color: #500C6B !important;
        border: 1px solid #D9C6E0 !important;
      }
      [data-testid="stFormSubmitButton"] [data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background-color: #EBDFF0 !important;
      }
      [data-testid="stBaseButton-tertiary"]:not([disabled]) {
        background-color: #F1E4F5 !important;
        color: #500C6B !important;
        border: 1px solid #D9C6E0 !important;
      }
      [data-testid="stBaseButton-tertiary"]:not([disabled]):hover {
        background-color: #EBDFF0 !important;
      }
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
        background-color: #F7F1F9 !important;
      }
      [data-testid="stHeader"] [data-testid="stToolbarActions"],
      [data-testid="stHeader"] [data-testid="stAppDeployButton"] {
        display: none !important;
      }
      [data-testid="stHeader"] [data-testid="stToolbar"] > div > div:last-child:not(.rc-overflow) {
        display: none !important;
      }
      [data-testid="stHeader"] [data-testid="stToolbar"] {
        justify-content: center !important;
      }
      [data-testid="stHeader"] [data-testid="stToolbar"] > div {
        justify-content: center !important;
      }
      [data-testid="stHeader"] .rc-overflow {
        flex: 1 1 auto !important;
        width: 100% !important;
        justify-content: center !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

SHOW_DECK_PAGE = False

pages = [
    st.Page("views/0_Urban_Company.py", title="Urban Company", default=True),
    st.Page("views/11_Competitors.py", title="Competitors"),
    st.Page("views/12_About_Insta_Talk.py", title="About Insta Talk & Steps"),
    st.Page("views/1_MVP.py", title="Insta Talk"),
    st.Page("views/2_Discovery_Engine.py", title="Discovery Engine"),
    st.Page("views/3_Evidence_Log.py", title="Evidence Log"),
    st.Page("views/4_Metric_Decomposition.py", title="Metric Breakdown"),
    st.Page("views/5_User_Research.py", title="User Research"),
    st.Page("views/6_Problem_Definition.py", title="Problem Definition"),
    st.Page("views/7_MVP_Testing.py", title="MVP Testing"),
    st.Page("views/8_Success_Metrics.py", title="Success Metrics"),
    st.Page("views/9_Risks.py", title="Risks & Limitations"),
]
if SHOW_DECK_PAGE:
    pages.append(st.Page("views/10_Deck.py", title="Deck"))

pg = st.navigation(pages, position="top")
pg.run()

st.markdown(
    """
    <div style="margin-top:2rem; padding:14px 18px; background:#F7F1F9; border:1px solid #E6D9EA;
                border-radius:12px; text-align:center; color:#52606A; font-size:0.82rem; line-height:1.5;">
      <strong style="color:#500C6B;">Urban Company</strong> · NextLeap Graduation Project · Nov 2026 · PMF Cohort 52<br>
      Public prototype · No bookings · No account access · Public information only · No personal details
    </div>
    """,
    unsafe_allow_html=True,
)