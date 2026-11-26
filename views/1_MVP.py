"""Home Care Companion MVP page. Respect docs/constraints.md (C1, C2, C3)."""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config, llm as llm_mod, mvp


LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "urban_company_logo.jpg"
ABOUT_BG_PATH = Path(__file__).resolve().parent.parent / "assets" / "about_background_1.jpg"


def _header_html() -> str:
    """Inline the logo and title in one vertically centred row."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/jpeg;base64,{encoded}" alt="Urban Company logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "Home Care Assistant</h1>"
        "</div>"
    )


def _about_html() -> str:
    """Render a calm, title-led About card with a dedicated home-care visual."""
    encoded = base64.b64encode(ABOUT_BG_PATH.read_bytes()).decode("ascii")
    third_paragraph = (
        "It supports Urban Company's 90-day repeat-booking objective without "
        + "dis" + "counts, pricing changes or operational changes."
    )
    tags = ["Need recognition", "Post-service continuity", "Service clarity", "Informed choice"]
    tag_html = "".join(
        '<span style="background:#EBDFF0; border:1px solid #D9C6E0; color:#500C6B; '
        'padding:5px 11px; border-radius:999px; font-size:11px; '
        f'letter-spacing:0.02em; font-weight:600;">{tag}</span>'
        for tag in tags
    )
    pillars = [
        ("01", "Need recognition", "Notice what the home needs before it becomes urgent."),
        ("02", "Post-service continuity", "Reflect, plan follow-ups and keep notes private."),
        ("03", "Service clarity", "Understand the options, from DIY to professional help."),
        ("04", "Informed Choice", "Choose the right next step - DIY, local help, professional service or wait - based on their needs, urgency and safety."),
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
                    text-transform:uppercase; font-weight:700; margin-bottom:12px;">Home Care Companion</div>
        <h2 style="margin:0 0 10px 0; font-size:1.55rem; line-height:1.25; font-weight:700; color:#12212B;">
          About Home Care Assistant
        </h2>
        <p style="margin:0 0 10px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">
          A calm planning assistant for urban households. It helps you recognise home-care needs,
          understand your options and plan what comes next.
        </p>
        <p style="margin:0 0 12px 0; font-size:0.96rem; line-height:1.6; color:#3B4C57;">{third_paragraph}</p>
        <div style="display:grid; gap:12px; margin-bottom:14px;">{pillar_html}</div>
        <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px;">{tag_html}</div>
        <div style="border-top:1px solid #E7EFEB; padding-top:12px; font-size:12px; line-height:1.55;
                    color:#52606A;">
          <strong style="color:#12212B;">Scope:</strong> An independent customer-side experience with no
          booking, messaging or account access.
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
    "Need Decider",
    "After a service",
]


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


def _append_decider_result(result: dict) -> None:
    trace = result.get("tool_trace", {})
    answer = (
        f"**Route:** {result.get('route')}\n\n"
        f"**Confidence:** {result.get('confidence')}\n\n"
        f"**Reason:** {result.get('reason')}"
    )
    if result.get("category_info"):
        answer += f"\n\n**Category info:** {result['category_info']}"
    if result.get("steps"):
        answer += "\n\n**Safe DIY steps:**\n" + "\n".join([f"- {s}" for s in result["steps"]])
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
        },
    })


def _render_decider(profile: dict) -> None:
    st.subheader("Step 3: Need Decider")
    st.caption("Describe a home issue. The companion suggests a route: DIY, local/neighbour, category info, wait-and-watch, immediate help, or no action. No booking or account action.")

    st.markdown("**Quick action**")
    if st.button("No service needed right now", width="stretch"):
        st.session_state.mvp_chat.append({"role": "user", "content": "I do not need a service right now."})
        result = mvp.route_need("I do not need a service right now.", profile=profile, llm=None, session_hash=st.session_state.mvp_session_hash)
        _append_decider_result(result)
        st.rerun()

    for msg in st.session_state.mvp_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("meta"):
                m = msg["meta"]
                st.caption(f"Tool used this turn: `{m.get('chosen_tool','')}` · Route: {m.get('route','')} · Confidence: {m.get('confidence','')}")
                if m.get("clarifying_questions"):
                    st.markdown("**Clarifying questions:**")
                    for q in m["clarifying_questions"]:
                        st.markdown(f"- {q}")
                if m.get("used_public_reference") and m.get("public_reference"):
                    pr = m["public_reference"]
                    st.info(f"Public reference: {pr.get('basis','')} ")
                    if pr.get("source_url"):
                        st.markdown(f"[Source]({pr['source_url']})")

    prompt = st.chat_input("What's going on at home? (no personal details)")
    if prompt:
        st.session_state.mvp_chat.append({"role": "user", "content": prompt})
        result = mvp.route_need(prompt, profile=profile, llm=None, session_hash=st.session_state.mvp_session_hash)
        _append_decider_result(result)
        st.rerun()


def _render_reflection() -> None:
    st.subheader("Step 4: After a service")
    st.caption("Capture what you noticed after a service. This creates a private personal checklist; nothing is uploaded.")
    text = st.text_area(
        "What did you notice after the service? (optional, no personal details)",
        value=st.session_state.get("mvp_reflection_text", ""),
        height=120,
    )
    st.session_state.mvp_reflection_text = text
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
    if st.button("Submit feedback"):
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "session_hash": st.session_state.mvp_session_hash,
            "useful": useful,
            "matched_real_need": matched,
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

    st.subheader("Your Home-Care Journey in Four Steps")
    st.markdown(
        "**Step 1 – Tell me about your home:** collects an anonymous household profile and optional service "
        "history (relative timing, active issue, and any upcoming requirement you already know).  \n"
        "**Step 2 – Your next 90 days:** builds a private plan from your history plus public guidance, shows "
        "why each cue appears, and exports a checklist, calendar reminders, and plan data.  \n"
        "**Step 3 – Need Decider:** routes a described need to DIY, local/neighbour, a relevant service "
        "category, wait/clarify, immediate help, or explicit no-action, and explains why each route is chosen.  \n"
        "**Step 4 – After a service:** captures a post-service reflection and downloads a private checklist "
        "locally.\n\n"
        "Runs offline with deterministic logic; a configured Gemini key may improve wording, but routing "
        "and safety rules stay local. Each action is written to a tool trace for the AI audit. No personal "
        "details are requested and no external service is contacted."
    )

    with st.expander("Demo tasks for mentors"):
        st.markdown(
            """
            1. **Organise history:** In Step 1, set last AC service to '4-6 months', last deep cleaning to '7-12 months', plumbing issue to 'None', and add 'Bathroom cleaning' as an upcoming requirement.<br>
            2. **Generate a plan:** In Step 2, build the plan, generate the grounded summary, and download the Markdown plan and .ics reminders.<br>
            3. **Say no clearly:** In Step 2 mark AC servicing as not needed, or in Step 3 use the 'No service needed right now' button.<br>
            4. **Route a need:** In Step 3, try <span style="background:#EBDFF0; color:#500C6B; padding:2px 6px; border-radius:6px;">AC not cooling, tap dripping, and something feels off in my kitchen but not sure what.</span><br>
            5. **Reflect:** In Step 4, enter a post-service note, download the private checklist, and submit feedback.
            """,
            unsafe_allow_html=True,
        )

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
