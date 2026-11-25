"""Run a real, deterministic tool-choice audit of Home Care Companion.

These are *system self-checks*, not user tests. Expected routes are a written
specification; actual routes come from running src.mvp.route_need. No user
observations or golden labels are fabricated. Respect docs/constraints.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from src import config, mvp

AUDIT_TASKS = [
    {"input": "gas smell in the kitchen", "expected_tool": "route_need", "expected_route": "SEEK_IMMEDIATE_HELP"},
    {"input": "sparking from the switchboard", "expected_tool": "route_need", "expected_route": "SEEK_IMMEDIATE_HELP"},
    {"input": "dust the AC filter myself", "expected_tool": "route_need", "expected_route": "DIY"},
    {"input": "wipe the vent with a cloth", "expected_tool": "route_need", "expected_route": "DIY"},
    {"input": "society watchman can arrange the plumber", "expected_tool": "route_need", "expected_route": "LOCAL_OR_NEIGHBOUR"},
    {"input": "my neighbour recommended a local electrician", "expected_tool": "route_need", "expected_route": "LOCAL_OR_NEIGHBOUR"},
    {"input": "AC not cooling for two days", "expected_tool": "public_reference_lookup", "expected_route": "UC_CATEGORY"},
    {"input": "kitchen tap leaking continuously", "expected_tool": "public_reference_lookup", "expected_route": "UC_CATEGORY"},
    {"input": "it is acting weird", "expected_tool": "ask_clarifying_question", "expected_route": "WAIT_AND_WATCH"},
    {"input": "help", "expected_tool": "ask_clarifying_question", "expected_route": "WAIT_AND_WATCH"},
    {"input": "mattress deep cleaning once a year", "expected_tool": "public_reference_lookup", "expected_route": "UC_CATEGORY"},
    {"input": "pest control before monsoon", "expected_tool": "public_reference_lookup", "expected_route": "UC_CATEGORY"},
]


def run() -> dict:
    config.ensure_dirs()
    original_trace = config.TOOL_TRACE
    config.TOOL_TRACE = config.OUTPUTS_DIR / "audit_trace.jsonl"
    rows = []
    try:
        for idx, task in enumerate(AUDIT_TASKS, start=1):
            result = mvp.route_need(task["input"], session_hash=f"audit-{idx:02d}")
            trace = result.get("tool_trace", {})
            rows.append({
                "task": idx,
                "input": task["input"],
                "expected_tool": task["expected_tool"],
                "actual_tool": trace.get("chosen_tool", ""),
                "expected_route": task["expected_route"],
                "actual_route": result.get("route", ""),
                "confidence": result.get("confidence", 0),
                "tool_match": trace.get("chosen_tool") == task["expected_tool"],
                "route_match": result.get("route") == task["expected_route"],
            })
    finally:
        config.TOOL_TRACE = original_trace

    tools = sorted({r["expected_tool"] for r in rows} | {r["actual_tool"] for r in rows})
    per_tool = {}
    for tool in tools:
        tp = sum(1 for r in rows if r["expected_tool"] == tool and r["actual_tool"] == tool)
        fp = sum(1 for r in rows if r["expected_tool"] != tool and r["actual_tool"] == tool)
        fn = sum(1 for r in rows if r["expected_tool"] == tool and r["actual_tool"] != tool)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        per_tool[tool] = {
            "tp": tp, "fp": fp, "fn": fn,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(2 * precision * recall / (precision + recall), 3) if precision + recall else 0.0,
        }

    n = max(1, len(rows))
    route_match = sum(1 for r in rows if r["route_match"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_type": "deterministic system self-check (not user testing)",
        "n_tasks": len(rows),
        "tool_accuracy_pct": round(100 * sum(1 for r in rows if r["tool_match"]) / n, 1),
        "route_accuracy_pct": round(100 * route_match / n, 1),
        "no_action_route_pct": round(100 * sum(1 for r in rows if r["actual_route"] == "WAIT_AND_WATCH") / n, 1),
        "incorrect_route_pct": round(100 * (n - route_match) / n, 1),
        "per_tool": per_tool,
        "rows": rows,
        "limitation": "Expected routes are a specification written by the team; this audit checks the deterministic router only, not real user outcomes.",
    }
    out = config.OUTPUTS_DIR / "audit_results.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = run()
    print(f"tasks={rep['n_tasks']} tool_accuracy={rep['tool_accuracy_pct']}% route_accuracy={rep['route_accuracy_pct']}%")
    print(f"no_action={rep['no_action_route_pct']}% incorrect_route={rep['incorrect_route_pct']}%")
    print(f"saved {config.OUTPUTS_DIR / 'audit_results.json'}")
