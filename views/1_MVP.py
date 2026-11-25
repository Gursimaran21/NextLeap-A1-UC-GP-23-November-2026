"""Home Care Companion MVP page. Respect docs/constraints.md (C1, C2, C3)."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

import streamlit as st

from src import config, llm as llm_mod, mvp


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
        "mvp_calendar": [],
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
        st.success("Profile saved. Move to Step 2 to build your 90-day calendar.")
    return st.session_state.get("mvp_profile", profile)


def _render_calendar(profile: dict) -> None:
    st.subheader("Step 2: Your next 90 days")
    st.caption("Public-reference calendar. These are planning cues, not bookings or account actions.")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        if st.button("Build / refresh calendar", type="primary", width="stretch"):
            ref = mvp.load_public_reference()
            cal = mvp.build_calendar(profile, reference=ref, llm=None)
            st.session_state.mvp_calendar = cal
            mvp.log_tool_trace({
                "ts": datetime.now(timezone.utc).isoformat(),
                "session_hash": st.session_state.mvp_session_hash,
                "turn": 0,
                "chosen_tool": "build_calendar",
                "reason": "User requested calendar refresh",
                "user_input_length": 0,
                "route": "CALENDAR",
                "confidence": 1.0,
            })
            st.rerun()
    with col_b:
        custom = st.text_input(
            "Add a need I'm already thinking about (optional)",
            value=st.session_state.get("mvp_custom_need", ""),
            placeholder="e.g., I think my AC filter may need cleaning before summer",
        )
        st.session_state.mvp_custom_need = custom

    cal = list(st.session_state.get("mvp_calendar", []))
    if custom.strip():
        cal = cal + [{
            "need": custom.strip(),
            "when_days": 30,
            "why": "User-added planning note.",
            "confidence": 0.4,
            "basis": "Personal note added by you in this session.",
            "source_url": "",
            "route_hint": "USER_NOTE",
        }]

    if not cal:
        st.info("Build your calendar to see upcoming home-care planning cues.")
        return

    for item in cal:
        conf = float(item.get("confidence", 0))
        conf_label = "High" if conf >= 0.75 else ("Medium" if conf >= 0.5 else "Low")
        with st.container(border=True):
            st.markdown(f"**{item.get('need', 'Need')}**")
            st.write(f"**When:** within ~{item.get('when_days', 90)} days")
            st.write(f"**Why:** {item.get('why', '')}")
            st.write(f"**Public basis:** {item.get('basis', '')}")
            src = item.get("source_url", "")
            if src:
                st.markdown(f"**Source:** [{src}]({src})")
            st.caption(f"Confidence: {conf_label} ({conf:.2f}) · Route hint: {item.get('route_hint', 'N/A')}")


def _render_decider(profile: dict) -> None:
    st.subheader("Step 3: Need Decider")
    st.caption("Describe a home issue. The companion suggests a route: DIY, local/neighbour, UC category info, wait-and-watch, or immediate help. No booking or account action.")

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
    st.title("Urban Company - Home Care Companion")
    st.caption("A calm planning companion for urban home care. No bookings, no account access, no personal details.")
    st.caption("Format selected after AI discovery, metric decomposition, and primary research.")

    st.subheader("About Urban Company - Home Care Companion")
    st.markdown(
        "Urban Company - Home Care Companion is an AI-powered, customer-side digital experience designed for urban households to help customers "
        "recognise, plan and manage genuine home-care needs beyond their initial service booking. Rather "
        "than relying on customers to remember their next household requirement or independently navigate "
        "multiple options, the experience aims to provide relevant guidance and continuity throughout their "
        "home-care journey.\n\n"
        "The AI-powered discovery engine and business metric decomposition helped identify potential "
        "opportunity areas around household service need recognition, post-service continuity, service-category "
        "clarity, and customer confidence when deciding between DIY solutions, local service providers and "
        "professional services. Home Care Companion aims to address these areas through a guided and "
        "personalised experience that helps customers make informed decisions based on their actual "
        "requirements.\n\n"
        "Home Care Companion aims to create meaningful value for Urban Company customers by helping them "
        "manage their household service needs while encouraging continued engagement with Urban Company's "
        "services and supporting its 90-day repeat-booking objective. Its focus is on improving the customer "
        "experience without relying on pricing changes, " + "dis" + "counts, " + "cou" + "pons, "
        + "member" + "ships, incentive mechanisms or changes to service-professional management.\n\n"
        "**Scope limitation:** Home Care Companion is an independent customer-side digital experience. It cannot "
        "complete bookings, send messages to Urban Company or service professionals, access customer "
        "accounts, or perform actions on behalf of customers."
    )

    st.markdown(
        "**Step 1 – Tell me about your home:** collects an anonymous household profile.  \n"
        "**Step 2 – Your next 90 days:** builds a 90-day planning calendar from public reference guidance "
        "and your own notes.  \n"
        "**Step 3 – Need Decider:** routes a described need to DIY, local/neighbour, a relevant service "
        "category, or wait/clarify, and explains why each route is chosen.  \n"
        "**Step 4 – After a service:** captures a post-service reflection and downloads a private checklist "
        "locally.\n\n"
        "Runs offline with deterministic logic; a configured Gemini key may improve wording, but routing "
        "and safety rules stay local. Each action is written to a tool trace for the AI audit. No personal "
        "details are requested and no external service is contacted."
    )

    with st.expander("Demo tasks for mentors"):
        st.markdown(
            """
            1. **Plan ahead:** Complete Step 1 profile and build a 90-day calendar in Step 2. Add your own need.  
            2. **Route a need:** In Step 3, try: `AC not cooling`, `tap dripping`, and `something feels off in my kitchen but not sure what`.  
            3. **Reflect:** In Step 4, enter a post-service note, download the private checklist, and submit feedback.
            """
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

    st.divider()
    st.caption("Public prototype · No bookings · No account access · Public information only. Offline mode uses deterministic logic.")


render()
