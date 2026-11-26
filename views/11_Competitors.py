"""Public competitor briefing for Urban Company. Respect docs/constraints.md."""

from __future__ import annotations

import base64

import streamlit as st

from src import config


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-17.png"


def _clean(value: str) -> str:
    """Strip indentation from inline-HTML fragments."""
    return "\n".join(line.strip() for line in value.strip().splitlines())


def _header_html() -> str:
    """Inline HCA-LOGO-17 beside the page title."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return _clean(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
          <img src="data:image/png;base64,{encoded}" alt="Project logo"
               style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />
          <h1 style="margin:0; line-height:1.2; font-size:2.25rem;">Urban Company Competitors</h1>
        </div>
        """
    )


def _card(title: str, body: str, *, tag: str = "") -> str:
    """Render one evidence card in the project's visual style."""
    pill = (
        _clean(
            f"""
            <div style="display:inline-block; background:#EBDFF0; color:#500C6B;
                        border:1px solid #D9C6E0; padding:4px 10px; border-radius:999px;
                        font-size:10px; letter-spacing:0.08em; text-transform:uppercase;
                        font-weight:700; margin-bottom:8px;">{tag}</div>
            """
        )
        if tag
        else ""
    )
    return _clean(
        f"""
        <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:16px;
                    padding:18px; height:100%; box-shadow:0 12px 28px rgba(15,27,38,0.06);">
          {pill}
          <div style="font-size:14px; font-weight:700; color:#12212B; line-height:1.35;">{title}</div>
          <div style="margin-top:7px; font-size:12px; line-height:1.6; color:#52606A;">{body}</div>
        </div>
        """
    )


SNAPSHOT = [
    {
        "name": "Snabbit",
        "founded": "2024",
        "base": "Bengaluru, India",
        "promise": "Everyday household help dispatched from dense micro-markets in about 10 minutes.",
        "categories": "Cleaning, dishwashing, laundry, kitchen prep; instant salon-at-home pilot.",
        "scale": "Over 40,000 jobs a day and more than 15,000 workers by Apr 2026; crossed 1 million monthly jobs in Mar 2026.",
        "funding": "$56M Series D in Apr 2026; about $112M raised in total; reported valuation around $350M.",
    },
    {
        "name": "Pronto",
        "founded": "2025",
        "base": "Bengaluru, India",
        "promise": "Background-verified Pros for quick home help, with instant, scheduled or recurring options.",
        "categories": "Laundry, kitchen prep, home cleaning; expanding into car washing, gardening and a home-cooks pilot.",
        "scale": "Over 26,000 daily bookings by May 2026, up from about 3,000 in early Dec 2025.",
        "funding": "$25M Series B in Mar 2026 at a $100M valuation; an additional $20M in May 2026 at a $200M valuation.",
    },
]

SNABBIT_FACTS = [
    (
        "Operating model",
        "A managed, hyperlocal fleet is stationed around dense residential clusters. Public reporting "
        "describes a 100% women-led expert fleet in 2025 and more than 15,000 workers by Apr 2026.",
    ),
    (
        "Demand thesis",
        "The bet is that short, frequent chores behave more like an everyday utility than a scheduled "
        "appointment. Reported fulfilment is around 10 minutes.",
    ),
    (
        "Traction signals",
        "More than 300,000 customers by Oct 2025, a reported 30–35% retention rate, over 40 micro-markets "
        "in five cities, then over 40,000 jobs a day in 2026.",
    ),
    (
        "Expansion",
        "Core categories are cleaning, dishwashing, laundry and kitchen prep. A sub-15-minute "
        "salon-at-home pilot was reported in Bengaluru in 2026.",
    ),
    (
        "Strategic read",
        "Competes on speed, frequency and supply density. The hard part is holding service quality and "
        "unit economics while entering higher-expectation categories.",
    ),
]

PRONTO_FACTS = [
    (
        "Operating model",
        "Calls its workers Pros, uses in-person training and background verification, and assigns "
        "structured shifts to make income more predictable.",
    ),
    (
        "Demand thesis",
        "Quick help for recurring household chores, available through instant, scheduled or recurring "
        "options. Reported dispatch is about 10–15 minutes.",
    ),
    (
        "Traction signals",
        "Daily bookings rose from about 3,000 in early Dec 2025 to more than 26,000 by May 2026. "
        "Public reporting also noted roughly 101,000 daily active users in late Feb 2026.",
    ),
    (
        "Expansion",
        "Laundry, kitchen prep and home cleaning are core. The company is adding car washing and "
        "gardening, and piloting home cooks.",
    ),
    (
        "Strategic read",
        "Describes itself as supply-constrained, so scaling trained workers is the central task. "
        "Management said contribution margins had turned positive in its oldest Gurugram micro-markets.",
    ),
]

COMPARISON = [
    (
        "Primary demand unit",
        "Snabbit and Pronto focus on urgent, repeatable, short-duration chores. Urban Company spans a wider "
        "set of scheduled, higher-consideration services and is also investing in instant help.",
    ),
    (
        "Fulfilment design",
        "Both challengers build density block by block so a worker is already nearby. Urban Company "
        "uses a broader professional network across many categories and cities.",
    ),
    (
        "Worker relationship",
        "Snabbit reports a women-led managed fleet; Pronto uses trained, verified Pros with structured "
        "shifts. Urban Company works with trained professionals across its service categories.",
    ),
    (
        "Customer moment",
        "The challengers own the 'I need help now' moment. Urban Company owns a wider planned-care moment. "
        "Neither is the same as helping a household decide whether help is needed at all.",
    ),
    (
        "Category economics",
        "Public reporting describes the instant-help category as capital intensive and burn-heavy. Scale, "
        "utilisation and repeat behaviour are the shared operating questions.",
    ),
]

IMPLICATIONS = [
    (
        "Speed is not the same as clarity",
        "Fast dispatch answers 'who can come quickly?'. It does not answer 'is this safe to handle myself?', "
        "'what should I prepare?' or 'what should I remember next time?'.",
    ),
    (
        "The project sits before and after the service",
        "Insta Talk is a customer-side guidance layer: need recognition, safe routing, private planning cues "
        "and aftercare continuity.",
    ),
    (
        "No need is a valid outcome",
        "A useful assistant should be able to say DIY, wait, local help or no action. That is different from "
        "a marketplace that only succeeds when a job is created.",
    ),
    (
        "Hypothesis, not proof",
        "This public scan supports the relevance of the 90-day repeat-service hypothesis. It does not prove "
        "that the MVP changes behaviour; interviews and user tests are still required.",
    ),
]

SOURCE_NOTES = [
    ("[S1]", "Reuters, 28 Apr 2026 — Snabbit funding, scale, monthly jobs and market context."),
    ("[S2]", "TechCrunch, 29 Oct 2025 — Snabbit fleet, micromarkets, retention and pricing context."),
    ("[S3]", "TechCrunch, 27 Apr 2026 — Snabbit Series D, worker count and daily jobs."),
    ("[S4]", "YourStory, 27 May 2026 — Snabbit instant salon-at-home pilot."),
    ("[P1]", "Reuters, 7 May 2026 — Pronto funding, valuation, daily bookings and expansion."),
    ("[P2]", "TechCrunch, 2 Mar 2026 — Pronto operating model, funding, users and market context."),
    ("[P3]", "TechCrunch, 6 May 2026 — additional Series B capital and category sizing."),
    ("[U1]", "Reuters, 19 Sep 2025 — Urban Company's stated focus on instant services."),
]


def _snapshot_html() -> str:
    """Render a compact side-by-side snapshot table."""
    rows = []
    for item in SNAPSHOT:
        rows.append(
            _clean(
                f"""
                <tr>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA; font-weight:700; color:#500C6B;">{item['name']}</td>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA;">{item['founded']}<br>{item['base']}</td>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA;">{item['promise']}</td>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA;">{item['categories']}</td>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA;">{item['scale']}</td>
                  <td style="padding:12px; border-bottom:1px solid #E6D9EA;">{item['funding']}</td>
                </tr>
                """
            )
        )
    return _clean(
        f"""
        <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                    padding:22px; margin-top:20px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
          <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                      padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                      text-transform:uppercase; font-weight:700; margin-bottom:12px;">Market snapshot</div>
          <h2 style="margin:0 0 12px 0; font-size:1.45rem; color:#12212B;">Two instant-help challengers</h2>
          <div style="overflow-x:auto;">
            <table style="border-collapse:collapse; width:100%; min-width:920px; font-size:12px; line-height:1.55; color:#3B4C57;">
              <thead>
                <tr style="background:#EBDFF0; color:#12212B; text-align:left;">
                  <th style="padding:12px;">Company</th><th style="padding:12px;">Founded / base</th>
                  <th style="padding:12px;">Core promise</th><th style="padding:12px;">Categories</th>
                  <th style="padding:12px;">Scale signal</th><th style="padding:12px;">Funding position</th>
                </tr>
              </thead>
              <tbody>{''.join(rows)}</tbody>
            </table>
          </div>
        </div>
        """
    )


def _facts_html(title: str, facts: list[tuple[str, str]], source_label: str) -> str:
    """Render one named competitor profile."""
    items = "".join(
        _clean(
            f"""
            <div style="margin-bottom:12px;">
              <div style="font-size:12px; font-weight:700; color:#500C6B;">{label}</div>
              <div style="margin-top:3px; font-size:12px; line-height:1.6; color:#52606A;">{body}</div>
            </div>
            """
        )
        for label, body in facts
    )
    return _clean(
        f"""
        <div style="background:#FFFFFF; border:1px solid #E6D9EA; border-radius:18px;
                    padding:22px; height:100%;">
          <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                      padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                      text-transform:uppercase; font-weight:700; margin-bottom:10px;">{source_label}</div>
          <h2 style="margin:0 0 14px 0; font-size:1.4rem; color:#12212B;">{title}</h2>
          {items}
        </div>
        """
    )


def render() -> None:
    """Render the competitor briefing page."""
    st.markdown(_header_html(), unsafe_allow_html=True)

    st.markdown(
        _clean(
            """
            <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                        padding:22px; margin-top:14px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
              <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                          padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">Why this page exists</div>
              <h2 style="margin:0 0 10px 0; font-size:1.45rem; color:#12212B;">Reading the instant-help wave</h2>
              <div style="font-size:13px; line-height:1.7; color:#3B4C57;">
                <p style="margin:0 0 10px 0;">
                  Two shifts are converging in urban India. Households have become used to on-demand
                  convenience in food and groceries, and they are beginning to expect the same from home help.
                  At the same time, routine household work is being reframed from an informal, arranged-over-phone
                  activity into a managed service that can be requested through an app.
                </p>
                <p style="margin:0 0 10px 0;">
                  Snabbit and Pronto are the two challengers most often named alongside Urban Company in public
                  reporting. Both build dense micro-markets, keep workers close to demand and promise very short
                  arrival times. Their categories are deliberately simple and frequent: cleaning, dishwashing,
                  laundry, kitchen preparation and related chores.
                </p>
                <p style="margin:0 0 10px 0;">
                  Urban Company is also investing in instant services. The competitive question is therefore no
                  longer whether quick help matters. It is how each player creates density, protects service
                  quality and earns repeat use without turning every household need into a transaction.
                </p>
                <p style="margin:0;">
                  For this project, the useful distinction is between fulfilment and judgement. Faster dispatch
                  does not tell a household whether a problem is urgent, whether it can be handled safely at home,
                  or what to remember after a service. Insta Talk sits in that gap.
                </p>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(_snapshot_html(), unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(_facts_html("Snabbit — detailed profile", SNABBIT_FACTS, "Challenger 01"), unsafe_allow_html=True)
    with right:
        st.markdown(_facts_html("Pronto — detailed profile", PRONTO_FACTS, "Challenger 02"), unsafe_allow_html=True)

    st.markdown(
        _clean(
            """
            <div style="margin-top:24px; background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                        padding:22px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
              <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                          padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">Comparison</div>
              <h2 style="margin:0 0 14px 0; font-size:1.45rem; color:#12212B;">How they compare with Urban Company</h2>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )
    for i, (label, body) in enumerate(COMPARISON, start=1):
        st.markdown(_card(f"{i:02d} · {label}", body, tag="Read"), unsafe_allow_html=True)

    implication_cards = "".join(
        _clean(
            f"""
            <div style="background:#FFFFFF; border:1px solid #D9C6E0; border-radius:14px; padding:16px;">
              <div style="font-size:13px; font-weight:700; color:#12212B;">
                {i:02d} · {label}
              </div>
              <div style="margin-top:6px; font-size:12px; line-height:1.6; color:#52606A;">{body}</div>
            </div>
            """
        )
        for i, (label, body) in enumerate(IMPLICATIONS, start=1)
    )
    st.markdown(
        _clean(
            f"""
            <div style="margin-top:24px; background:#EBDFF0; border:1px solid #D9C6E0; border-radius:18px;
                        padding:22px;">
              <div style="font-size:11px; font-weight:700; color:#500C6B; letter-spacing:0.08em;
                          text-transform:uppercase;">Implication for Insta Talk</div>
              <h2 style="margin:6px 0 14px 0; font-size:1.45rem; color:#12212B;">What implication for Insta Talk means</h2>
              <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px;">
                {implication_cards}
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )

    source_rows = "".join(
        _clean(
            f"""
            <tr>
              <td style="padding:9px; border-bottom:1px solid #E6D9EA; font-weight:700; color:#500C6B;">{sid}</td>
              <td style="padding:9px; border-bottom:1px solid #E6D9EA;">{note}</td>
            </tr>
            """
        )
        for sid, note in SOURCE_NOTES
    )
    st.markdown(
        _clean(
            f"""
            <div style="margin-top:24px; background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                        padding:22px;">
              <div style="font-size:14px; font-weight:700; color:#12212B;">Source map</div>
              <div style="margin-top:6px; font-size:12px; line-height:1.6; color:#52606A;">
                Public sources used for this briefing are listed below by ID. No URL is displayed in the app.
              </div>
              <table style="border-collapse:collapse; width:100%; margin-top:12px; font-size:12px; color:#3B4C57;">
                <tbody>{source_rows}</tbody>
              </table>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


render()
