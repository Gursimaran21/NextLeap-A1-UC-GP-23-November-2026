"""Deterministic guidance layer for Insta Talk.

This module provides public-information guidance only. It never creates a
transaction, contacts an external service, or changes account state.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from . import config, mvp


TALK_MODES = [
    ("Explain", "Explain a service area"),
    ("Decide", "Decide my next step"),
    ("Prepare", "Prepare for a service"),
    ("Aftercare", "Aftercare check"),
    ("No action", "No service needed right now"),
    ("Next 90 days", "What should I plan next?"),
]

_WHY_NOT = {
    "SEEK_IMMEDIATE_HELP": (
        "DIY, local help, and service categories are not safe first steps for a possible hazard."
    ),
    "NO_ACTION": (
        "A reminder or suggestion would add noise when you have said no service is needed."
    ),
    "WAIT_AND_WATCH": (
        "DIY or a category suggestion could be mismatched without clearer symptoms."
    ),
    "DIY": (
        "Local or category help may be unnecessary for a simple, routine task."
    ),
    "LOCAL_OR_NEIGHBOUR": (
        "DIY may not be permitted or safe, and a service category may not fit a building-level task."
    ),
    "UC_CATEGORY": (
        "DIY may miss a root cause, local help may vary, and waiting may let the issue grow."
    ),
    "PREPARE": (
        "A route decision is not needed yet; readiness is the useful next step."
    ),
    "AFTERCARE": (
        "A new route is not needed yet; observation and a private checklist come first."
    ),
    "PLAN": (
        "A single route today is less useful than a private 90-day view."
    ),
    "PLAN_CUE": (
        "A route today is not required; this is only a private planning cue."
    ),
}

_GENERIC_GUIDANCE = (
    "I don’t have enough public information to guide this safely. "
    "Tell me which service area or symptom you mean, and I will stay within public guidance."
)

_UNSUPPORTED = ("insta help", "native", "international", "beauty", "wellness")

_MONTHS_RE = re.compile(r"\b(\d{1,2})\s*(?:-|to)?\s*(months?)\b", re.I)
_WEEKS_RE = re.compile(r"\b(\d{1,2})\s*(?:-|to)?\s*(weeks?)\b", re.I)

_SPEECH_NEEDS = [
    ("AC service", ("ac", "air conditioner", "cooling")),
    ("Deep cleaning", ("deep clean", "cleaning", "sofa", "bathroom clean", "kitchen clean")),
    ("Plumbing", ("tap", "leak", "pipe", "drain", "plumbing")),
    ("Pest control", ("pest", "cockroach", "ants", "termite")),
    ("Appliance repair", ("fridge", "washing machine", "geyser", "appliance")),
    ("Salon", ("salon", "haircut", "facial", "grooming")),
]


def guard(text: str) -> str:
    """Return a safe fallback if generated text contains a prohibited pattern."""
    safe = str(text or "").strip()
    lowered = safe.lower()
    for pattern in config.FORBIDDEN_PATTERNS:
        if pattern and pattern in lowered:
            return (
                "I can only share public guidance and private planning cues here. "
                "I can’t help with that part."
            )
    return safe


def why_not(route: str) -> str:
    """Explain why alternative routes were not preferred."""
    return guard(_WHY_NOT.get(str(route), "Other routes need more context before being suggested."))


def ensure_why_not(reason: str, route: str) -> str:
    """Append a why-not line when the base route result does not include one."""
    base = str(reason or "").strip()
    if "why not other routes" in base.lower():
        return guard(base)
    return guard(f"{base} Why not other routes: {why_not(route)}")


def _trace(tool: str, reason: str, route: str, confidence: float, session_hash: str) -> dict[str, Any]:
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "session_hash": session_hash or "local-session",
        "turn": 0,
        "chosen_tool": tool,
        "reason": reason,
        "user_input_length": len(reason),
        "route": route,
        "confidence": round(float(confidence), 2),
    }


def _result(
    *,
    tool: str,
    route: str,
    confidence: float,
    reason: str,
    session_hash: str,
    category: str = "",
    source_url: str = "",
    basis: str = "",
    category_info: str = "",
    steps: list[str] | None = None,
    questions: list[str] | None = None,
    plan_item: dict[str, Any] | None = None,
) -> dict[str, Any]:
    reason = ensure_why_not(reason, route)
    result: dict[str, Any] = {
        "route": route,
        "confidence": round(float(confidence), 2),
        "reason": reason,
        "clarifying_questions": list(questions or []),
        "used_public_reference": bool(source_url),
        "public_reference": (
            {"category": category, "basis": basis, "source_url": source_url}
            if source_url
            else None
        ),
        "category_info": guard(category_info) if category_info else "",
        "steps": [guard(s) for s in (steps or [])],
        "tool_trace": _trace(tool, reason, route, confidence, session_hash),
    }
    if plan_item is not None:
        result["plan_item"] = plan_item
    return result


def _service_match(text: str) -> tuple[str | None, float, dict[str, str] | None]:
    category, confidence = mvp.match_core_category(text)
    if not category:
        return None, 0.0, None
    row = next(
        (
            item
            for item in mvp.category_guide()
            if item["category"].lower() == category.lower()
        ),
        None,
    )
    return category, confidence, row


def _unsupported(text: str) -> bool:
    lowered = str(text or "").lower()
    return any(token in lowered for token in _UNSUPPORTED)


def _relative_months(text: str) -> int | None:
    lowered = str(text or "").lower()
    months = _MONTHS_RE.search(lowered)
    if months:
        return int(months.group(1))
    weeks = _WEEKS_RE.search(lowered)
    if weeks:
        return max(1, round(int(weeks.group(1)) / 4))
    return None


def planning_cue(text: str, session_hash: str = "") -> dict[str, Any] | None:
    """Turn a spoken relative-timing note into a private planning cue."""
    lowered = str(text or "").lower()
    months = _relative_months(lowered)
    if months is None:
        return None

    need = ""
    for label, keywords in _SPEECH_NEEDS:
        if any(word in lowered for word in keywords):
            need = label
            break
    if not need:
        return None

    category, confidence, row = _service_match(need)
    source_url = str((row or {}).get("source_url", "") or "")
    basis = str((row or {}).get("covers", "") or "Public timing guidance.")
    status = "Soon" if months <= 6 else "Needs attention"
    cue = {
        "need": need,
        "status": status,
        "due_in_days": max(14, 30 * max(1, 6 - months)) if months <= 6 else 14,
        "why": f"You mentioned this was about {months} month(s) ago.",
        "basis": "Your spoken note plus public timing guidance.",
        "source_url": source_url,
        "confidence": 0.72,
        "route_hint": "PLAN_CUE",
        "evidence": "customer input plus public guidance",
    }
    reason = (
        f"This looks like a planning cue for {need.lower()}. "
        f"Basis: your input plus public timing guidance. "
        "Confidence: high. This is not a service requirement."
    )
    return _result(
        tool="insta_talk_planning_cue",
        route="PLAN_CUE",
        confidence=0.72,
        reason=reason,
        session_hash=session_hash,
        category=category or need,
        source_url=source_url,
        basis=basis,
        category_info="You can add this as a private reminder in Step 2.",
        questions=["Would you like this kept as a private reminder?"],
        plan_item=cue,
    )


def mode_response(
    mode: str,
    text: str,
    *,
    profile: dict[str, Any] | None = None,
    plan: list[dict[str, Any]] | None = None,
    session_hash: str = "",
) -> dict[str, Any]:
    """Produce a deterministic Insta Talk response for one talk mode."""
    profile = profile or {}
    plan = plan or []
    lowered_mode = str(mode or "").strip().lower()

    if lowered_mode == "no action":
        result = mvp.route_need(
            "No service needed right now.",
            profile=profile,
            llm=None,
            session_hash=session_hash,
        )
        result["reason"] = guard(
            "No action added. No reminder created. You can return if the situation changes. "
            f"Why not other routes: {why_not('NO_ACTION')}"
        )
        return result

    if lowered_mode == "decide":
        cue = planning_cue(text, session_hash=session_hash)
        if cue:
            return cue
        category, _, _ = _service_match(text)
        if not category and _unsupported(text):
            return _result(
                tool="insta_talk_decide",
                route="WAIT_AND_WATCH",
                confidence=0.2,
                reason=_GENERIC_GUIDANCE,
                session_hash=session_hash,
            )
        result = mvp.route_need(
            text or "I need help deciding",
            profile=profile,
            llm=None,
            session_hash=session_hash,
        )
        result["reason"] = ensure_why_not(result.get("reason", ""), str(result.get("route", "")))
        return result

    if lowered_mode == "next 90 days":
        if not plan:
            return _result(
                tool="insta_talk_next_90",
                route="PLAN",
                confidence=0.6,
                reason=(
                    "I don’t have a private 90-day view yet. Step 2 can build one from your "
                    "household history and public timing guidance."
                ),
                session_hash=session_hash,
            )
        names = ", ".join(str(item.get("need", "cue")) for item in plan[:4])
        return _result(
            tool="insta_talk_next_90",
            route="PLAN",
            confidence=0.8,
            reason=(
                f"Your private plan currently has {len(plan)} cue(s): {names}. "
                "These are planning cues only, drawn from your input and public guidance."
            ),
            session_hash=session_hash,
        )

    category, confidence, row = _service_match(text)

    if lowered_mode == "explain":
        if category and row:
            covers = str(row.get("covers", "") or "general household guidance")
            consider = str(row.get("consider_when", "") or "your own observation")
            return _result(
                tool="insta_talk_explain",
                route="UC_CATEGORY",
                confidence=confidence,
                reason=(
                    f"{category} usually covers {covers}. Consider it when {consider}. "
                    "This is public guidance only; no action is taken here."
                ),
                session_hash=session_hash,
                category=category,
                source_url=str(row.get("source_url", "") or ""),
                basis=covers,
                category_info=f"{category} is a service area with public guidance.",
            )
        if _unsupported(text):
            return _result(
                tool="insta_talk_explain",
                route="WAIT_AND_WATCH",
                confidence=0.2,
                reason=_GENERIC_GUIDANCE,
                session_hash=session_hash,
            )
        return _result(
            tool="insta_talk_explain",
            route="WAIT_AND_WATCH",
            confidence=0.2,
            reason=_GENERIC_GUIDANCE,
            session_hash=session_hash,
        )

    if lowered_mode == "prepare":
        if category and row:
            covers = str(row.get("covers", "") or "the service area")
            return _result(
                tool="insta_talk_prepare",
                route="PREPARE",
                confidence=max(0.65, confidence),
                reason=(
                    f"For {category.lower()}, a private readiness checklist can focus on {covers}. "
                    "Write down what you noticed, clear the area safely, and keep notes for yourself."
                ),
                session_hash=session_hash,
                category=category,
                source_url=str(row.get("source_url", "") or ""),
                basis=covers,
                steps=[
                    "Note what you observed and when it started.",
                    "Clear the area only if it is safe to do so.",
                    "Keep your own notes private and decide later what, if anything, you need.",
                ],
            )
        return _result(
            tool="insta_talk_prepare",
            route="PREPARE",
            confidence=0.3,
            reason=(
                "I can make a general readiness checklist, but I don’t have enough public "
                "information for a service-specific one yet."
            ),
            session_hash=session_hash,
            steps=[
                "Write down what you observed and when.",
                "Stop if there is any safety risk.",
                "Keep the note private and decide later.",
            ],
        )

    if lowered_mode == "aftercare":
        return _result(
            tool="insta_talk_aftercare",
            route="AFTERCARE",
            confidence=0.7,
            reason=(
                "After a service, a short private check helps you notice what changed. "
                "Use this to build continuity without taking any external action."
            ),
            session_hash=session_hash,
            category=category or "",
            source_url=str((row or {}).get("source_url", "") or ""),
            basis=str((row or {}).get("covers", "") or "your own observation"),
            steps=[
                "Write down what looks better and what still feels unresolved.",
                "Note anything you want to remember for the next 90 days.",
                "Keep the checklist private; no message is sent from this app.",
            ],
            questions=["What should I remember for next time?"],
        )

    return _result(
        tool="insta_talk",
        route="WAIT_AND_WATCH",
        confidence=0.2,
        reason=_GENERIC_GUIDANCE,
        session_hash=session_hash,
    )
