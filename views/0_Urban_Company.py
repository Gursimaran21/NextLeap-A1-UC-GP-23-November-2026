"""Urban Company context page.

Mirrors the structure of public About Us / city pages at a high level.
Public information only. Respects docs/constraints.md (C1/C2/C3).
"""

from __future__ import annotations

import streamlit as st

from src import config

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


def _card(title: str, body: str) -> None:
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.caption(body)


def render() -> None:
    st.title("Urban Company")
    st.caption(
        "Public company context · Home Care Companion graduation project · Nov 2026"
    )

    st.subheader("About Us")
    st.markdown(
        """
        Urban Company is a technology-driven platform that connects customers with
        trusted professionals for home and beauty needs — from cleaning and repairs to
        salon and spa services. Its public positioning is to simplify urban living
        through reliable, high-quality and transparent services.

        This page gives context only. The app does not provide service search, booking,
        payment, messaging, or account actions.
        """
    )
    st.caption("Paraphrased from the public About Us page; source logged in `docs/sources.md`.")

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
