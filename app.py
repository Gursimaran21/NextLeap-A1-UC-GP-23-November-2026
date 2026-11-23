"""Urban Company Graduation Project - Streamlit router.

Respect docs/constraints.md. MVP is the default/root page.
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
    page_title="Urban Company — Home Care Companion",
    page_icon="🏠",
    layout="wide",
)
config.ensure_dirs()

st.markdown(
    """
    <style>
      html, body, [class*="css"] { font-size: 16px; color: #12212B; background: #FFFFFF; }
      .block-container { padding-top: 2rem; padding-bottom: 2rem; }
      [data-testid="stSidebar"] { background-color: #F3F6F5; }
      [data-testid="stSidebar"] * { color: #12212B; }
      a, button, input, textarea, [role="tab"] { outline-color: #0B6E4F !important; }
      a:focus-visible, button:focus-visible, input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible {
        outline: 3px solid #0B6E4F !important;
        outline-offset: 2px;
      }
      .stAlert { border-radius: 8px; }
      .small-muted { color: #6B7A83; font-size: 0.9rem; }
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

with st.sidebar:
    st.markdown("### UC Graduation Project")
    st.caption("Nov 2026 · PMF Cohort 52")
    st.divider()
    st.markdown(
        '<div class="small-muted">Public prototype · No bookings · No account access · Public information only</div>',
        unsafe_allow_html=True,
    )

pg = st.navigation(pages)
pg.run()