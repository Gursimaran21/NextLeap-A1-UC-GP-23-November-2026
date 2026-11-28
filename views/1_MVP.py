"""Home Care Companion MVP page. Respect docs/constraints.md (C1, C2, C3)."""

from __future__ import annotations

import base64
import hashlib
import html
import json
import textwrap
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src import config, export, insta_talk, llm as llm_mod, mvp


LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "HCA-LOGO-6.png"

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


STEPS = [
    "Tell me about your home",
    "Your next 90 days",
    "Insta Talk",
    "After a service",
]

QUICK_PROMPTS = [
    ("AC not cooling", "Decide", "AC not cooling"),
    ("Tap dripping", "Decide", "Tap dripping"),
    ("No need right now", "No action", "No service needed right now"),
    ("Planning cue", "Next 90 days", "Deep cleaning was 9 months ago"),
]

HISTORY_FIELDS = [
    ("last_ac_service", "Last AC servicing"),
    ("last_deep_clean", "Last deep cleaning"),
    ("last_pest_control", "Last pest control"),
    ("last_plumbing_check", "Last plumbing check"),
    ("plumbing_issue", "Plumbing issue"),
    ("upcoming_need", "Upcoming requirement you already know"),
    ("no_need_now", "Services I do not need right now"),
]


def _numbered_history_labels(start: int) -> dict[str, str]:
    """Number history fields continuously after the profile fields."""
    return {key: f"{start + idx}. {label}" for idx, (key, label) in enumerate(HISTORY_FIELDS)}


def _clean_html(value: str) -> str:
    """Strip indentation from small inline-HTML fragments."""
    return "\n".join(line.strip() for line in textwrap.dedent(value).strip().splitlines())


DEMO_TASKS = [
    (
        "Complete combined intake",
        "In Step 1, use the one form: choose home profile answers, set last AC service to '4-6 months', "
        "last deep cleaning to '7-12 months', plumbing issue to 'None', and add 'Bathroom cleaning' "
        "as an upcoming requirement. Save once. Point out that one Reset clears both sections.",
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
        "Show next-cycle care plan",
        "In Step 2, pick a recently completed service and open the six care tabs. Show Watch for, "
        "Note down and Review, one need-recognition cue, a decision question and the source confidence.",
    ),
    (
        "Run guided intake",
        "In Step 2, answer the three guided questions, including 'Possible urgency', and show how "
        "the plan changes. In the guidance tab, point out the source class, freshness and match score.",
    ),
    (
        "Test continuity loop",
        "In Step 4, generate a reflection, build the continuity loop, add its review cue to Step 2, "
        "and download the private summary.",
    ),
    (
        "Record leading indicators",
        "After a guided plan and a continuity loop, save the short local checks on next-need recall, "
        "review-window clarity and confidence. Show that the evidence is leading, not a booking claim.",
    ),
    (
        "Use quick prompts and summary",
        "In Step 3, tap a quick prompt instead of typing. Then open the session summary to see service, "
        "change, timing and review window, with edit and reset controls.",
    ),
    (
        "Test continuity",
        "In Step 4, speak or type 'What should I remember for next time?', download the private "
        "checklist, and submit feedback on usefulness, real need match, route clarity and "
        "revisit intent.",
    ),
]


def _demo_tasks_html() -> str:
    """Render the Insta Talk Demo as an About Us-style card grid."""
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
                        padding:26px; margin-top:24px; margin-bottom:18px;
                        box-shadow:0 16px 36px rgba(15,27,38,0.08);">
              <div style="display:inline-block; background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0;
                          padding:5px 12px; border-radius:999px; font-size:11px; letter-spacing:0.09em;
                          text-transform:uppercase; font-weight:700; margin-bottom:12px;">Insta Talk Demo</div>
              <h2 style="margin:0 0 18px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
                Insta Talk Demo
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
        "mvp_profile_version": 0,
        "mvp_history_version": 0,
        "mvp_plan": [],
        "mvp_plan_summary": "",
        "mvp_own_refresh_notice": False,
        "mvp_review_cues": [],
        "mvp_review_summary": "",
        "mvp_care_category": "AC Service",
        "mvp_care_plan": None,
        "mvp_continuity": None,
        "mvp_intake_edit": False,
        "mvp_step2_ack": False,
        "mvp_edit_guided_notice": False,
        "intake_service": insta_talk.CARE_PLAN_CATEGORIES[0],
        "mvp_leading": {},
        "mvp_reflection_text": "",
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
    cards = []
    for i, label in enumerate(STEPS, start=1):
        if i < step:
            status, badge, bg, border = "Completed", "✅", "#EAF6EE", "#BFE3C8"
            circle_bg, circle_fg, text_fg, badge_bg = "#2E7D46", "#FFFFFF", "#1F5130", "#D6F0DC"
        elif i == step:
            status, badge, bg, border = "In progress", "👉", "#EBDFF0", "#D9C6E0"
            circle_bg, circle_fg, text_fg, badge_bg = "#500C6B", "#FFFFFF", "#500C6B", "#F1E4F5"
        else:
            status, badge, bg, border = "Upcoming", "▫️", "#F8F9FA", "#E3E6E8"
            circle_bg, circle_fg, text_fg, badge_bg = "#E3E6E8", "#7A858D", "#7A858D", "#EEF0F2"
        cards.append(
            _clean_html(
                f"""
                <div style="position:relative; z-index:1; flex:1 1 0; min-width:0;
                            background:{bg}; border:1px solid {border}; border-radius:14px; padding:12px;
                            box-shadow:0 8px 20px rgba(15,27,38,0.05);">
                  <div style="display:flex; align-items:center; justify-content:space-between; gap:6px;">
                    <span style="flex:0 0 26px; height:26px; border-radius:50%; background:{circle_bg};
                                 color:{circle_fg}; font-size:12px; font-weight:700; display:flex;
                                 align-items:center; justify-content:center;">{i}</span>
                    <span style="background:{badge_bg}; color:{text_fg}; border-radius:999px;
                                 padding:3px 8px; font-size:11px; font-weight:700;
                                 white-space:nowrap;">{badge}</span>
                  </div>
                  <div style="margin-top:8px; font-size:10px; letter-spacing:0.08em;
                              text-transform:uppercase; font-weight:700; color:{text_fg};
                              opacity:0.75;">{status}</div>
                  <div style="margin-top:4px; font-size:12px; font-weight:700; line-height:1.35;
                              color:{text_fg};">Step {i}: {label}</div>
                </div>
                """
            )
        )
    line_pct = 0.0 if len(STEPS) <= 1 else (step - 1) / (len(STEPS) - 1) * 75
    st.markdown(
        _clean_html(
            f"""
            <div style="margin-top:4px; padding:2px 0 12px 0;">
              <div style="position:relative;">
                <div style="position:absolute; top:25px; left:12.5%; right:12.5%; height:2px;
                            background:#E3E6E8; z-index:0;"></div>
                <div style="position:absolute; top:25px; left:12.5%; height:2px;
                            width:{line_pct:.1f}%; background:#500C6B; z-index:0;"></div>
                <div style="display:flex; gap:10px; align-items:stretch;">
                  {''.join(cards)}
                </div>
              </div>
            </div>
            """
        ),
        unsafe_allow_html=True,
    )


def _step2_complete() -> bool:
    """Step 2 is done once a plan is built or the user explicitly skips care cues."""
    return (
        bool(st.session_state.get("mvp_care_plan"))
        or bool(st.session_state.get("mvp_plan"))
        or bool(st.session_state.get("mvp_step2_ack"))
    )


def _step3_complete() -> bool:
    """Step 3 is done once Insta Talk has produced an assistant response."""
    return any(
        str(msg.get("role")) == "assistant"
        for msg in st.session_state.get("mvp_chat", [])
        if isinstance(msg, dict)
    )


def _nav_buttons() -> None:
    step = int(st.session_state.mvp_step)
    c1, c2, c3 = st.columns([1, 1, 6])
    with c1:
        if st.button("Back", disabled=step <= 1, width="stretch", type="tertiary"):
            st.session_state.mvp_step = max(1, step - 1)
            st.rerun()
    with c2:
        next_clicked = st.button("Next", disabled=step >= len(STEPS), width="stretch", type="primary")
    if next_clicked:
        if step == 1 and not st.session_state.get("mvp_profile"):
            with c3:
                st.warning("Save home details in Step 1 before continuing.")
        elif step == 2 and not _step2_complete():
            with c3:
                st.warning("Build a guided or own care plan in Step 2 before continuing.")
        elif step == 3 and not _step3_complete():
            with c3:
                st.warning("Complete an Insta Talk turn in Step 3 before continuing.")
        else:
            st.session_state.mvp_step = min(len(STEPS), step + 1)
            st.rerun()


def _reset_home_intake_state() -> None:
    """Clear the combined Step 1 form and its downstream session outputs."""
    st.session_state.mvp_profile = {}
    st.session_state.mvp_history = {}
    st.session_state.mvp_profile_version = int(st.session_state.mvp_profile_version) + 1
    st.session_state.mvp_history_version = int(st.session_state.mvp_history_version) + 1
    st.session_state.mvp_plan = []
    st.session_state.mvp_plan_summary = ""
    st.session_state.mvp_care_plan = None
    st.session_state.mvp_review_cues = []
    st.session_state.mvp_review_summary = ""
    st.session_state.mvp_continuity = None
    st.session_state.mvp_reflection = None
    st.session_state.mvp_reflection_text = ""
    st.session_state.mvp_intake_edit = False
    st.rerun()


def _render_profile() -> dict:
    """Collect profile and household history in one combined Step 1 form."""
    st.subheader("Step 1: Tell me about your home")
    st.markdown(
        '<div style="background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0; '
        'border-radius:10px; padding:12px 14px; font-size:14px; line-height:1.5; margin-bottom:12px;">'
        "We don't ask for personal details. No name, phone, address, flat number, or booking screenshots. "
        "Complete both sections once, then use Save."
        "</div>",
        unsafe_allow_html=True,
    )

    saved_profile = dict(st.session_state.get("mvp_profile", {}))
    saved_history = dict(st.session_state.get("mvp_history", {}))
    profile_version = int(st.session_state.mvp_profile_version)
    history_version = int(st.session_state.mvp_history_version)
    history_labels = _numbered_history_labels(len(mvp.PROFILE_QUESTIONS) + 1)

    def _timing_index(key: str) -> int:
        value = str(saved_history.get(key, "Not sure") or "Not sure")
        return mvp.HISTORY_TIMING_OPTIONS.index(value) if value in mvp.HISTORY_TIMING_OPTIONS else 0

    profile: dict[str, Any] = {}
    history: dict[str, Any] = {}

    with st.form("home_intake_form", clear_on_submit=False):
        st.markdown("### 01 - About your home")
        st.caption("Broad context only. This helps the plan avoid guesses about your space and habits.")
        profile_cols = st.columns(2)
        for idx, q in enumerate(mvp.PROFILE_QUESTIONS, start=1):
            qid = q["id"]
            opts = q["options"]
            default = saved_profile.get(qid)
            widget_key = f"prof_{qid}_{profile_version}"
            label = f"{idx}. {q['question']}"
            with profile_cols[(idx - 1) % 2]:
                if q["type"] == "single":
                    selected = opts.index(default) if default in opts else 0
                    profile[qid] = st.selectbox(label, opts, index=selected, key=widget_key)
                else:
                    default_list = default if isinstance(default, list) else []
                    profile[qid] = st.multiselect(
                        label,
                        opts,
                        default=[d for d in default_list if d in opts],
                        key=widget_key,
                    )

        st.markdown("---")
        st.markdown("### 02 - Household service history")
        st.caption("Relative timing only. Leave as 'Not sure' if you do not remember.")

        history_cols = st.columns(2)
        with history_cols[0]:
            history["last_ac_service"] = st.selectbox(
                history_labels["last_ac_service"],
                mvp.HISTORY_TIMING_OPTIONS,
                index=_timing_index("last_ac_service"),
                key=f"hist_ac_{history_version}",
            )
            history["last_deep_clean"] = st.selectbox(
                history_labels["last_deep_clean"],
                mvp.HISTORY_TIMING_OPTIONS,
                index=_timing_index("last_deep_clean"),
                key=f"hist_deep_{history_version}",
            )
        with history_cols[1]:
            history["last_pest_control"] = st.selectbox(
                history_labels["last_pest_control"],
                mvp.HISTORY_TIMING_OPTIONS,
                index=_timing_index("last_pest_control"),
                key=f"hist_pest_{history_version}",
            )
            history["last_plumbing_check"] = st.selectbox(
                history_labels["last_plumbing_check"],
                mvp.HISTORY_TIMING_OPTIONS,
                index=_timing_index("last_plumbing_check"),
                key=f"hist_plumb_{history_version}",
            )

        issue_col, upcoming_col = st.columns(2)
        with issue_col:
            issue_default = str(saved_history.get("plumbing_issue", "None") or "None")
            history["plumbing_issue"] = st.selectbox(
                history_labels["plumbing_issue"],
                mvp.PLUMBING_ISSUE_OPTIONS,
                index=mvp.PLUMBING_ISSUE_OPTIONS.index(issue_default)
                if issue_default in mvp.PLUMBING_ISSUE_OPTIONS else 0,
                key=f"hist_issue_{history_version}",
            )
        with upcoming_col:
            history["upcoming_need"] = st.text_input(
                history_labels["upcoming_need"],
                value=str(saved_history.get("upcoming_need", "") or ""),
                placeholder="e.g., Bathroom cleaning",
                key=f"hist_upcoming_{history_version}",
            )

        saved_no_need = [str(x) for x in saved_history.get("no_need_now", []) if str(x) in mvp.NO_NEED_OPTIONS]
        history["no_need_now"] = st.multiselect(
            history_labels["no_need_now"],
            mvp.NO_NEED_OPTIONS,
            default=saved_no_need,
            key=f"hist_no_need_{history_version}",
        )

        st.markdown("---")
        save_col, reset_col, _ = st.columns([1, 1, 4])
        with save_col:
            save_all = st.form_submit_button("Save home details", type="primary", width="stretch", wrap=True)
        with reset_col:
            reset_all = st.form_submit_button("Reset", width="stretch", wrap=True)

    if save_all:
        history["upcoming_need"] = str(history.get("upcoming_need", "") or "").strip()
        st.session_state.mvp_profile = profile
        st.session_state.mvp_history = history
        st.session_state.mvp_plan = []
        st.session_state.mvp_plan_summary = ""
        st.session_state.mvp_care_plan = None
        st.session_state.mvp_review_cues = []
        st.session_state.mvp_review_summary = ""
        st.session_state.mvp_continuity = None
        st.success("Home details saved. Step 2 is ready.")
    if reset_all:
        _reset_home_intake_state()

    current_profile = st.session_state.get("mvp_profile", {})
    current_history = st.session_state.get("mvp_history", {})
    if current_profile or current_history:
        snapshot_rows: list[dict[str, str]] = []
        for idx, q in enumerate(mvp.PROFILE_QUESTIONS, start=1):
            value = current_profile.get(q["id"], "")
            snapshot_rows.append({
                "Section": "Profile",
                "Field": f"{idx}. {q['question']}",
                "Value": ", ".join(map(str, value)) if isinstance(value, list) else str(value or "Not provided"),
            })
        for key, _ in HISTORY_FIELDS:
            value = current_history.get(key, "")
            snapshot_rows.append({
                "Section": "Household",
                "Field": history_labels[key],
                "Value": ", ".join(map(str, value)) if isinstance(value, list) else str(value or "Not provided"),
            })
        st.caption("Saved home snapshot for this session")
        header_html = "".join(
            f'<th style="background:#500C6B; color:#FFFFFF; text-align:left; '
            f'padding:8px 10px; font-size:13px;">{col}</th>'
            for col in ("Section", "Field", "Value")
        )
        body_html = "".join(
            "<tr>"
            + "".join(
                f'<td style="padding:8px 10px; border-bottom:1px solid #E6D9EA; '
                f'font-size:13px;">{html.escape(str(row[col]))}</td>'
                for col in ("Section", "Field", "Value")
            )
            + "</tr>"
            for row in snapshot_rows
        )
        st.markdown(
            f'<table style="width:100%; border-collapse:collapse;">'
            f"<thead><tr>{header_html}</tr></thead><tbody>{body_html}</tbody></table>",
            unsafe_allow_html=True,
        )
        snapshot_df = pd.DataFrame(snapshot_rows, columns=["Section", "Field", "Value"])
        snapshot_downloaded = st.download_button(
            "Download home snapshot (CSV)",
            data=snapshot_df.to_csv(index=False).encode("utf-8"),
            file_name=f"home_snapshot_{date.today().isoformat()}.csv",
            mime="text/csv",
            type="primary",
        )
        if snapshot_downloaded:
            st.success("Home snapshot (CSV) is downloaded.")

    return st.session_state.get("mvp_profile", profile)


def _tinted_note(text: str) -> str:
    """Render a light-purple, dark-purple note used for guidance text."""
    return (
        '<div style="background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0; '
        'border-radius:10px; padding:12px 14px; font-size:14px; line-height:1.5;">'
        f'{html.escape(str(text))}</div>'
    )


def _vertical_space(px: int = 16) -> None:
    """Add a small vertical gap between adjacent content blocks."""
    st.markdown(f'<div style="height:{px}px;"></div>', unsafe_allow_html=True)


def _care_pdf_markdown(care: dict) -> str:
    """Render the full on-screen care plan as a structured PDF document."""
    lines = [
        f"Date and Time: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        "",
        f"# Your Next-Cycle Care Plan: {care.get('category', 'your home')}",
        "",
        "## 1. 90-day Plan",
        "",
        "### Watch for",
    ]
    watch = list(care.get("watch_for", [])) or ["Use your own notes for this service."]
    lines.extend(f"{i}.) {item}" for i, item in enumerate(watch, 1))
    lines.extend(["", "### Note down"])
    note = list(care.get("note_down", [])) or ["Use your own notes for this service."]
    lines.extend(f"{i}.) {item}" for i, item in enumerate(note, 1))
    lines.extend(["", "### Review around this time"])
    review = list(care.get("review", []))
    if review:
        lines.extend(
            f"{i}.) {row.get('need', '')}: about {row.get('days', 0)} day(s) - "
            f"{row.get('basis', '') or 'public timing guidance'}"
            for i, row in enumerate(review, 1)
        )
    else:
        lines.append("Use your own notes; no public timing cue is available.")
    lines.extend(["", "## 2. Need Cues"])
    cues = list(care.get("need_cues", []))
    if cues:
        lines.extend(
            f"{i}.) {cue.get('signal', '')} - check {cue.get('category', '')} "
            f"(confidence {float(cue.get('confidence', 0)):.2f}) - {cue.get('basis', 'Public guidance')}"
            for i, cue in enumerate(cues, 1)
        )
    else:
        lines.append("No public cue is available for this service. Use your own notes.")
    lines.extend(["", "## 3. Category Awareness"])
    guide = {row["category"]: row for row in mvp.category_guide()}
    for category in care.get("adjacent_categories", []):
        row = guide.get(category, {})
        lines.extend([
            "",
            f"### {category}",
            f"Covers: {row.get('covers', 'Public guidance')}",
            f"Consider when: {row.get('consider_when', 'Your own observation')}",
        ])
    lines.extend(["", "Category information only. No provider names or availability are shown."])
    lines.extend(["", "## 4. Decision Confidence"])
    questions = list(care.get("decision_questions", [])) or ["What would help you decide calmly?"]
    lines.extend(f"{i}.) {question}" for i, question in enumerate(questions, 1))
    lines.extend(["", "## 5. Route Choice"])
    for item in care.get("route_guide", []):
        lines.extend([
            "",
            f"### {item['route']}",
            f"Fits: {item.get('fits', '')}",
            f"Caution: {item.get('caution', '')}",
        ])
    lines.extend(["", "Decide what fits you. Nothing here contacts anyone."])
    lines.extend(["", "## 6. Why This Guidance?", "", "### Why this guidance:"])
    why_text = str(care.get("why", ""))
    if why_text.lower().startswith("why this guidance:"):
        why_text = why_text.split(":", 1)[1].strip()
    sentences = why_text.split(". ")
    lines.extend(f"{part}." for part in sentences[:-1] if part)
    if sentences[-1]:
        lines.append(sentences[-1])
    lines.extend(["", "", "", "", "", "", "From Urban Company,", "Insta Talk (Next-Cycle Care Plan)"])
    return "\n".join(lines)


def _own_plan_pdf_markdown(plan: list[dict]) -> str:
    """Render the displayed planning cues as a standalone PDF document."""
    lines = [
        f"Date and Time: {datetime.now().strftime('%d %B %Y, %H:%M')}",
        "",
        "# Your Own Care Plan: Planning Cues",
        "",
        "## 1. Planning cues",
        "",
    ]
    if not plan:
        lines.append("No planning cues yet.")
    for i, item in enumerate(plan, 1):
        lines.extend([
            f"{i}.) {item.get('need', 'Cue')}",
            f"Status: {item.get('status', 'Unclear')}",
        ])
        if item.get("due_in_days") is not None:
            lines.append(f"When: about {int(item['due_in_days'])} day(s) from today")
        lines.append(f"Why: {item.get('why', '')}")
        lines.append(f"Basis: {item.get('basis', '')}")
        if item.get("source_url"):
            lines.append(f"Public source: {item['source_url']}")
        lines.append("")
    lines.extend([
        "Planning cues only. No service is required by this plan.",
        "",
        "",
        "From Urban Company,",
        "Insta Talk (Own Care Plan)",
    ])
    return "\n".join(lines)


def _render_plan_details(
    plan: list[dict],
    profile: dict,
    history: dict,
    summary_key: str = "mvp_plan_summary",
) -> None:
    """Render planning cues and the grounded summary for one cue list."""
    plan = list(plan or [])
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
    if st.button("Generate grounded summary", type="primary", key=f"generate_summary_{summary_key}"):
        summary = mvp.summarise_plan(
            profile,
            history,
            plan,
            llm=llm_mod if llm_mod.available() else None,
        )
        st.session_state[summary_key] = summary
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
    if st.session_state.get(summary_key):
        st.markdown("**Grounded summary**")
        st.markdown(_tinted_note(st.session_state[summary_key]), unsafe_allow_html=True)
    else:
        st.caption("Generate a short summary grounded only in the items above.")
    _vertical_space()

    with st.expander("Understand service categories", key=f"understand_categories_{summary_key}"):
        guide_df = pd.DataFrame(mvp.category_guide())
        st.dataframe(guide_df, width="stretch", hide_index=True)
        if summary_key != "mvp_plan_summary":
            st.caption("Category descriptions use public information. No external action is taken from this page.")
    if summary_key != "mvp_plan_summary":
        st.divider()
    if summary_key == "mvp_plan_summary":
        st.divider()
        own_pdf_downloaded = st.download_button(
            "Download own care plan (PDF)",
            data=export.md_to_pdf_bytes(_own_plan_pdf_markdown(plan)),
            file_name="own_care_plan.pdf",
            mime="application/pdf",
            type="primary",
            width="content",
        )
        if own_pdf_downloaded:
            st.success("Own care plan (PDF) is downloaded.")



def _render_care_plan(care: dict, profile: dict, history: dict) -> None:
    """Render the care plan display inside the guided intake expander."""
    if care:
        st.markdown(f"**Care plan for {care['category']}**")
        if care.get("intake"):
            st.caption(
                f"Built from your answers: {care['intake'].get('timing', 'Routine')} · "
                f"{care['intake'].get('change') or 'no extra detail'}"
            )
        if care.get("intake_paused"):
            st.warning(insta_talk.guard(str(care.get("reason", ""))))
        care_tabs = st.tabs([
            "90-day plan",
            "Need cues",
            "Category awareness",
            "Decision confidence",
            "Route choice",
            "Why this guidance?",
        ])
        with care_tabs[0]:
            watch_col, note_col, review_col = st.columns(3)
            with watch_col:
                st.markdown("**Watch for**")
                for item in care.get("watch_for", []):
                    st.markdown(f"- {item}")
            with note_col:
                st.markdown("**Note down**")
                for item in care.get("note_down", []):
                    st.markdown(f"- {item}")
            with review_col:
                st.markdown("**Review around this time**")
                if care.get("review"):
                    for item in care["review"]:
                        badge = insta_talk.coverage_badge(
                            item.get("match_strength", ""), item.get("freshness", ""), item.get("source_url", "")
                        )
                        st.markdown(
                            f"- **{item['need']}**: about {item['days']} day(s) "
                            f"{_coverage_html(badge)}",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"{badge['note']} · {item.get('basis', 'Public timing guidance')}")
                else:
                    st.caption("Use your own notes; no public timing cue is available.")
            st.caption("Review windows are prompts to check your own situation, not service requirements.")
            if care.get("plan_item") and st.button("Add first review cue below", key="care_add_plan", type="primary", width="content"):
                cues = list(st.session_state.get("mvp_review_cues", []))
                cues.append(dict(care["plan_item"]))
                st.session_state.mvp_review_cues = cues
                st.session_state.mvp_review_summary = ""
                st.success("Private cue added below.")
            if st.session_state.get("mvp_review_cues"):
                _render_plan_details(
                    st.session_state.mvp_review_cues,
                    profile,
                    history,
                    summary_key="mvp_review_summary",
                )
            pdf_col, none_col, note_col, _pdf_spacer = st.columns([0.313, 0.18, 0.387, 0.12])
            with pdf_col:
                care_pdf_downloaded = st.download_button(
                    "Download Next-cycle care plan (PDF)",
                    data=export.md_to_pdf_bytes(_care_pdf_markdown(care)),
                    file_name="next_cycle_care_plan.pdf",
                    mime="application/pdf",
                    type="primary",
                    width="content",
                )
            no_need_clicked = False
            with none_col:
                if st.button("No need right now", key="care_no_need", width="content"):
                    st.session_state.mvp_care_plan = None
                    st.session_state.mvp_review_cues = []
                    st.session_state.mvp_review_summary = ""
                    st.session_state.mvp_step2_ack = True
                    no_need_clicked = True
            with note_col:
                if no_need_clicked:
                    st.markdown(
                        '<div style="background:#E8F5E9; color:#1B5E20; border:1px solid #C8E6C9; '
                        'border-radius:8px; padding:8px 12px; font-size:14px; line-height:1.2; '
                        'white-space:nowrap;">Nothing added. You can return if that changes.</div>',
                        unsafe_allow_html=True,
                    )
            if care_pdf_downloaded:
                st.success("Next-cycle care plan (PDF) is downloaded.")
        with care_tabs[1]:
            if care.get("need_cues"):
                for cue in care["need_cues"]:
                    badge = insta_talk.coverage_badge(
                        cue.get("match_strength", care.get("match_strength", "")),
                        cue.get("freshness", care.get("freshness", "")),
                        cue.get("source_url", ""),
                    )
                    st.markdown(
                        f"- **{cue['signal']}** - check {cue['category']} "
                        f"(confidence {float(cue['confidence']):.2f}) {_coverage_html(badge)}",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"{badge['note']} · {cue.get('basis', 'Public guidance')}")
            else:
                st.caption("No public cue is available for this service. Use your own notes.")
        with care_tabs[2]:
            for category in care.get("adjacent_categories", []):
                row = next((x for x in mvp.category_guide() if x["category"] == category), {})
                st.markdown(f"**{category}**")
                st.caption(f"Covers: {row.get('covers', 'Public guidance')}")
                st.caption(f"Consider when: {row.get('consider_when', 'Your own observation')}")
            st.caption("Category information only. No provider names or availability are shown.")
        with care_tabs[3]:
            for question in care.get("decision_questions", []):
                st.markdown(f"- {question}")
        with care_tabs[4]:
            for item in care.get("route_guide", []):
                st.markdown(f"**{item['route']}**")
                st.caption(f"Fits: {item['fits']}")
                st.caption(f"Caution: {item['caution']}")
            st.caption("Decide what fits you. Nothing here contacts anyone.")
        with care_tabs[5]:
            st.markdown(_tinted_note(care.get("why", "")), unsafe_allow_html=True)
            _vertical_space()
            parts = care.get("confidence_parts", {}) or {}
            st.write(
                f"**Confidence:** {float(care.get('confidence', 0)):.2f} "
                f"({parts.get('label', 'not scored')})"
            )
            st.caption(
                f"Source class: {parts.get('source_class', care.get('source_class', 'not recorded'))} · "
                f"Freshness: {parts.get('freshness', 'not recorded')} · "
                f"Match: {parts.get('match_strength', 'not recorded')}"
            )
            if care.get("source_url"):
                st.markdown(f"[Public source]({care['source_url']})")
            st.caption("Your service name stays in this session only.")


def _reset_guided_care_plan() -> None:
    """Clear the built guided plan and return its three inputs to defaults."""
    st.session_state.mvp_care_plan = None
    st.session_state.mvp_review_cues = []
    st.session_state.mvp_review_summary = ""
    st.session_state.mvp_care_category = ""
    st.session_state.mvp_intake_edit = True
    st.session_state.intake_service = insta_talk.CARE_PLAN_CATEGORIES[0]
    st.session_state.intake_note = ""
    st.session_state.intake_mode = "Routine"


def _edit_guided_answers(service: str, change: str, timing: str) -> None:
    """Return to guided intake with the current summary answers prefilled."""
    options = list(insta_talk.CARE_PLAN_CATEGORIES)
    st.session_state.intake_service = service if service in options else options[0]
    st.session_state.intake_note = "" if change == "not added" else change
    st.session_state.intake_mode = timing if timing in ("Routine", "Planned", "Possible urgency") else "Routine"
    st.session_state.mvp_care_category = st.session_state.intake_service
    st.session_state.mvp_intake_edit = True
    st.session_state.mvp_step = 2
    st.session_state.mvp_edit_guided_notice = True


def _build_own_plan(profile: dict, history: dict) -> None:
    """Rebuild the private own-care plan from saved home details."""
    ref = mvp.load_public_reference()
    st.session_state.mvp_plan = mvp.build_plan_from_history(
        profile,
        history,
        reference=ref,
        llm=None,
    )
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


def _render_calendar(profile: dict) -> None:
    st.subheader("Step 2: Your next 90 days")
    st.caption("A private plan built from your household history and public guidance. Planning cues only; no service is required by this plan.")

    care = st.session_state.get("mvp_care_plan")
    history = st.session_state.get("mvp_history", {})

    st.subheader("Choose your home care plan")
    st.caption(
        "Choose a guided next-cycle plan or build your own private plan from home details. "
        "Planning cues only; no bookings, messages, or account access."
    )

    with st.expander("1. Guided intake - 3 quick questions", expanded=bool(st.session_state.get("mvp_intake_edit"))):
        st.markdown("### Next-cycle care plan (guidance only)")
        st.caption(
            "Based only on the service you say you completed and public guidance. "
            "No prices, availability, messages, or account access."
        )

        intake_cat, intake_change, intake_timing = st.columns([1, 2, 1])
        care_options = list(insta_talk.CARE_PLAN_CATEGORIES)
        with intake_cat:
            intake_service = st.selectbox(
                "1. Recently completed service",
                care_options,
                key="intake_service",
            )
        with intake_change:
            intake_note = st.text_input(
                "2. What changed after it? (optional, no personal details)",
                key="intake_note",
                placeholder="e.g., airflow feels weaker",
            )
        with intake_timing:
            intake_mode = st.radio(
                "3. How should we treat it?",
                ["Routine", "Planned", "Possible urgency"],
                key="intake_mode",
            )
        build_col, reset_col, _build_spacer = st.columns([0.205, 0.205, 0.59])
        with build_col:
            if st.button("Build guided care plan", type="primary", width="content"):
                built = insta_talk.guided_intake_plan(
                    {
                        "category": intake_service,
                        "change": intake_note,
                        "timing": intake_mode,
                    },
                    session_hash=st.session_state.mvp_session_hash,
                )
                st.session_state.mvp_care_category = intake_service
                st.session_state.mvp_care_plan = built
                st.session_state.mvp_review_cues = []
                st.session_state.mvp_review_summary = ""
                st.session_state.mvp_intake_edit = True
                _log_leading_indicator("guided_intake_built", "guided_intake", {
                    "category": intake_service,
                    "timing": intake_mode,
                    "paused": bool(built.get("intake_paused")),
                    "confidence": built.get("confidence", 0),
                    "source_class": built.get("source_class", ""),
                    "freshness": built.get("freshness", ""),
                    "match_strength": built.get("match_strength", ""),
                }, quiet=True)
                st.rerun()
        with reset_col:
            st.button(
                "Reset guided care plan",
                key="care_plan_reset",
                width="content",
                on_click=_reset_guided_care_plan,
            )

        _render_care_plan(care, profile, history)

        if care and care.get("intake") and not care.get("intake_paused"):
            _leading_check(
                "guided_intake",
                "guided_intake_check",
                ("li_intake_name", "li_intake_clear", "li_intake_conf"),
                (
                    "Could you name a plausible next need?",
                    "Is the review window clear?",
                    "How confident do you feel now?",
                ),
                ("next_need_recall", "review_window_clarity", "confidence_rating"),
                "Save intake check",
            )


    with st.expander("2. Build your own care plan"):
        st.markdown("### Build your own care plan")
        st.caption(
            "Use your saved home details and public timing guidance to build private planning cues. "
            "No prices, availability, messages, or account access."
        )
        history = st.session_state.get("mvp_history", {})
        build_col, refresh_col, _build_spacer = st.columns([0.205, 0.205, 0.59])
        with build_col:
            if st.button("Build own care plan", type="primary", width="content"):
                _build_own_plan(profile, history)
                st.rerun()
        with refresh_col:
            if st.button("Refresh own care plan", key="own_plan_refresh", width="content"):
                st.session_state.mvp_plan = []
                st.session_state.mvp_plan_summary = ""
                st.session_state.mvp_own_refresh_notice = True
                st.rerun()
        if st.session_state.pop("mvp_own_refresh_notice", False):
            st.success("Own care plan refreshed.")
        with st.container():
            st.text_input(
                "Add an upcoming need you already know (optional)",
                value=st.session_state.get("mvp_custom_need", ""),
                placeholder="e.g., Bathroom cleaning",
                key="mvp_custom_need",
            )
            if st.button("Add as personal note", type="primary", width="content") and st.session_state.get("mvp_custom_need", "").strip():
                custom = st.session_state.mvp_custom_need
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
                st.session_state.mvp_plan_summary = ""
                st.rerun()

        plan = list(st.session_state.get("mvp_plan", []))
        if plan:
            _render_plan_details(plan, profile, history)

    st.markdown(
        '<div style="background:#EBDFF0; color:#500C6B; border:1px solid #D9C6E0; '
        'border-radius:10px; padding:12px 14px; font-size:14px; line-height:1.5; '
        'margin-top:16px; margin-bottom:-24px;">'
        "Save home details in Step 1, then build your plan to see upcoming home-care cues."
        "</div>",
        unsafe_allow_html=True,
    )

    if not plan:
        return



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
    st.toast("Intake check is saved locally.")


def _log_leading_indicator(event: str, flow: str, fields: dict, quiet: bool = False) -> None:
    """Record a session-only leading indicator without any personal text."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_hash": st.session_state.mvp_session_hash,
        "turn": 0,
        "chosen_tool": "insta_talk_leading_indicator",
        "reason": event,
        "flow": flow,
        "user_input_length": 0,
    }
    record.update({k: v for k, v in fields.items() if v not in (None, "", "Select")})
    mvp.log_tool_trace(record)
    st.session_state.mvp_leading[event] = dict(fields)
    if not quiet:
        st.toast("Intake check is saved locally.")


def _reset_leading_check(keys: tuple[str, str, str], event: str) -> None:
    """Reset one quick check's answers and its saved local record."""
    st.session_state[keys[0]] = "Select"
    st.session_state[keys[1]] = "Select"
    st.session_state[keys[2]] = 3
    st.session_state.get("mvp_leading", {}).pop(event, None)


def _leading_check(
    flow: str,
    event: str,
    keys: tuple[str, str, str],
    labels: tuple[str, str, str],
    fields: tuple[str, str, str],
    button_label: str,
) -> None:
    """Render and save a short leading-indicator check for one flow."""
    with st.container(border=True):
        st.markdown("**Quick check**")
        first = st.radio(labels[0], ["Select", "Yes", "Partly", "No"], horizontal=True, key=keys[0])
        second = st.radio(labels[1], ["Select", "Yes", "Partly", "No"], horizontal=True, key=keys[1])
        third = st.slider(labels[2], 1, 5, 3, key=keys[2])
        if button_label == "Save intake check":
            save_col, reset_col, _check_spacer = st.columns([0.188, 0.188, 0.624])
        else:
            save_col = st.container()
        with save_col:
            if st.button(
                button_label,
                key=f"leading_{flow}",
                width="content" if button_label == "Save intake check" else "stretch",
                type="primary" if button_label == "Save intake check" else "secondary",
            ):
                if first == "Select" or second == "Select":
                    st.warning("Choose an answer for both questions before saving.")
                else:
                    _log_leading_indicator(event, flow, {
                        fields[0]: first,
                        fields[1]: second,
                        fields[2]: int(third),
                    }, quiet=button_label == "Save intake check")
                    if button_label == "Save intake check":
                        st.success("Intake check is saved locally.")
        if button_label == "Save intake check":
            with reset_col:
                st.button(
                    "Reset intake check",
                    key=f"leading_{flow}_reset",
                    width="content",
                    on_click=_reset_leading_check,
                    args=(keys, event),
                )


def _coverage_html(badge: dict) -> str:
    """Inline a small public-basis badge next to one cue."""
    return (
        f'<span style="display:inline-block; background:{badge["bg"]}; color:{badge["fg"]}; '
        f'border:1px solid {badge["border"]}; border-radius:999px; padding:2px 8px; '
        f'font-size:10px; font-weight:700; white-space:nowrap;">{badge["label"]}</span>'
    )


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
    if not text and mode not in {"No action", "Next 90 days", "Care plan"}:
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
                if mode in {"No action", "Next 90 days", "Care plan"}:
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

    st.markdown("**Quick prompts**")
    st.caption("Tap an example to send it, or type your own below. Examples are not instructions.")
    prompt_cols = st.columns(len(QUICK_PROMPTS))
    for idx, (label, mode, text) in enumerate(QUICK_PROMPTS):
        with prompt_cols[idx]:
            if st.button(label, key=f"quick_prompt_{idx}", width="stretch"):
                st.session_state.mvp_talk_mode = mode
                _handle_talk(mode, text, profile)

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
                    st.session_state.mvp_plan_summary = ""
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
    cont = st.session_state.get("mvp_continuity")
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

        st.markdown("**Post-service continuity loop**")
        if st.button("Build continuity loop", key="continuity_build", width="stretch"):
            built_cont = insta_talk.continuity_loop(
                ref,
                st.session_state.get("mvp_care_plan"),
                text,
                session_hash=st.session_state.mvp_session_hash,
            )
            st.session_state.mvp_continuity = built_cont
            _log_leading_indicator("continuity_loop_built", "continuity_loop", {
                "completed_service": built_cont.get("completed_service", ""),
                "review_source": "public" if built_cont.get("source_url") else "own notes",
                "confidence": built_cont.get("confidence", 0),
                "coverage": (built_cont.get("plan_item", {}).get("coverage", {}) or {}).get("label", ""),
            }, quiet=True)
            st.rerun()

        cont = st.session_state.get("mvp_continuity")
        if cont:
            st.info(insta_talk.guard(str(cont.get("reason", ""))))
            done_col, watch_col, note_col, review_col = st.columns(4)
            with done_col:
                st.markdown("**Completed service**")
                st.markdown(f"- {cont.get('completed_service', '')}")
            with watch_col:
                st.markdown("**What to monitor**")
                for item in cont.get("monitor", []):
                    st.markdown(f"- {item}")
            with note_col:
                st.markdown("**Private notes**")
                for item in cont.get("private_notes", []):
                    st.markdown(f"- {item}")
            with review_col:
                st.markdown("**Review window**")
                st.markdown(f"- {cont.get('review_window', '')}")
                coverage = (cont.get("plan_item", {}) or {}).get("coverage") or {}
                if coverage:
                    st.markdown(_coverage_html(coverage), unsafe_allow_html=True)
            st.caption(cont.get("why", ""))
            cont_json = {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "completed_service": cont.get("completed_service", ""),
                "monitor": cont.get("monitor", []),
                "private_notes": cont.get("private_notes", []),
                "review_window": cont.get("review_window", ""),
                "followup_question": cont.get("followup_question", ""),
                "confidence": cont.get("confidence", 0),
                "note": "Private summary generated locally. No upload and no external action.",
            }
            cont_col1, cont_col2 = st.columns(2)
            with cont_col1:
                if st.button("Add review cue to Step 2 plan", key="continuity_add_plan", width="stretch"):
                    plan = list(st.session_state.get("mvp_plan", []))
                    plan.append(dict(cont["plan_item"]))
                    st.session_state.mvp_plan = plan
                    st.session_state.mvp_plan_summary = ""
                    st.success("Private review cue added to Step 2.")
            with cont_col2:
                if st.button("Open review window in Step 2", key="continuity_open_step2", width="stretch"):
                    st.session_state.mvp_step = 2
                    st.rerun()
            st.download_button(
                "Download continuity summary (JSON)",
                data=json.dumps(cont_json, indent=2, ensure_ascii=False).encode("utf-8"),
                file_name="continuity_summary.json",
                mime="application/json",
                width="stretch",
            )

    if cont:
        _leading_check(
            "continuity_loop",
            "continuity_loop_check",
            ("li_cont_monitor", "li_cont_clear", "li_cont_useful"),
            (
                "Could you name what to monitor?",
                "Is the review window clear?",
                "How useful is this private summary?",
            ),
            ("monitor_clarity", "review_window_clarity", "usefulness_rating"),
            "Save continuity check",
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

    st.divider()
    _nav_buttons()


render()
