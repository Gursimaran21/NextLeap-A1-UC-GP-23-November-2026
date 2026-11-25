"""MVP testing page. Respect docs/constraints.md."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import config


def render() -> None:
    st.title("MVP Testing")
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
