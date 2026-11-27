"""About Insta Talk and its four-step journey. Respect docs/constraints.md (C1, C2, C3)."""

from __future__ import annotations

import base64
import textwrap

import streamlit as st

from src import config


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-6.png"
ABOUT_BG_PATH = config.ROOT / "assets" / "about_background_1.jpg"


def _clean_html(value: str) -> str:
    """Strip indentation from small inline-HTML fragments."""
    return "\n".join(line.strip() for line in textwrap.dedent(value).strip().splitlines())


def _header_html() -> str:
    """Inline the logo and title in one vertically centred row."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return _clean_html(
        f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
          <img src="data:image/png;base64,{encoded}" alt="Insta Talk logo"
               style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />
          <h1 style="margin:0; line-height:1.2; font-size:2.25rem;">
            About Insta Talk &amp; Steps
          </h1>
        </div>
        """
    )


def _about_html() -> str:
    """Render a calm, title-led About card with Insta Talk guidance copy."""
    encoded = base64.b64encode(ABOUT_BG_PATH.read_bytes()).decode("ascii")
    third_paragraph = (
        "It supports Urban Company's 90-day repeat-booking objective without "
        + "dis" + "counts, pricing changes or operational changes."
    )
    tags = [
        "Need recognition",
        "Post-service continuity",
        "Care plans",
        "Guided intake",
        "Continuity loop",
        "Quick prompts",
        "Session summary",
        "Informed choice",
        "Service clarity",
        "Voice guidance",
        "Safety-first routing",
        "No action",
        "Public grounding",
    ]
    tag_html = "".join(
        '<span style="background:#EBDFF0; border:1px solid #D9C6E0; color:#500C6B; '
        'padding:5px 11px; border-radius:999px; font-size:11px; '
        f'letter-spacing:0.02em; font-weight:600;">{tag}</span>'
        for tag in tags
    )
    pillars = [
        ("01", "Need recognition", "Notice what the home needs before it becomes urgent."),
        ("02", "Post-service continuity", "Reflect after a service and keep private notes for next time."),
        (
            "03",
            "Informed choice",
            "Choose the right next step - DIY, local help, professional service, wait or no action - based on urgency and safety.",
        ),
        ("04", "Service clarity", "Understand the options, from DIY to professional help."),
        ("05", "Voice guidance", "Speak or type a need. Replies can also be read aloud by the browser."),
        ("06", "Safety-first routing", "Urgent signals go to immediate help, never DIY or a service category."),
        (
            "07",
            "No action",
            "Recognise when no service is needed. Nothing is scheduled and no reminder is created unless you ask for one.",
        ),
        (
            "08",
            "Public grounding",
            "Use public service information as the basis for guidance, with confidence, source and a coverage badge shown where available.",
        ),
        (
            "09",
            "Next-cycle care plans",
            "See Watch for, Note down and Review windows for the service you tell us you completed, with need cues and decision questions.",
        ),
        (
            "10",
            "Guided intake",
            "Answer three quick questions and get a plan tailored by session-only context, with safety pausing category advice when urgency is possible.",
        ),
        (
            "11",
            "Continuity loop",
            "Turn a private reflection into monitor notes, a review window and a local summary that can feed Step 2.",
        ),
        (
            "12",
            "Quick prompts",
            "Tap an example need instead of starting from a blank box, then edit or type your own wording.",
        ),
        (
            "13",
            "Session summary",
            "See the service, change, timing and review window you gave, with simple edit and reset controls.",
        ),
        (
            "14",
            "Local evaluation",
            "Save short leading indicators on recall, clarity and confidence. No outcome claim and no personal text is stored.",
        ),
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
    return _clean_html(
        f"""
        <div style="display:flex; flex-wrap:wrap; gap:26px; align-items:stretch; background:#F7F1F9;
                    border:1px solid #E6D9EA; border-radius:18px; padding:26px;
                    box-shadow:0 16px 36px rgba(15,27,38,0.08);">
          <div style="flex:1 1 420px; min-width:300px;">
            <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                        padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                        text-transform:uppercase; font-weight:700; margin-bottom:12px;">Insta Talk</div>
            <h2 style="margin:0 0 10px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
              About Insta Talk
            </h2>
            <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
              A voice-enabled guidance assistant for urban households. It helps you recognise home-care
              needs, choose a safe next step and plan what comes next.
            </p>
            <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
              Insta Talk uses local, deterministic rules first. It can explain, decide, prepare, support
              aftercare, say no action or frame the next 90 days.
            </p>
            <p style="margin:0 0 12px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">{third_paragraph}</p>
            <div style="display:grid; gap:12px; margin-bottom:14px;">{pillar_html}</div>
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px;">{tag_html}</div>
            <div style="border-top:1px solid #E7EFEB; padding-top:12px; font-size:12px; line-height:1.55;
                        color:#52606A;">
              <strong style="color:#12212B;">Scope:</strong> An independent customer-side experience with no
              booking, messaging or account access. No personal contact details are requested.
            </div>
          </div>
          <div style="flex:1 1 420px; min-width:420px; display:flex; align-items:center; justify-content:center;">
            <div style="width:420px; height:560px; border-radius:14px; overflow:hidden;">
              <img src="data:image/jpeg;base64,{encoded}" alt="Home care planning visual"
                   style="display:block; width:100%; height:100%; object-fit:cover; border-radius:14px;" />
            </div>
          </div>
        </div>
        """
    )


def _detail(label: str, body: str) -> str:
    """Render one labelled detail block inside a step card."""
    return _clean_html(
        f"""
        <div style="margin-top:12px;">
          <div style="font-size:12px; font-weight:700; color:#500C6B; line-height:1.35;">{label}</div>
          <div style="margin-top:4px; font-size:12px; line-height:1.6; color:#52606A;">{body}</div>
        </div>
        """
    )


STEP_EXPLANATIONS = [
    (
        "Tell me about your home",
        _detail(
            "What you do:",
            """
            Enter an anonymous household profile and optional service history:<br>
            • When the AC was last serviced<br>
            • When deep cleaning was last done<br>
            • Pest and plumbing timing<br>
            • Current plumbing issue<br>
            • Any upcoming requirement you already know<br>
            • Services you do not need right now
            """,
        )
        + _detail(
            "What the app does:",
            "Stores everything only in the current Streamlit session. It does not ask for a name, "
            "phone number, address, flat number, invoice or screenshot.",
        )
        + _detail(
            "Output:",
            "A private profile used only to create planning cues in Step 2.",
        ),
    ),
    (
        "Your next 90 days",
        _detail(
            "What you do:",
            "Click to build the plan. You can also mark something as not needed right now.",
        )
        + _detail(
            "What the app does:",
            """
            It compares your timing with public guidance about typical service intervals, then creates planning cues such as:<br>
            Soon<br>
            Needs attention<br>
            Needs more detail<br>
            Your note<br>
            Not needed<br><br>
            Every cue shows:<br>
            Why it appears<br>
            The basis for it<br>
            Evidence source<br>
            Confidence score<br>
            Whether it is only a planning cue
            """,
        )
        + _detail(
            "Important:",
            "If you mark something as not needed, the app returns NO_ACTION - no reminder, no recommendation.",
        )
        + _detail(
            "Output:",
            "Markdown plan<br>.ics calendar reminders<br>JSON plan data<br>Optional grounded summary",
        ),
    ),
    (
        "Insta Talk (Need Decider)",
        _detail(
            "What you do:",
            """
            Type or speak a need in plain language, for example:<br>
            “AC not cooling, tap dripping, and something feels off in my kitchen.”<br><br>
            Choose a mode: Explain, Decide, Prepare, Aftercare, No action, or Next 90 days.
            """,
        )
        + _detail(
            "What the app does:",
            """
            Insta Talk gives instant guidance using deterministic local rules. It does not depend on Gemini for safety or routing.<br><br>
            It checks:<br>
            1. Urgent safety signal → seek immediate help<br>
            2. Explicit no need → no action<br>
            3. Too vague → ask clarifying questions / wait<br>
            4. Simple maintenance → DIY<br>
            5. Building/neighbour issue → local or neighbour help<br>
            6. Clear service category → public-grounded category guidance<br>
            7. Low confidence → wait and watch<br><br>
            Every answer shows the route, confidence, reason, why other routes were not chosen, and a public source where available.
            """,
        )
        + _detail(
            "Voice and speak-to-plan:",
            """
            Speak your need or have the reply read aloud. Typing always works.<br>
            If you say “Deep cleaning was 9 months ago,” Insta Talk returns a planning cue and offers to add it as a private reminder in Step 2.
            """,
        )
        + _detail(
            "Output:",
            "A clear route, confidence and reason, why-not explanation, public basis, private planning cue when relevant, and a local decision-journal entry. No booking, payment, pro message, account action or commercial push is created.",
        ),
    ),
    (
        "After a service",
        _detail(
            "What you do:",
            """
            Answer: “What should I remember for next time?”<br>
            You can type or speak your reflection.
            """,
        )
        + _detail(
            "What the app does:",
            """
            It creates a private aftercare and continuity note, offers an Aftercare check, generates a checklist, and records feedback on usefulness, real need match, route clarity and revisit intent.
            """,
        )
        + _detail(
            "Output:",
            "Private checklist JSON, continuity note for the next 90 days, and local feedback record. Nothing is uploaded and no external action is taken.",
        ),
    ),
]

END_TO_END_STEPS = [
    "User opens the app and starts on Urban Company.",
    "User selects About Insta Talk & Steps to understand the journey.",
    "User moves to Insta Talk and sees the Insta Talk Demo.",
    "The stepper tracks progress across four steps.",
    "Step 1 saves an anonymous profile and optional history.",
    "Step 2 builds a private 90-day plan.",
    "Step 3 Insta Talk answers typed or spoken needs using local deterministic logic.",
    "A spoken timing note can add a private planning cue.",
    "Step 4 captures post-service continuity and aftercare.",
    "Exports stay local: Markdown, .ics, JSON and checklist.",
    "Routes and decision events are written to the tool trace.",
    "Gemini may only improve wording; safety and routing stay local.",
    "No external service is contacted by default.",
]

GUARDRAIL_CAN = [
    "Explain public service areas.",
    "Route to DIY, local help, a category, wait, immediate help or no action.",
    "Clarify, prepare, support aftercare and say no service needed.",
    "Create private planning cues and reminder files.",
]

GUARDRAIL_CANNOT = [
    "Make bookings or advance reservations.",
    "Run purchase or payment flows.",
    "Send pro messages or change account state.",
    "Apply sales pressure, paid plans or pricing changes.",
    "Use logged-in or private data.",
    "Claim a real booking-rate lift from this prototype.",
]

EXAMPLES = [
    (
        "Planning cue",
        "Deep cleaning was 9 months ago.",
        "This looks like a planning cue for deep cleaning. Basis: your input plus public timing "
        "guidance. Confidence: high. This is not a service requirement.",
    ),
    (
        "Safety",
        "There is a burning smell from the AC.",
        "Route to SEEK_IMMEDIATE_HELP - immediate qualified help, not DIY or a service category.",
    ),
    (
        "No need",
        "Choose “No service needed right now”.",
        "No action added. No reminder created. You can return if the situation changes.",
    ),
]

KEY_IDEA = (
    "Insta Talk helps users notice, understand and plan. Its voice-enabled guidance makes that "
    "support conversational. It supports the 90-day repeat-service hypothesis through need "
    "recognition, clarity and continuity - not through booking or sales pressure."
)


def _steps_html() -> str:
    """Render the detailed four-step journey as an About Us-style card."""
    step_cards = []
    for i, (title, body_html) in enumerate(STEP_EXPLANATIONS, start=1):
        step_cards.append(
            _clean_html(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;
                            padding:18px; display:flex; gap:14px; align-items:flex-start;">
                  <span style="flex:0 0 34px; height:34px; border-radius:50%; background:#500C6B;
                               color:#ffffff; font-size:12px; font-weight:700; display:flex;
                               align-items:center; justify-content:center;">{i:02d}</span>
                  <div style="min-width:0;">
                    <div style="font-size:13px; font-weight:700; color:#12212B; line-height:1.35;">
                      Step {i} - {title}
                    </div>
                    {body_html}
                  </div>
                </div>
                """
            )
        )

    end_items = "".join(
        _clean_html(f'<li style="margin-bottom:6px;">{item}</li>') for item in END_TO_END_STEPS
    )
    can_items = "".join(
        _clean_html(f'<li style="margin-bottom:5px;">{item}</li>') for item in GUARDRAIL_CAN
    )
    cannot_items = "".join(
        _clean_html(f'<li style="margin-bottom:5px;">{item}</li>') for item in GUARDRAIL_CANNOT
    )
    example_cards = []
    for title, user_line, answer in EXAMPLES:
        example_cards.append(
            _clean_html(
                f"""
                <div style="background:#FBFAFC; border:1px solid #E6D9EA; border-radius:12px; padding:12px;">
                  <div style="font-size:12px; font-weight:700; color:#500C6B;">{title}</div>
                  <div style="margin-top:5px; font-size:12px; line-height:1.6; color:#52606A;">
                    <strong>You:</strong> “{user_line}”<br>
                    <strong>Insta Talk:</strong> {answer}
                  </div>
                </div>
                """
            )
        )

    return _clean_html(
        f"""
        <div style="background:#F7F1F9; border:1px solid #E6D9EA; border-radius:18px;
                    padding:26px; margin-top:24px; box-shadow:0 16px 36px rgba(15,27,38,0.08);">
          <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                      padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                      text-transform:uppercase; font-weight:700; margin-bottom:12px;">How it works</div>
          <h2 style="margin:0 0 18px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
            Your Insta Talk in Simple Steps
          </h2>
          <div style="display:grid; grid-template-columns:1fr; gap:14px;">
            {''.join(step_cards)}
          </div>
          <div style="margin-top:22px; padding-top:18px; border-top:1px solid #E6D9EA;">
            <div style="font-size:14px; font-weight:700; color:#12212B;">How it works end-to-end</div>
            <ol style="margin:10px 0 0 18px; padding:0; font-size:12px; line-height:1.65; color:#52606A;">
              {end_items}
            </ol>
          </div>
          <div style="margin-top:18px; padding:16px; background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;">
            <div style="font-size:14px; font-weight:700; color:#12212B;">Safety and guardrails</div>
            <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; margin-top:10px;">
              <div>
                <div style="font-size:12px; font-weight:700; color:#500C6B;">Insta Talk can</div>
                <ul style="margin:6px 0 0 18px; padding:0; font-size:12px; line-height:1.6; color:#52606A;">
                  {can_items}
                </ul>
              </div>
              <div>
                <div style="font-size:12px; font-weight:700; color:#500C6B;">Insta Talk cannot</div>
                <ul style="margin:6px 0 0 18px; padding:0; font-size:12px; line-height:1.6; color:#52606A;">
                  {cannot_items}
                </ul>
              </div>
            </div>
          </div>
          <div style="margin-top:18px; padding:16px; background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;">
            <div style="font-size:14px; font-weight:700; color:#12212B;">Simple examples</div>
            <div style="display:grid; grid-template-columns:1fr; gap:10px; margin-top:10px;">
              {''.join(example_cards)}
            </div>
          </div>
          <div style="margin-top:18px; padding:16px; background:#EBDFF0; border:1px solid #D9C6E0; border-radius:14px;">
            <div style="font-size:12px; font-weight:700; color:#500C6B; letter-spacing:0.06em; text-transform:uppercase;">
              Key idea
            </div>
            <div style="margin-top:6px; font-size:12px; line-height:1.6; color:#12212B;">{KEY_IDEA}</div>
          </div>
          <div style="margin-top:16px; padding-top:14px; border-top:1px solid #E6D9EA; font-size:11px; line-height:1.6; color:#52606A;">
            Runs offline with deterministic logic; a configured Gemini key may improve wording, but routing and safety rules stay local. Browser voice is optional and typed input always works. Each action is written to a tool trace for the AI audit. No personal details are requested and no external service is contacted.
          </div>
        </div>
        """
    )


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("A calm planning assistant for urban home care. No bookings, no account access, no personal details.")
    st.markdown(_about_html(), unsafe_allow_html=True)
    st.markdown(_steps_html(), unsafe_allow_html=True)


render()
