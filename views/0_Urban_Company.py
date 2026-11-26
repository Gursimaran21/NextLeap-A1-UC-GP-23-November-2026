"""Urban Company context page.

Mirrors the structure of public About Us / city pages at a high level.
Public information only. Respects docs/constraints.md (C1/C2/C3).
"""

from __future__ import annotations

import base64
import textwrap

import streamlit as st

from src import config

LOGO_PATH = config.ROOT / "assets" / "urban_company_logo.jpg"
ABOUT_BG_PATH = config.ROOT / "assets" / "Urban Company" / "uc-img-6.jpg"
ICON_DIR = config.ROOT / "assets" / "icons"

BUSINESS_UNITS = [
    (
        "India Consumer Services",
        "Trusted home services across Beauty & Wellness and Home Repairs.",
    ),
    (
        "Insta Help",
        "Instant, verified household help.",
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
    (
        "Cleaning & Pest Control",
        "Deep cleaning, room cleaning, pest control",
        "cleaning-pest-control.svg",
        "Cleaning and pest control icon",
    ),
    (
        "AC & Appliance Repair",
        "AC service, appliance and stove repair",
        "ac-appliance-repair.svg",
        "AC and appliance repair icon",
    ),
    (
        "Electrician, Plumber & Carpenter",
        "Repairs and installation work at home",
        "electrician-plumber-carpenter.svg",
        "Electrician, plumber and carpenter icon",
    ),
    (
        "Salon & Spa",
        "Beauty and wellness services at home",
        "salon-spa.svg",
        "Salon and spa icon",
    ),
    (
        "Painting & Water-proofing",
        "Home painting and protection",
        "painting-waterproofing.svg",
        "Painting and waterproofing icon",
    ),
    (
        "Native Smart Products",
        "Water purifiers and smart locks",
        "native-smart-products.svg",
        "Native smart products icon",
    ),
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
                    text-transform:uppercase; font-weight:700; margin-bottom:12px;">Urban Company</div>
        <h2 style="margin:0 0 10px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
          About Us
        </h2>
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
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{tag_html}</div>
      </div>
      <div style="flex:1 1 340px; min-width:340px; min-height:376px; position:relative;">
        <div style="position:absolute; top:0; bottom:0; left:50%; transform:translateX(-50%); aspect-ratio:1 / 1; max-width:100%; border-radius:14px; overflow:hidden;">
          <img src="data:image/jpeg;base64,{encoded}" alt="Home care planning visual"
               style="display:block; width:100%; height:100%; object-fit:contain; border-radius:14px;" />
        </div>
      </div>
    </div>
    """


def _our_business_html() -> str:
    """Render business units with the same card style as the About card."""
    cards = []
    for i, (title, body) in enumerate(BUSINESS_UNITS):
        cards.append(
            "\n".join(
                line.strip()
                for line in textwrap.dedent(
                    f"""
                    <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                                padding:20px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
                      <div style="display:flex; gap:10px; align-items:flex-start;">
                        <span style="flex:0 0 26px; height:26px; border-radius:50%; background:#500C6B;
                                     color:#ffffff; font-size:11px; font-weight:700; display:flex;
                                     align-items:center; justify-content:center;">{i + 1:02d}</span>
                        <div style="font-size:13px; font-weight:700; color:#12212B;">{title}</div>
                      </div>
                      <div style="margin-top:10px; font-size:12px; line-height:1.55; color:#3B4C57;">
                        {body}
                      </div>
                    </div>
                    """
                ).strip().splitlines()
            )
        )
    return (
        '<div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px;">'
        + "".join(cards)
        + "</div>"
    )


def _home_services_html() -> str:
    """Render service groups in an About Us-style card with custom icons."""
    cards = []
    for title, body, icon_file, alt in SERVICE_GROUPS:
        encoded = base64.b64encode((ICON_DIR / icon_file).read_bytes()).decode("ascii")
        cards.append(
            "\n".join(
                line.strip()
                for line in textwrap.dedent(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;
                                padding:16px;">
                      <div style="display:flex; align-items:center; gap:12px;">
                        <div style="width:44px; height:44px; border-radius:12px; background:#EBDFF0;
                                    display:flex; align-items:center; justify-content:center; flex-shrink:0;">
                          <img src="data:image/svg+xml;base64,{encoded}" alt="{alt}"
                               style="width:30px; height:30px; object-fit:contain;" />
                        </div>
                        <div style="font-size:13px; font-weight:700; color:#12212B; line-height:1.35;">
                          {title}
                        </div>
                      </div>
                      <div style="margin-top:10px; font-size:12px; line-height:1.5; color:#52606A;">
                        {body}
                      </div>
                    </div>
                    """
                ).strip().splitlines()
            )
        )
    return "\n".join(
        line.strip()
        for line in textwrap.dedent(
            f"""
            <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                        padding:26px; margin-top:24px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
              <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                          padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">Home Services</div>
              <h2 style="margin:0 0 10px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
                Home Services at your Doorstep
              </h2>
              <p style="margin:0 0 18px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
                Keep track of what you have had done, spot upcoming care needs early, and decide
                what makes sense for your home - without digging through old chats or guessing
                when maintenance is due.
              </p>
              <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px;">
                {''.join(cards)}
              </div>
            </div>
            """
        ).strip().splitlines()
    )


def _at_a_glance_html() -> str:
    """Render headline figures in an About Us-style card."""
    metrics = [
        ("Service rating", "4.8"),
        ("Customers globally", "12M+"),
        ("Repeat share of NTV", f"~{config.REPEAT_NTV_PCT}%"),
    ]
    tiles = []
    for label, value in metrics:
        tiles.append(
            "\n".join(
                line.strip()
                for line in textwrap.dedent(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;
                                padding:18px; text-align:center;">
                      <div style="font-size:2rem; font-weight:700; color:#500C6B; line-height:1.1;">{value}</div>
                      <div style="margin-top:8px; font-size:13px; font-weight:700; color:#12212B;">{label}</div>
                    </div>
                    """
                ).strip().splitlines()
            )
        )
    return "\n".join(
        line.strip()
        for line in textwrap.dedent(
            f"""
            <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                        padding:26px; margin-top:24px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
              <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                          padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">Key Figures</div>
              <h2 style="margin:0 0 18px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
                At a Glance
              </h2>
              <div style="display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px;">
                {''.join(tiles)}
              </div>
            </div>
            """
        ).strip().splitlines()
    )


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption(
        "A technology-driven platform connecting customers with trusted professionals "
        "for home and beauty needs - from cleaning and repairs to salon and spa services."
    )

    st.markdown(_about_html(), unsafe_allow_html=True)

    st.subheader("Our Business")
    st.markdown(_our_business_html(), unsafe_allow_html=True)

    st.markdown(_home_services_html(), unsafe_allow_html=True)

    st.markdown(_at_a_glance_html(), unsafe_allow_html=True)



render()
