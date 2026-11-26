"""Urban Company context page.

Mirrors the structure of public About Us / city pages at a high level.
Public information only. Respects docs/constraints.md (C1/C2/C3).
"""

from __future__ import annotations

import base64

import streamlit as st

from src import config

LOGO_PATH = config.ROOT / "assets" / "urban_company_logo.jpg"
ABOUT_BG_PATH = config.ROOT / "assets" / "about_background_1.jpg"

BUSINESS_UNITS = [
    (
        "India Consumer Services",
        "Trusted home services across Beauty & Wellness and Home Repairs.",
    ),
    (
        "Insta Help",
        "Instant, verified household help. Excluded from this project's core-category metric.",
    ),
    (
        "Native",
        "Devices under the Native brand for tech-enabled living.",
    ),
    (
        "International",
        "Services in the UAE, Singapore and KSA.",
    ),
]

SERVICE_GROUPS = [
    ("Cleaning & Pest Control", "Deep cleaning, room cleaning, pest control"),
    ("AC & Appliance Repair", "AC service, appliance and stove repair"),
    ("Electrician, Plumber & Carpenter", "Repairs and installation work at home"),
    ("Salon & Spa", "Beauty and wellness services at home"),
    ("Painting & Water-proofing", "Home painting and protection"),
    ("Native Smart Products", "Water purifiers and smart locks"),
]


def _header_html() -> str:
    """Inline the logo and title in one vertically centred row, like the MVP page."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/jpeg;base64,{encoded}" alt="Urban Company logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "Urban Company</h1>"
        "</div>"
    )


def _about_html() -> str:
    """Title-led About card with a home-care visual, like the MVP page."""
    encoded = base64.b64encode(ABOUT_BG_PATH.read_bytes()).decode("ascii")
    tags = [
        "Home services",
        "Beauty & Wellness",
        "Home Repairs",
        "Insta Help",
        "Native",
        "International",
    ]
    tag_html = "".join(
        '<span style="background:#EBDFF0; border:1px solid #D9C6E0; color:#500C6B; '
        'padding:5px 11px; border-radius:999px; font-size:11px; '
        f'letter-spacing:0.02em; font-weight:600;">{tag}</span>'
        for tag in tags
    )
    pillars = [
        (f"{i + 1:02d}", title, body) for i, (title, body) in enumerate(BUSINESS_UNITS)
    ]
    pillar_html = "".join(
        '<div style="display:flex; gap:10px; align-items:flex-start;">'
        '<span style="flex:0 0 26px; height:26px; border-radius:50%; background:#500C6B; '
        'color:#ffffff; font-size:11px; font-weight:700; display:flex; '
        f'align-items:center; justify-content:center;">{num}</span>'
        '<div><div style="font-size:13px; font-weight:700; color:#12212B;">'
        f'{title}</div><div style="font-size:12px; line-height:1.45; color:#52606A;">'
        f'{detail}</div></div></div>'
        for num, title, detail in pillars
    )
    return f"""
    <div style="display:flex; flex-wrap:wrap; gap:26px; align-items:stretch; background:#F7F1F9;
                border:1px solid #E6D9EA; border-radius:18px; padding:26px;
                box-shadow:0 16px 36px rgba(15,27,38,0.08);">
      <div style="flex:1 1 420px; min-width:300px;">
        <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                    padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                    text-transform:uppercase; font-weight:700; margin-bottom:12px;">About Urban Company</div>
        <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
          Urban Company is an online services marketplace that connects customers with
          trained professionals for at-home beauty, wellness, cleaning, repair, and
          maintenance services.
        </p>
        <p style="margin:0 0 12px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
          Its public positioning is to simplify urban living through reliable, high-quality
          and transparent services.
        </p>
        <div style="display:grid; gap:12px; margin-bottom:14px;">{pillar_html}</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px;">{tag_html}</div>
      </div>
      <div style="flex:1 1 340px; min-width:340px; display:flex; align-items:center; justify-content:center;">
        <div style="width:340px; height:453px; border-radius:14px; overflow:hidden;">
          <img src="data:image/jpeg;base64,{encoded}" alt="Home care planning visual"
               style="display:block; width:100%; height:100%; object-fit:cover; border-radius:14px;" />
        </div>
      </div>
    </div>
    """


def _card(title: str, body: str) -> None:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(body)


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption(
        "A technology-driven platform connecting customers with trusted professionals "
        "for home and beauty needs - from cleaning and repairs to salon and spa services."
    )

    st.markdown(_about_html(), unsafe_allow_html=True)

    st.subheader("Our Business")
    cols = st.columns(2)
    for i, (title, body) in enumerate(BUSINESS_UNITS):
        with cols[i % 2]:
            _card(title, body)
        if i % 2 == 1 and i < len(BUSINESS_UNITS) - 1:
            cols = st.columns(2)

    st.subheader("Home services at your doorstep")
    st.markdown(
        "Public city pages group services in the following way. This project studies "
        "the period **after** one completed service, not the booking flow."
    )
    cols = st.columns(3)
    for i, (title, body) in enumerate(SERVICE_GROUPS):
        with cols[i % 3]:
            _card(title, body)
        if i % 3 == 2 and i < len(SERVICE_GROUPS) - 1:
            cols = st.columns(3)

    st.subheader("At a glance")
    m1, m2, m3 = st.columns(3)
    m1.metric("Service rating", "4.8")
    m2.metric("Customers globally", "12M+")
    m3.metric("Repeat share of NTV", f"~{config.REPEAT_NTV_PCT}%")
    st.caption(
        "Service rating and customer count are public website figures as on 31 Dec 2024. "
        f"The ~{config.REPEAT_NTV_PCT}% repeat share comes from the project brief and is not recomputed here."
    )

    st.subheader("Where this project fits")
    st.markdown(
        f"""
        | Stage | What happens | Project focus |
        |---|---|---|
        | Before service | Customer notices a need and chooses a provider | Context only |
        | During service | Professional visits and completes the work | Context only |
        | After service | Customer returns to daily life; next needs may or may not be recognised | **Main focus** |

        The business metric is the share of customers who complete another eligible
        service within **{config.WINDOW_DAYS} days** of an anchor service. Redos, warranty
        claims, refunds and InstaHelp are excluded.
        """
    )

    st.subheader("Scope and guardrails")
    st.markdown(
        """
        The Home Care Companion is a customer-side continuity aid. It organises what the
        customer chooses to share, explains home-care categories in plain language, and
        creates a checklist and reminders. It can also say that **no service is needed**.

        Deliberately out of scope:

        - No discounts, coupons, memberships or pricing changes.
        - No changes to professional earnings, pay or management.
        - No bookings, messages, payments or account actions.
        - No logged-in scraping; only public information and customer-provided details.
        """
    )

    st.subheader("How to read this app")
    st.markdown(
        """
        1. **Home Care Companion** — try the MVP with a household scenario.
        2. **Discovery Engine** — inspect the public-review evidence.
        3. **Evidence Log** — review the manually labelled examples.
        4. **Metric Breakdown** — see the business metric and exclusions.
        5. **User Research / Problem Definition** — read interviews and the hypothesis.
        6. **MVP Testing / Success Metrics / Risks / Deck** — validation plan and submission.
        """
    )

    st.caption(
        "Sources: public About Us and Chennai city pages, plus the project brief. "
        "URLs and access dates are logged in `docs/sources.md`. No private or logged-in "
        "Urban Company surfaces were used."
    )


render()
