"""Urban Company context page.

Public information only. Respects docs/constraints.md (C1/C2/C3).
"""

from __future__ import annotations

import streamlit as st

from src import config


def render() -> None:
    st.title("Urban Company")
    st.caption(
        "Public context for the Home Care Companion graduation project. "
        "No account access, no transactions, no logged-in data."
    )

    st.subheader("What the company does")
    st.markdown(
        """
        Urban Company is a home-services marketplace. Customers use it for recurring and
        one-off home needs such as deep cleaning, AC service, plumbing, pest control,
        appliance repair and salon services. The work is delivered by professionals who
        visit the customer's home.

        This project studies what happens **after** one of those services is completed:
        whether genuine next home needs are recognised, understood and easy to act on
        without pressure.
        """
    )

    st.subheader("Why repeat behaviour matters")
    col1, col2 = st.columns([1, 2])
    col1.metric("Repeat share of net transaction value", f"~{config.REPEAT_NTV_PCT}%")
    col2.markdown(
        f"""
        The project brief gives **~{config.REPEAT_NTV_PCT}% of net transaction value** as
        coming from repeat customers. That is why the business metric in this app looks at
        the share of customers who complete another eligible service within
        **{config.WINDOW_DAYS} days** of an anchor service.

        The number is taken from the brief as supplied; it is not recomputed or
        independently verified in this prototype.
        """
    )

    st.subheader("Where this project fits")
    st.markdown(
        """
        The Home Care Companion is a **customer-side continuity aid**. It organises the
        history a customer chooses to share, explains home-care categories in plain
        language, and produces a checklist and reminders. It can also say that **no
        service is needed**.

        Deliberately out of scope:

        - No discounts, coupons, memberships or pricing changes.
        - No changes to professional earnings, pay or management.
        - No bookings, messages, or actions on a customer's account.
        - No logged-in scraping; only public information and customer-provided details.
        """
    )

    st.subheader("How to use this app")
    st.markdown(
        """
        1. **Home Care Companion** - try the MVP with a household scenario.
        2. **Discovery Engine** - inspect the public-review evidence.
        3. **Evidence Log** - review the manually labelled examples.
        4. **Metric Breakdown** - see the business metric and exclusions.
        5. **User Research / Problem Definition** - read the interviews and hypothesis.
        6. **MVP Testing / Success Metrics / Risks / Deck** - validation plan and submission.
        """
    )
    st.markdown("Use the **Home Care Companion** entry in the top navigation to try the MVP.")

    st.caption(
        "Company context source: the project brief (`docs/brief.md`) and the public-source "
        "log (`docs/sources.md`). No private or logged-in Urban Company surfaces were used."
    )


render()
