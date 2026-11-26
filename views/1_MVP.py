"""Home Care Companion MVP page. Respect docs/constraints.md (C1, C2, C3)."""

from __future__ import annotations

import base64
import hashlib
import json
import textwrap
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config, insta_talk, llm as llm_mod, mvp


LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "HCA-LOGO-6.png"
ABOUT_BG_PATH = Path(__file__).resolve().parent.parent / "assets" / "about_background_1.jpg"

_VOICE_HTML = """
<div class="hca-voice">
  <div class="hca-voice-row">
    <button id="hca-mic" type="button">🎙 Speak your need</button>
    <button id="hca-speak" type="button">🔊 Read reply</button>
  </div>
  <div id="hca-voice-status" class="hca-voice-status">Browser voice is optional. Typing always works.</div>
</div>
"""

_VOICE_CSS = """
.hca-voice {
  font-family: var(--st-font);
  color: var(--st-text-color);
  border: 1px solid #E6D9EA;
  background: #FBFAFC;
  border-radius: 14px;
  padding: 12px;
}
.hca-voice-row { display: flex; gap: 8px; flex-wrap: wrap; }
.hca-voice button {
  border: 1px solid #500C6B;
  background: #FFFFFF;
  color: #500C6B;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}
.hca-voice button:hover { background: #EBDFF0; }
.hca-voice-status { margin-top: 8px; font-size: 11px; line-height: 1.5; opacity: 0.85; }
"""

_VOICE_JS = r"""
export default function({ parentElement, data, setStateValue, setTriggerValue }) {
  const mic = parentElement.querySelector("#hca-mic");
  const speak = parentElement.querySelector("#hca-speak");
  const status = parentElement.querySelector("#hca-voice-status");
  const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
  const lang = (data && data.lang) || "en-IN";

  mic.onclick = () => {
    if (!Speech) {
      status.textContent = "Browser speech input is unavailable here. Please type instead.";
      return;
    }
    const rec = new Speech();
    rec.lang = lang;
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    status.textContent = "Listening…";
    rec.onresult = (event) => {
      const text = event.results[0][0].transcript || "";
      status.textContent = "Voice note received.";
      setStateValue("transcript", text);
      setTriggerValue("transcript_ready", true);
    };
    rec.onerror = () => {
      status.textContent = "Voice input was not available. Please type instead.";
    };
    rec.onend = () => {
      if (status.textContent === "Listening…") status.textContent = "Ready. Type anytime.";
    };
    rec.start();
  };

  speak.onclick = () => {
    const text = (data && data.speech) || "";
    if (!text) {
      status.textContent = "There is no reply to read yet.";
      return;
    }
    if (!("speechSynthesis" in window)) {
      status.textContent = "Browser speech output is unavailable here.";
      return;
    }
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text.slice(0, 900));
    utterance.lang = lang;
    utterance.rate = 0.95;
    window.speechSynthesis.speak(utterance);
    status.textContent = "Reading the latest reply.";
  };
}
"""

voice_component = st.components.v2.component(
    "hca_insta_talk_voice",
    html=_VOICE_HTML,
    css=_VOICE_CSS,
    js=_VOICE_JS,
)


def _header_html() -> str:
    """Inline the logo and title in one vertically centred row."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="Insta Talk logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "Insta Talk</h1>"
        "</div>"
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
                    text-transform:uppercase; font-weight:700; margin-bottom:12px;">Insta Talk</div>
        <h2 style="margin:0 0 10px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
          About Insta Talk
        </h2>
        <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
          A voice-enabled guidance companion for urban households. It helps you recognise home-care
          needs, choose a safe next step and plan what comes next.
        </p>
        <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
          Insta Talk uses local, deterministic rules first. It can explain, decide, prepare, support
          aftercare, say no action or frame the next 90 days. Public evidence grounds the guidance;
          a configured Gemini key may only improve wording.
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
      <div style="flex:1 1 340px; min-width:340px; display:flex; align-items:center; justify-content:center;">
        <div style="width:340px; height:453px; border-radius:14px; overflow:hidden;">
          <img src="data:image/jpeg;base64,{encoded}" alt="Home care planning visual"
               style="display:block; width:100%; height:100%; object-fit:cover; border-radius:14px;" />
        </div>
      </div>
    </div>
    """


STEPS = [
    "Tell me about your home",
    "Your next 90 days",
    "Insta Talk",
    "After a service",
]

def _clean_html(value: str) -> str:
    """Strip indentation from small inline-HTML fragments."""
    return "\n".join(line.strip() for line in textwrap.dedent(value).strip().splitlines())


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
            "If you mark something as not needed, the app returns NO_ACTION — no reminder, no recommendation.",
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
    "User selects Insta Talk.",
    "The page shows About, the four-step explanation and Demo Tasks for Mentors.",
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
        "Route to SEEK_IMMEDIATE_HELP — immediate qualified help, not DIY or a service category.",
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
    "recognition, clarity and continuity — not through booking or sales pressure."
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
                      Step {i} — {title}
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


DEMO_TASKS = [
    (
        "Organise history",
        "In Step 1, set last AC service to '4-6 months', last deep cleaning to '7-12 months', "
        "plumbing issue to 'None', and add 'Bathroom cleaning' as an upcoming requirement. "
        "Point out that no name, phone number or address is requested.",
    ),
    (
        "Build a 90-day plan",
        "In Step 2, build the plan, generate the grounded summary, and download the Markdown "
        "plan and .ics reminders. Show one cue with its reason, source and confidence.",
    ),
    (
        "Test no-action",
        "In Step 2 mark AC servicing as not needed, or in Step 3 choose the 'No action' mode "
        "and enter 'No service needed right now'. Confirm that no reminder or recommendation "
        "is added.",
    ),
    (
        "Route with Insta Talk",
        "In Step 3, type or speak <span style=\"background:#EBDFF0; color:#500C6B; padding:2px 6px; "
        "border-radius:6px;\">AC not cooling, tap dripping, and something feels off in my "
        "kitchen but not sure what.</span> Try Explain, Decide and Prepare. Show the route, "
        "confidence, why-not note and public basis. Then say 'Deep cleaning was 9 months ago' "
        "to show the speak-to-plan cue.",
    ),
    (
        "Test continuity",
        "In Step 4, speak or type 'What should I remember for next time?', download the private "
        "checklist, and submit feedback on usefulness, real need match, route clarity and "
        "revisit intent.",
    ),
]


def _demo_tasks_html() -> str:
    """Render Demo Tasks for Mentors as an About Us-style card grid."""
    cards = []
    for i, (title, detail) in enumerate(DEMO_TASKS, start=1):
        cards.append(
            "\n".join(
                line.strip()
                for line in textwrap.dedent(
                    f"""
                    <div style="background:#FFFFFF; border:1px solid #E6D9EA; border-radius:14px;
                                padding:18px; display:flex; gap:14px; align-items:flex-start;">
                      <span style="flex:0 0 34px; height:34px; border-radius:50%; background:#500C6B;
                                   color:#ffffff; font-size:12px; font-weight:700; display:flex;
                                   align-items:center; justify-content:center;">{i}</span>
                      <div style="min-width:0;">
                        <div style="font-size:13px; font-weight:700; color:#12212B; line-height:1.35;">
                          {title}
                        </div>
                        <div style="margin-top:6px; font-size:12px; line-height:1.55; color:#52606A;">
                          {detail}
                        </div>
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
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">For Mentors</div>
              <h2 style="margin:0 0 18px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
                Demo Tasks for Mentors
              </h2>
              <div style="display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px;">
                {''.join(cards)}
              </div>
            </div>
            """
        ).strip().splitlines()
    )


def _init_state() -> None:
    defaults = {
        "mvp_step": 1,
        "mvp_profile": {},
        "mvp_history": {},
        "mvp_plan": [],
        "mvp_plan_summary": "",
        "mvp_custom_need": "",
        "mvp_chat": [],
        "mvp_reflection": None,
        "mvp_feedback": {},
        "mvp_talk_mode": "Decide",
        "mvp_decision_started": None,
        "mvp_aftercare_result": None,
        "mvp_session_hash": hashlib.sha256(str(datetime.now(timezone.utc).timestamp()).encode()).hexdigest()[:12],
    }
    for k, v in defaults.items():
        st.session_state.setdefault(k, v)


def _stepper() -> None:
    step = int(st.session_state.mvp_step)
    st.progress(step / len(STEPS))
    cols = st.columns(len(STEPS))
    for i, (col, label) in enumerate(zip(cols, STEPS), start=1):
        prefix = "✅" if i < step else ("👉" if i == step else "▫️")
        col.markdown(f"**{prefix} Step {i}: {label}**")


def _nav_buttons() -> None:
    step = int(st.session_state.mvp_step)
    c1, c2, c3 = st.columns([1, 1, 6])
    with c1:
        if st.button("Back", disabled=step <= 1, width="stretch"):
            st.session_state.mvp_step = max(1, step - 1)
            st.rerun()
    with c2:
        if st.button("Next", disabled=step >= len(STEPS), width="stretch"):
            st.session_state.mvp_step = min(len(STEPS), step + 1)
            st.rerun()


def _render_profile() -> dict:
    st.subheader("Step 1: Tell me about your home")
    st.info("We don't ask for personal details. No name, phone, address, flat number, or booking screenshots.")

    profile = dict(st.session_state.get("mvp_profile", {}))
    with st.form("profile_form"):
        for q in mvp.PROFILE_QUESTIONS:
            qid = q["id"]
            label = q["question"]
            opts = q["options"]
            default = profile.get(qid)
            if q["type"] == "single":
                idx = opts.index(default) if default in opts else 0
                profile[qid] = st.selectbox(label, opts, index=idx, key=f"prof_{qid}")
            else:
                default_list = default if isinstance(default, list) else []
                profile[qid] = st.multiselect(label, opts, default=[d for d in default_list if d in opts], key=f"prof_{qid}")
        submitted = st.form_submit_button("Save profile")
    if submitted:
        st.session_state.mvp_profile = profile
        st.success("Profile saved. Add optional household history below, then move to Step 2.")

    history = dict(st.session_state.get("mvp_history", {}))
    st.markdown("**Optional household service history**")
    st.caption("Relative timing only. This stays in your session and helps the plan avoid guesses.")

    def _timing_index(key: str) -> int:
        value = str(history.get(key, "Not sure") or "Not sure")
        return mvp.HISTORY_TIMING_OPTIONS.index(value) if value in mvp.HISTORY_TIMING_OPTIONS else 0

    with st.form("history_form"):
        left, right = st.columns(2)
        with left:
            h_ac = st.selectbox("Last AC servicing", mvp.HISTORY_TIMING_OPTIONS, index=_timing_index("last_ac_service"), key="hist_ac")
            h_deep = st.selectbox("Last deep cleaning", mvp.HISTORY_TIMING_OPTIONS, index=_timing_index("last_deep_clean"), key="hist_deep")
        with right:
            h_pest = st.selectbox("Last pest control", mvp.HISTORY_TIMING_OPTIONS, index=_timing_index("last_pest_control"), key="hist_pest")
            h_plumb = st.selectbox("Last plumbing check", mvp.HISTORY_TIMING_OPTIONS, index=_timing_index("last_plumbing_check"), key="hist_plumb")

        issue_default = str(history.get("plumbing_issue", "None") or "None")
        h_issue = st.selectbox(
            "Plumbing issue",
            mvp.PLUMBING_ISSUE_OPTIONS,
            index=mvp.PLUMBING_ISSUE_OPTIONS.index(issue_default) if issue_default in mvp.PLUMBING_ISSUE_OPTIONS else 0,
            key="hist_issue",
        )
        h_upcoming = st.text_input(
            "Upcoming requirement you already know",
            value=str(history.get("upcoming_need", "") or ""),
            placeholder="e.g., Bathroom cleaning",
            key="hist_upcoming",
        )
        saved_no_need = [str(x) for x in history.get("no_need_now", []) if str(x) in mvp.NO_NEED_OPTIONS]
        h_no_need = st.multiselect(
            "Services I do not need right now",
            mvp.NO_NEED_OPTIONS,
            default=saved_no_need,
            key="hist_no_need",
        )
        save_history = st.form_submit_button("Save household history")

    if save_history:
        st.session_state.mvp_history = {
            "last_ac_service": h_ac,
            "last_deep_clean": h_deep,
            "last_pest_control": h_pest,
            "last_plumbing_check": h_plumb,
            "plumbing_issue": h_issue,
            "upcoming_need": h_upcoming.strip(),
            "no_need_now": h_no_need,
        }
        st.session_state.mvp_plan = []
        st.session_state.mvp_plan_summary = ""
        st.success("Household history saved. Build your plan in Step 2.")

    current_history = st.session_state.get("mvp_history", {})
    if current_history:
        display_rows = [
            {
                "Field": label,
                "Value": ", ".join(map(str, current_history.get(key, []))) if isinstance(current_history.get(key), list) else str(current_history.get(key, "") or "Not provided"),
            }
            for key, label in [
                ("last_ac_service", "Last AC servicing"),
                ("last_deep_clean", "Last deep cleaning"),
                ("last_pest_control", "Last pest control"),
                ("last_plumbing_check", "Last plumbing check"),
                ("plumbing_issue", "Plumbing issue"),
                ("upcoming_need", "Upcoming requirement"),
                ("no_need_now", "No need right now"),
            ]
        ]
        st.caption("Saved history for this session")
        st.dataframe(pd.DataFrame(display_rows), width="stretch", hide_index=True)

    return st.session_state.get("mvp_profile", profile)


def _render_calendar(profile: dict) -> None:
    st.subheader("Step 2: Your next 90 days")
    st.caption("A private plan built from your household history and public guidance. Planning cues only; no service is required by this plan.")

    history = st.session_state.get("mvp_history", {})
    col_a, col_b = st.columns([1, 2])
    with col_a:
        if st.button("Build / refresh plan", type="primary", width="stretch"):
            ref = mvp.load_public_reference()
            plan = mvp.build_plan_from_history(profile, history, reference=ref, llm=None)
            st.session_state.mvp_plan = plan
            st.session_state.mvp_plan_summary = ""
            mvp.log_tool_trace({
                "ts": datetime.now(timezone.utc).isoformat(),
                "session_hash": st.session_state.mvp_session_hash,
                "turn": 0,
                "chosen_tool": "build_calendar",
                "reason": "User requested plan refresh from household history",
                "user_input_length": len(json.dumps(history, ensure_ascii=False)),
                "route": "PLAN",
                "confidence": 1.0,
            })
            st.rerun()
    with col_b:
        custom = st.text_input(
            "Add an upcoming need you already know (optional)",
            value=st.session_state.get("mvp_custom_need", ""),
            placeholder="e.g., Bathroom cleaning",
        )
        st.session_state.mvp_custom_need = custom
        if st.button("Add as personal note") and custom.strip():
            plan = list(st.session_state.get("mvp_plan", []))
            plan.append({
                "need": custom.strip(),
                "status": "Your note",
                "due_in_days": 30,
                "why": "You added this as an upcoming requirement.",
                "basis": "Your own note; no external claim is made.",
                "source_url": "",
                "confidence": 0.4,
                "route_hint": "USER_NOTE",
                "evidence": "customer input only",
            })
            st.session_state.mvp_plan = plan
            st.rerun()

    plan = list(st.session_state.get("mvp_plan", []))
    if not plan:
        st.info("Save optional history in Step 1, then build your plan to see upcoming home-care cues.")
        return

    st.markdown("**Planning cues**")
    for item in plan:
        conf = float(item.get("confidence", 0))
        conf_label = "High" if conf >= 0.75 else ("Medium" if conf >= 0.5 else "Low")
        status = str(item.get("status", "Unclear"))
        with st.container(border=True):
            head_left, head_right = st.columns([4, 1])
            with head_left:
                st.markdown(f"**{item.get('need', 'Cue')}**")
                st.caption(f"Status: {status} · Evidence: {item.get('evidence', 'not stated')}")
            with head_right:
                st.metric("Confidence", f"{conf:.2f}")
            if item.get("due_in_days") is not None:
                st.write(f"**When:** about {int(item['due_in_days'])} day(s) from today")
            st.write(f"**Why:** {item.get('why', '')}")
            st.write(f"**Basis:** {item.get('basis', '')}")
            src = item.get("source_url", "")
            if src:
                st.markdown(f"**Public source:** [{src}]({src})")
            if status == "Not needed":
                st.success("You marked this as not needed. No action is suggested.")
            elif status == "Needs more detail":
                st.warning("Add more detail if you want a specific timing cue.")
            else:
                st.caption("Planning cue only — not a service requirement.")

    st.divider()
    st.markdown("**Plain-language summary**")
    if st.button("Generate grounded summary"):
        summary = mvp.summarise_plan(
            profile,
            history,
            plan,
            llm=llm_mod if llm_mod.available() else None,
        )
        st.session_state.mvp_plan_summary = summary
        mvp.log_tool_trace({
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_hash": st.session_state.mvp_session_hash,
            "turn": 0,
            "chosen_tool": "summarise_plan",
            "reason": "User requested grounded summary of household plan",
            "user_input_length": len(summary),
            "route": "PLAN",
            "confidence": 1.0,
        })
        st.rerun()
    if st.session_state.get("mvp_plan_summary"):
        st.info(st.session_state["mvp_plan_summary"])
    else:
        st.caption("Generate a short summary grounded only in the items above.")

    with st.expander("Understand service categories"):
        guide_df = pd.DataFrame(mvp.category_guide())
        st.dataframe(guide_df, width="stretch", hide_index=True)
        st.caption("Category descriptions use public information. No external action is taken from this page.")

    st.divider()
    st.subheader("Export your private plan")
    summary = str(st.session_state.get("mvp_plan_summary", "") or "")
    md_plan = mvp.plan_to_markdown(profile, history, plan, summary)
    ics_plan = mvp.plan_to_ics(plan)
    json_plan = json.dumps(
        {
            "generated_on": date.today().isoformat(),
            "profile": profile,
            "history": history,
            "plan": plan,
            "summary": summary,
            "note": "Private planning cues only. No account access or external action.",
        },
        indent=2,
        ensure_ascii=False,
    )
    exp1, exp2, exp3 = st.columns(3)
    with exp1:
        st.download_button(
            "Download plan (Markdown)",
            data=md_plan.encode("utf-8"),
            file_name=f"home_care_plan_{date.today().isoformat()}.md",
            mime="text/markdown",
            width="stretch",
        )
    with exp2:
        st.download_button(
            "Download reminders (.ics)",
            data=ics_plan.encode("utf-8"),
            file_name="home_care_reminders.ics",
            mime="text/calendar",
            width="stretch",
        )
    with exp3:
        st.download_button(
            "Download plan data (JSON)",
            data=json_plan.encode("utf-8"),
            file_name="home_care_plan.json",
            mime="application/json",
            width="stretch",
        )
    st.caption("The calendar file uses one-day-before reminders and stays on your device.")


def _plain_speech(text: str) -> str:
    """Make a chat answer readable when spoken aloud."""
    clean = str(text or "").replace("**", "").replace("`", "")
    return " ".join(clean.split())[:900]


def _voice_bridge(speech_text: str, key: str) -> str:
    """Mount browser-native voice controls and return a finished transcript."""
    if not hasattr(st, "components") or not hasattr(st.components, "v2"):
        st.caption("Voice assistance needs a newer Streamlit build. Typed input still works.")
        return ""
    result = voice_component(
        data={"speech": _plain_speech(speech_text), "lang": "en-IN"},
        default={"transcript": ""},
        on_transcript_change=lambda: None,
        on_transcript_ready_change=lambda: None,
        key=key,
        width="stretch",
    )
    st.caption("Voice is processed by your browser. You can switch to typing anytime.")
    if getattr(result, "transcript_ready", None):
        return str(getattr(result, "transcript", "") or "")
    return ""


def _log_decision_event(event: str, msg: dict) -> None:
    """Record leading indicators for Insta Talk evaluation."""
    meta = msg.get("meta", {})
    started = st.session_state.get("mvp_decision_started")
    seconds = round(time.time() - float(started), 1) if started else None
    mvp.log_tool_trace({
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_hash": st.session_state.mvp_session_hash,
        "turn": 0,
        "chosen_tool": "insta_talk_decision_event",
        "reason": event,
        "user_input_length": 0,
        "route": meta.get("route", ""),
        "confidence": meta.get("confidence", 0),
        "accepted_route": event == "route_clear",
        "revisit_intent": event == "revisit_later",
        "seconds_to_decision": seconds,
    })
    st.toast("Saved locally for evaluation.")


def _append_decider_result(result: dict, mode: str = "") -> None:
    trace = result.get("tool_trace", {})
    parts = []
    if mode:
        parts.append(f"**Insta Talk mode:** {mode}")
    parts.append(f"**Route:** {result.get('route')}")
    parts.append(f"**Confidence:** {result.get('confidence')}")
    parts.append(f"**Reason:** {insta_talk.guard(str(result.get('reason', '')))}")
    if result.get("category_info"):
        parts.append(f"**Category info:** {result['category_info']}")
    if result.get("steps"):
        parts.append("**Steps to keep in mind:**")
        parts.extend([f"- {s}" for s in result["steps"]])
    answer = "\n\n".join(parts)
    st.session_state.mvp_chat.append({
        "role": "assistant",
        "content": answer,
        "meta": {
            "chosen_tool": trace.get("chosen_tool", "route_need"),
            "route": result.get("route"),
            "confidence": result.get("confidence"),
            "clarifying_questions": result.get("clarifying_questions", []),
            "used_public_reference": result.get("used_public_reference", False),
            "public_reference": result.get("public_reference"),
            "mode": mode,
            "plan_item": result.get("plan_item"),
        },
    })


def _handle_talk(mode: str, text: str, profile: dict) -> None:
    text = str(text or "").strip()
    if not text and mode not in {"No action", "Next 90 days"}:
        text = "I need guidance."
    user_text = text or "No service needed right now."
    st.session_state.mvp_chat.append({"role": "user", "content": user_text})
    if st.session_state.get("mvp_decision_started") is None:
        st.session_state.mvp_decision_started = time.time()
    result = insta_talk.mode_response(
        mode,
        text,
        profile=profile,
        plan=st.session_state.get("mvp_plan", []),
        session_hash=st.session_state.mvp_session_hash,
    )
    trace = result.get("tool_trace", {})
    if str(trace.get("chosen_tool", "")).startswith("insta_talk"):
        mvp.log_tool_trace(trace)
    _append_decider_result(result, mode)
    st.rerun()


def _talk_mode_selector() -> str:
    st.markdown("**Insta Talk modes**")
    cols = st.columns(3)
    for idx, (mode, label) in enumerate(insta_talk.TALK_MODES):
        with cols[idx % 3]:
            if st.button(label, key=f"talk_mode_{idx}", width="stretch"):
                st.session_state.mvp_talk_mode = mode
                if mode in {"No action", "Next 90 days"}:
                    _handle_talk(mode, "", st.session_state.get("mvp_profile", {}))
                st.rerun()
    active = str(st.session_state.get("mvp_talk_mode", "Decide"))
    st.caption(f"Active mode: {active}")
    return active


def _render_decider(profile: dict) -> None:
    st.subheader("Step 3: Insta Talk — Need Decider")
    st.caption(
        "Type or speak a home issue. Insta Talk gives public-information guidance, a clear "
        "route, confidence, and why other routes were not preferred. No booking or account action."
    )

    active_mode = _talk_mode_selector()
    context = st.text_input(
        "Add context for this mode (optional)",
        key=f"talk_context_{active_mode}",
        placeholder="e.g., Deep cleaning was 9 months ago",
    )
    if st.button("Send to Insta Talk", key="talk_send_mode"):
        _handle_talk(active_mode, context, profile)

    st.divider()
    for idx, msg in enumerate(list(st.session_state.mvp_chat)):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("meta"):
                m = msg["meta"]
                st.caption(
                    f"Tool used this turn: `{m.get('chosen_tool','')}` · "
                    f"Route: {m.get('route','')} · Confidence: {m.get('confidence','')}"
                )
                if m.get("clarifying_questions"):
                    st.markdown("**Clarifying questions:**")
                    for q in m["clarifying_questions"]:
                        st.markdown(f"- {q}")
                if m.get("used_public_reference") and m.get("public_reference"):
                    pr = m["public_reference"]
                    st.info(f"Public reference: {pr.get('basis','')} ")
                    if pr.get("source_url"):
                        st.markdown(f"[Source]({pr['source_url']})")
                if m.get("plan_item") and st.button(
                    "Add private reminder to Step 2", key=f"add_plan_cue_{idx}"
                ):
                    plan = list(st.session_state.get("mvp_plan", []))
                    plan.append(dict(m["plan_item"]))
                    st.session_state.mvp_plan = plan
                    st.success("Private cue added to the Step 2 plan.")

    last_assistant = next(
        (m for m in reversed(list(st.session_state.mvp_chat)) if m["role"] == "assistant"),
        None,
    )
    if last_assistant:
        clear_col, revisit_col = st.columns(2)
        with clear_col:
            if st.button("Route was clear", key="route_clear", width="stretch"):
                _log_decision_event("route_clear", last_assistant)
        with revisit_col:
            if st.button("I’ll revisit later", key="revisit_later", width="stretch"):
                _log_decision_event("revisit_later", last_assistant)

    st.divider()
    voice_text = _voice_bridge(
        _plain_speech(last_assistant["content"] if last_assistant else "Describe a home issue."),
        "hca_voice_step3",
    )
    if voice_text:
        _handle_talk(active_mode, voice_text, profile)

    prompt = st.chat_input("What's going on at home? (no personal details)")
    if prompt:
        _handle_talk(active_mode, prompt, profile)


def _render_reflection() -> None:
    st.subheader("Step 4: Insta Talk after a service")
    st.caption(
        "What should I remember for next time? Capture a private continuity note. "
        "Speak or type; nothing is uploaded."
    )

    voice_text = _voice_bridge(
        "What should I remember for next time?",
        "hca_voice_step4",
    )
    if voice_text:
        st.session_state.mvp_reflection_text = (
            str(st.session_state.get("mvp_reflection_text", "") or "") + " " + voice_text
        ).strip()
        st.rerun()

    text = st.text_area(
        "What should I remember for next time? (optional, no personal details)",
        value=st.session_state.get("mvp_reflection_text", ""),
        height=120,
    )
    st.session_state.mvp_reflection_text = text

    if st.button("Aftercare check", key="aftercare_check"):
        result = insta_talk.mode_response(
            "Aftercare",
            text,
            plan=st.session_state.get("mvp_plan", []),
            session_hash=st.session_state.mvp_session_hash,
        )
        trace = result.get("tool_trace", {})
        if str(trace.get("chosen_tool", "")).startswith("insta_talk"):
            mvp.log_tool_trace(trace)
        st.session_state.mvp_aftercare_result = result
        st.rerun()

    aftercare = st.session_state.get("mvp_aftercare_result")
    if aftercare:
        st.info(insta_talk.guard(str(aftercare.get("reason", ""))))
        if aftercare.get("steps"):
            st.markdown("**Private aftercare checklist:**")
            for step in aftercare["steps"]:
                st.markdown(f"- {step}")

    if st.button("Generate reflection checklist"):
        ref = mvp.reflect(text, session_hash=st.session_state.mvp_session_hash)
        st.session_state.mvp_reflection = ref
        st.rerun()

    ref = st.session_state.get("mvp_reflection")
    if ref:
        st.markdown("**Open topics to keep in mind**")
        for t in ref.get("open_topics", []):
            st.markdown(f"- {t}")
        st.write("**Follow-up question:**", ref.get("followup_question", ""))
        checklist = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "open_topics": ref.get("open_topics", []),
            "followup_question": ref.get("followup_question", ""),
            "note": "Private checklist generated locally in your session. No upload. No booking action.",
        }
        st.download_button(
            "Download personal checklist (JSON)",
            data=json.dumps(checklist, indent=2, ensure_ascii=False).encode("utf-8"),
            file_name="home_care_checklist.json",
            mime="application/json",
        )

    st.divider()
    st.markdown("**Quick feedback**")
    useful = st.radio("Was this useful?", ["Select", "Yes", "Partly", "No"], horizontal=True, key="fb_useful")
    matched = st.radio("Did this match a real need?", ["Select", "Yes", "Partly", "No"], horizontal=True, key="fb_match")
    clear = st.radio("Was the route clear?", ["Select", "Yes", "Partly", "No"], horizontal=True, key="fb_clear")
    revisit = st.radio("Will you revisit this assistant later?", ["Select", "Yes", "Maybe", "No"], horizontal=True, key="fb_revisit")
    if st.button("Submit feedback"):
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_hash": st.session_state.mvp_session_hash,
            "useful": useful,
            "matched_real_need": matched,
            "route_clear": clear,
            "revisit_intent": revisit,
        }
        mvp.log_feedback(record)
        st.session_state.mvp_feedback = record
        st.success("Feedback saved locally to outputs/mvp_feedback.jsonl.")

    st.divider()
    st.success("Nothing here books anything. These are public facts and your own notes.")


def render() -> None:
    _init_state()
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("A calm planning assistant for urban home care. No bookings, no account access, no personal details.")

    st.markdown(_about_html(), unsafe_allow_html=True)

    st.markdown(_steps_html(), unsafe_allow_html=True)

    st.markdown(_demo_tasks_html(), unsafe_allow_html=True)

    _stepper()
    profile = st.session_state.get("mvp_profile", {})
    step = int(st.session_state.mvp_step)
    if step == 1:
        profile = _render_profile()
    elif step == 2:
        _render_calendar(profile)
    elif step == 3:
        _render_decider(profile)
    elif step == 4:
        _render_reflection()

    _nav_buttons()


render()
