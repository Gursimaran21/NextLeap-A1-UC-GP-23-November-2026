"""MVP testing page. Respect docs/constraints.md."""

from __future__ import annotations

import base64

import pandas as pd
import streamlit as st

from src import config


LOGO_PATH = config.ROOT / "assets" / "HCA-LOGO-12.png"


def _header_html() -> str:
    """Inline the HCA-LOGO-12 mark beside the page title."""
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return (
        '<div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">'
        f'<img src="data:image/png;base64,{encoded}" alt="Home Care Assistant logo" '
        'style="width:44px; height:44px; object-fit:contain; flex-shrink:0;" />'
        '<h1 style="margin:0; line-height:1.2; font-size:2.25rem;">'
        "MVP Testing</h1>"
        "</div>"
    )


def render() -> None:
    st.markdown(_header_html(), unsafe_allow_html=True)
    st.caption("At least three real tasks with users from the target segment. No PII, no account actions.")

    st.subheader("Testing methodology (R6)")
    st.markdown(
        """
        - Participants: >=3 users from the target segment; no names or contact details recorded.
        - Method: assign real tasks, observe interaction, note confusion and time-on-task, then ask about usefulness and relevance.
        - Evidence: task outcome, tool trace from `outputs/tool_trace.jsonl`, and feedback from `outputs/mvp_feedback.jsonl`.
        - Safety: confirm no PII was collected and no booking/messaging/account action was attempted.
        """
    )

    st.subheader("3-user test plan")
    tests = [
        {
            "user": "R_T1 (placeholder)",
            "task": "Build a 90-day home-care plan from profile and identify one upcoming need.",
            "expected_tool_trace": "build_calendar -> public_reference_lookup/show_public_info",
            "observed": "[Fill after test]",
            "change_next_iteration": "[Fill after test]",
        },
        {
            "user": "R_T2 (placeholder)",
            "task": "Use Need Decider for a vague issue and a clear AC issue.",
            "expected_tool_trace": "ask_clarifying_question for vague; route_need/public_reference_lookup for clear AC issue",
            "observed": "[Fill after test]",
            "change_next_iteration": "[Fill after test]",
        },
        {
            "user": "R_T3 (placeholder)",
            "task": "Complete post-service reflection and download the private checklist.",
            "expected_tool_trace": "capture_reflection -> local checklist download; no upload",
            "observed": "[Fill after test]",
            "change_next_iteration": "[Fill after test]",
        },
    ]
    st.dataframe(pd.DataFrame(tests), width="stretch", hide_index=True)

    st.subheader("Test cards")
    for t in tests:
        with st.container(border=True):
            st.markdown(f"**{t['user']}**")
            st.write("**Task:**", t["task"])
            st.write("**Expected tool trace:**", t["expected_tool_trace"])
            st.write("**Observed:**", t["observed"])
            st.write("**Change for next iteration:**", t["change_next_iteration"])

    st.subheader("Iteration 2 task cards (unrun)")
    iteration_2 = [
        {
            "user": "R_T4 (placeholder)",
            "task": "Use guided intake with a routine answer, then with Possible urgency.",
            "expected_evidence": "guided_intake_plan route CARE_PLAN for routine; SEEK_IMMEDIATE_HELP for urgency",
            "observed": "[Fill after test]",
        },
        {
            "user": "R_T5 (placeholder)",
            "task": "Explain why one care-plan item has higher confidence than another using source class, freshness and match.",
            "expected_evidence": "confidence_v2 breakdown shown in the guidance tab; no overclaim",
            "observed": "[Fill after test]",
        },
        {
            "user": "R_T6 (placeholder)",
            "task": "Generate a reflection, build the continuity loop, add its review cue to Step 2 and download the summary.",
            "expected_evidence": "capture_reflection -> continuity_loop -> local JSON; no upload",
            "observed": "[Fill after test]",
        },
        {
            "user": "R_T7 (placeholder)",
            "task": "Save the guided-intake and continuity leading checks, then explain what they can and cannot show.",
            "expected_evidence": "insta_talk_leading_indicator for guided_intake_check and continuity_loop_check; leading indicators only",
            "observed": "[Fill after test]",
        },
        {
            "user": "R_T8 (placeholder)",
            "task": "Use a quick prompt in Step 3, then open the session summary, edit the answers and reset guided notes.",
            "expected_evidence": "quick_prompt_0 -> chat turn; session summary shows service, change, timing and review window",
            "observed": "[Fill after test]",
        },
    ]
    for t in iteration_2:
        with st.container(border=True):
            st.markdown(f"**{t['user']}**")
            st.write("**Task:**", t["task"])
            st.write("**Expected evidence:**", t["expected_evidence"])
            st.write("**Observed:**", t["observed"])

    st.subheader("Synthesis (pending real tests)")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**What worked well**")
        st.markdown("- [Fill after tests]")
        st.markdown("**User feedback on usefulness / relevance**")
        st.markdown("- [Fill after tests]")
    with c2:
        st.markdown("**What did not work / issues identified**")
        st.markdown("- [Fill after tests]")
        st.markdown("**Changes proposed for next iteration**")
        st.markdown("- [Fill after tests]")

    st.subheader("Evidence capture checklist")
    st.markdown(
        """
        - Record task success/failure and time-on-task.
        - Capture the tool trace from `outputs/tool_trace.jsonl`.
        - Note confusion, trust concerns, and false positives/negatives.
        - Confirm no PII was collected; no booking/account actions were attempted.
        - Do not fill placeholders with invented observations.
        """
    )


render()
