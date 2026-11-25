"""Success metrics and guardrails page. Respect docs/constraints.md (C4, C5)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src import config


def render() -> None:
    st.title("Success Metrics")
    st.caption("Measure continuity value without incentives, spam, or account actions.")

    st.subheader("Metric ladder")
    st.info(config.METRIC_DEFINITION)

    metrics = pd.DataFrame([
        {
            "type": "Business metric",
            "metric": "90-day repeat completion rate (eligible anchor customers)",
            "definition": "Share of eligible anchor customers completing another booking in any category within 90 days.",
            "rationale": "Core business outcome; repeat drives NTV.",
            "target": "Directional lift vs baseline (TBD with real data)",
            "measurement_source": "Product analytics / experiment readout (internal when available); MVP uses proxy signals only.",
        },
        {
            "type": "Leading indicator",
            "metric": "Calendar engagement rate",
            "definition": "% of MVP users who build calendar and save/add at least one need.",
            "rationale": "Indicates planning value.",
            "target": ">=40% in pilot",
            "measurement_source": "MVP session events / feedback.",
        },
        {
            "type": "Leading indicator",
            "metric": "Need Decider resolution rate",
            "definition": "% of turns with confident route or useful clarifying question.",
            "rationale": "Measures decision confidence support.",
            "target": ">=70%",
            "measurement_source": "tool_trace.jsonl + user feedback.",
        },
        {
            "type": "Leading indicator",
            "metric": "Reflection checklist download rate",
            "definition": "% of Step 4 users who download checklist.",
            "rationale": "Captures post-service closure intent.",
            "target": ">=25%",
            "measurement_source": "MVP UI event/log.",
        },
        {
            "type": "Guardrail",
            "metric": "False-urgency / bad-route rate",
            "definition": "% of tested golden tasks with wrong route or unsafe suggestion.",
            "rationale": "Avoid harmful or pushy guidance.",
            "target": "<10%",
            "measurement_source": "Golden task audit.",
        },
        {
            "type": "Guardrail",
            "metric": "No-need respect rate",
            "definition": "% of no-need cases where system recommends wait/watch or no action appropriately.",
            "rationale": "Avoid creating false need.",
            "target": ">=90%",
            "measurement_source": "Golden task audit + interviews.",
        },
    ])
    st.dataframe(metrics, width="stretch", hide_index=True)

    st.subheader("AI performance metrics (R7)")
    st.caption(
        "Defined but not yet computed — pending the labelled golden-task audit and real user tests. "
        "No accuracy figure is claimed before measurement."
    )
    ai_metrics = pd.DataFrame([
        {
            "metric": "AI recommendation accuracy",
            "definition": "Share of coded AI outputs that match human labels on the golden set.",
            "measurement_method": "Compare engine output with manually labelled rows in data/golden_set.csv.",
            "target": "TBD after baseline; must be reported honestly",
            "rationale": "Validate AI insights instead of accepting them blindly.",
            "status": "Pending 20 manual labels",
        },
        {
            "metric": "Correct tool choice at the right moment",
            "definition": "Share of turns where the chosen tool matches the expected tool for that need.",
            "measurement_method": "outputs/tool_trace.jsonl against the 10 golden tasks below.",
            "target": "TBD after audit",
            "rationale": "The agent must select the right tool, not just a plausible one.",
            "status": "Pending golden-task audit",
        },
        {
            "metric": "No-action recognition",
            "definition": "Share of no-need cases routed to WAIT_AND_WATCH or a clarifying question.",
            "measurement_method": "Golden tasks with no actionable need; tool-trace review.",
            "target": "TBD after audit",
            "rationale": "Recognise when no recommendation is required; avoid false demand.",
            "status": "Pending golden-task audit",
        },
        {
            "metric": "Incorrect / unnecessary recommendation rate",
            "definition": "Share of turns with a wrong, unsafe, or pushy recommendation.",
            "measurement_method": "Trace audit plus 'matched real need' user feedback.",
            "target": "TBD; drive toward zero for unsafe cases",
            "rationale": "Guardrail against unnecessary bookings and misleading guidance.",
            "status": "Pending audit and user tests",
        },
    ])
    st.dataframe(ai_metrics, width="stretch", hide_index=True)

    st.subheader("Tool-choice golden tasks (10)")
    golden_tasks = pd.DataFrame([
        {"task": "AC not cooling before summer", "expected_tool": "public_reference_lookup/route_need", "expected_route": "UC_CATEGORY"},
        {"task": "Tap dripping slowly", "expected_tool": "route_need", "expected_route": "UC_CATEGORY/LOCAL_OR_NEIGHBOUR"},
        {"task": "Something feels off in my kitchen but not sure what", "expected_tool": "ask_clarifying_question", "expected_route": "WAIT_AND_WATCH + clarifying"},
        {"task": "Gas smell near stove", "expected_tool": "route_need", "expected_route": "SEEK_IMMEDIATE_HELP"},
        {"task": "Need to clean AC filter", "expected_tool": "route_need", "expected_route": "DIY"},
        {"task": "Society wants common-area electrician", "expected_tool": "route_need", "expected_route": "LOCAL_OR_NEIGHBOUR"},
        {"task": "Plan next 90 days after AC service", "expected_tool": "build_calendar", "expected_route": "CALENDAR"},
        {"task": "What did I notice after cleaning service?", "expected_tool": "capture_reflection", "expected_route": "REFLECTION"},
        {"task": "Do I need pest control before monsoon?", "expected_tool": "public_reference_lookup/route_need", "expected_route": "UC_CATEGORY or WAIT_AND_WATCH"},
        {"task": "No issue right now", "expected_tool": "ask_clarifying_question/show_public_info", "expected_route": "WAIT_AND_WATCH"},
    ])
    st.dataframe(golden_tasks, width="stretch", hide_index=True)

    st.markdown("**Precision/recall of tool choice:** compute against labelled golden tasks once run. Report per-tool precision/recall and overall accuracy. Not yet computed — pending the labelled golden-task audit; no accuracy figure is claimed.")
    st.code("precision = TP / (TP + FP)\nrecall = TP / (TP + FN)\nReport per tool and macro average.", language="text")

    st.subheader("3 anti-nudge guardrails")
    st.markdown(
        """
        1. **Non-UC route rate:** Track % of recommendations that are DIY/local/wait/immediate-help. A healthy system should not push UC for every case.
        2. **No-need rate:** Track % of sessions where the appropriate outcome is no action/wait. System must respect no-need.
        3. **2-week "did I actually need it?" follow-up:** Optional opt-in check (outside MVP transactions) to measure false positives and trust. No booking prompts.
        """
    )


render()
