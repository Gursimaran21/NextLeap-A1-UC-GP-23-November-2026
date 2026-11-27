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
    ("Care plan", "Next-cycle care plan"),
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
    "CARE_PLAN": (
        "A single route today is less useful than a private care plan built from public guidance."
    ),
    "CONTINUITY": (
        "A new route today is not needed; a private reflection and review window carry the continuity."
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

# Guidance-only templates for next-cycle care plans. Every item is a private
# planning cue; none of these fields creates an external action.
_CARE_PLAN_LIBRARY: dict[str, dict[str, Any]] = {
    "AC Service": {
        "watch_for": [
            "Reduced cooling or airflow that feels weaker than usual",
            "Dust build-up near vents or filters",
            "Unusual noise or water leakage from the unit",
        ],
        "note_down": [
            "When the change in cooling started",
            "Which rooms feel most affected",
            "Whether filters were cleaned recently",
        ],
        "review": [("AC filter cleaning", 30), ("AC servicing", 180)],
        "cues": [
            {
                "signal": "Dusty airflow or reduced cooling",
                "category": "AC Service",
                "basis": "Public AC maintenance guidance",
                "confidence": 0.78,
            },
            {
                "signal": "Unusual noise or water leakage",
                "category": "Appliance Repair",
                "basis": "Public electrical and appliance safety guidance",
                "confidence": 0.62,
            },
        ],
        "adjacent": ["Deep Cleaning", "Pest Control"],
        "decision_questions": [
            "What exactly did the previous service cover?",
            "What changed after the service?",
            "Is this a routine check or a safety concern?",
        ],
    },
    "Deep Cleaning": {
        "watch_for": [
            "Dust returning quickly in high-use rooms",
            "Allergy symptoms or musty smells from soft furnishings",
            "Kitchen or bathroom areas needing a reset",
        ],
        "note_down": [
            "Which rooms matter most to you",
            "Any allergy or sensitivity triggers",
            "What you already handle yourself",
        ],
        "review": [("Mattress/sofa cleaning", 180), ("Deep home cleaning", 120)],
        "cues": [
            {
                "signal": "Allergy symptoms or dusty soft furnishings",
                "category": "Deep Cleaning",
                "basis": "Public indoor-allergen guidance",
                "confidence": 0.7,
            },
            {
                "signal": "Slow drainage or damp smell",
                "category": "Plumbing",
                "basis": "Public water and drain maintenance guidance",
                "confidence": 0.6,
            },
        ],
        "adjacent": ["Pest Control", "Plumbing"],
        "decision_questions": [
            "Which areas actually need attention?",
            "What can be handled with your own routine?",
            "Is there a health or safety reason to act sooner?",
        ],
    },
    "Plumbing": {
        "watch_for": [
            "Damp patches or higher-than-usual water use",
            "Slow drainage or recurring odour",
            "Drips that return after a previous fix",
        ],
        "note_down": [
            "Where you noticed the issue",
            "Whether it is constant or intermittent",
            "What was fixed previously",
        ],
        "review": [("Plumbing leak check", 60), ("Bathroom/kitchen drain check", 90)],
        "cues": [
            {
                "signal": "Dampness or higher water use",
                "category": "Plumbing",
                "basis": "Public leak-prevention guidance",
                "confidence": 0.76,
            },
            {
                "signal": "Slow drainage with odour",
                "category": "Plumbing",
                "basis": "Public drain-maintenance guidance",
                "confidence": 0.68,
            },
        ],
        "adjacent": ["Deep Cleaning", "Appliance Repair"],
        "decision_questions": [
            "Is the issue small and local, or spreading?",
            "Can you safely pause use until it is reviewed?",
            "What scope would you want clarified first?",
        ],
    },
    "Pest Control": {
        "watch_for": [
            "Visible insects or recurring sightings",
            "Humid corners or moisture build-up",
            "Signs of activity after rainy periods",
        ],
        "note_down": [
            "Where sightings happen most",
            "Whether activity is seasonal",
            "Any steps already taken",
        ],
        "review": [("Pest control inspection", 120)],
        "cues": [
            {
                "signal": "Humidity or visible insects",
                "category": "Pest Control",
                "basis": "Public pest-prevention guidance",
                "confidence": 0.7,
            },
            {
                "signal": "Moisture near walls or drains",
                "category": "Plumbing",
                "basis": "Public moisture and leak guidance",
                "confidence": 0.58,
            },
        ],
        "adjacent": ["Deep Cleaning", "Plumbing"],
        "decision_questions": [
            "Is this a one-off sighting or a pattern?",
            "What prevention steps are already in place?",
            "Would an inspection clarify the cause?",
        ],
    },
    "Appliance Repair": {
        "watch_for": [
            "Unusual noise, weak performance or vibration",
            "Burning smell, sparks or loose wiring signs",
            "Reduced cooling or flow in a major appliance",
        ],
        "note_down": [
            "Which appliance is affected",
            "When the symptom started",
            "Any warning signs you observed",
        ],
        "review": [("Appliance safety check", 7), ("Refrigerator coil cleaning", 180), ("Kitchen chimney/filter cleaning", 90)],
        "cues": [
            {
                "signal": "Sparks, burning smell or unusual noise",
                "category": "Appliance Repair",
                "basis": "Public electrical safety guidance",
                "confidence": 0.86,
            },
            {
                "signal": "Reduced cooling or airflow",
                "category": "AC Service",
                "basis": "Public appliance efficiency guidance",
                "confidence": 0.6,
            },
        ],
        "adjacent": ["AC Service", "Plumbing"],
        "decision_questions": [
            "Is there a safety warning sign?",
            "What did the earlier service actually cover?",
            "Do you need a routine check or a safety review?",
        ],
    },
    "Salon": {
        "watch_for": [
            "A personal-care need you have been postponing",
            "A pre-planned occasion or routine preference",
            "Comfort with at-home service versus your own routine",
        ],
        "note_down": [
            "What you usually prefer",
            "When you last felt satisfied",
            "Whether this is planned or spontaneous",
        ],
        "review": [],
        "cues": [],
        "adjacent": ["Deep Cleaning"],
        "decision_questions": [
            "Is this a planned need or a mood-based choice?",
            "What outcome matters most to you?",
            "Would your own routine be enough this time?",
        ],
    },
}

CARE_PLAN_CATEGORIES = list(_CARE_PLAN_LIBRARY.keys())

_ROUTE_GUIDE = [
    {
        "route": "DIY",
        "fits": "Small, low-risk routine tasks you are comfortable handling",
        "caution": "Stop if there is any safety warning sign",
    },
    {
        "route": "Local help",
        "fits": "Familiar help for quick or building-level tasks",
        "caution": "Scope and reliability can vary",
    },
    {
        "route": "Professional service",
        "fits": "Recurring, technical or safety-related needs",
        "caution": "Clarify the scope and expectations first",
    },
]

_GENERIC_CARE_PLAN: dict[str, Any] = {
    "watch_for": ["A change that keeps recurring", "A task you keep putting off"],
    "note_down": ["What you noticed", "When you noticed it"],
    "review": [],
    "cues": [],
    "adjacent": CARE_PLAN_CATEGORIES,
    "decision_questions": [
        "What exactly changed at home?",
        "Is this routine, urgent or simply planned?",
        "What information would help you decide calmly?",
    ],
}


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


_SOURCE_CLASS_WEIGHT = {
    "public_guidance": 0.86,
    "manufacturer_guidance": 0.82,
    "customer_input": 0.40,
}
_FRESHNESS_WEIGHT = {
    "updated_2025-01": 0.95,
    "checked_2026-11": 0.88,
    "search_indexed_2026-11": 0.68,
    "blocked_2026-11": 0.52,
    "not_recorded": 0.55,
}
_MATCH_WEIGHT = {
    "exact": 0.95,
    "partial": 0.72,
    "category": 0.55,
    "template": 0.50,
    "none": 0.35,
}


def confidence_v2(source_class: str = "", freshness: str = "", match_strength: str = "") -> dict[str, Any]:
    """Score guidance using source class, freshness and source-to-need match."""
    sc = str(source_class or "customer_input").strip().lower()
    fr = str(freshness or "not_recorded").strip().lower()
    ms = str(match_strength or "template").strip().lower()
    source_w = float(_SOURCE_CLASS_WEIGHT.get(sc, 0.55))
    fresh_w = float(_FRESHNESS_WEIGHT.get(fr, 0.55))
    match_w = float(_MATCH_WEIGHT.get(ms, 0.50))
    score = round(min(0.95, max(0.20, 0.45 * source_w + 0.25 * fresh_w + 0.30 * match_w)), 2)
    label = "higher" if score >= 0.80 else "moderate" if score >= 0.60 else "low"
    return {
        "score": score,
        "label": label,
        "source_class": sc,
        "freshness": fr,
        "match_strength": ms,
        "source_class_weight": round(source_w, 2),
        "freshness_weight": round(fresh_w, 2),
        "match_weight": round(match_w, 2),
    }


_COVERAGE_STYLES = {
    "exact": ("Strong public basis", "#EAF6EE", "#1F5130", "#BFE3C8"),
    "partial": ("Partial public basis", "#FFF4E5", "#7A4B00", "#F0D9A8"),
    "category": ("Category-level basis", "#EBDFF0", "#500C6B", "#D9C6E0"),
    "template": ("No public basis", "#F8F9FA", "#7A858D", "#E3E6E8"),
    "none": ("No public basis", "#F8F9FA", "#7A858D", "#E3E6E8"),
}


def coverage_badge(match_strength: str = "", freshness: str = "", source_url: str = "") -> dict[str, str]:
    """Return a small, honest coverage label for one public-guidance cue."""
    ms = str(match_strength or "template").strip().lower()
    label, bg, fg, border = _COVERAGE_STYLES.get(ms, _COVERAGE_STYLES["template"])
    fr = str(freshness or "not_recorded").strip().lower()
    if not source_url:
        note = "No source link recorded. Use your own notes."
    elif fr == "blocked_2026-11":
        note = "Source link check was blocked; treat this as partial basis."
    elif fr == "search_indexed_2026-11":
        note = "Source found in a public search index; direct fetch was not confirmed."
    elif fr == "updated_2025-01":
        note = "Source page dated 2025-01-31."
    elif fr == "checked_2026-11":
        note = "Source link checked 2026-11."
    else:
        note = "Freshness not recorded."
    return {
        "label": label,
        "bg": bg,
        "fg": fg,
        "border": border,
        "note": note,
        "match_strength": ms,
    }


def _reference_lookup() -> dict[str, dict[str, str]]:
    """Return public timing references keyed by need, without any network call."""
    try:
        ref = mvp.load_public_reference()
    except Exception:
        return {}
    out: dict[str, dict[str, str]] = {}
    for _, row in ref.iterrows():
        key = str(row.get("need", "") or "").strip().lower()
        if not key:
            continue
        out[key] = {
            "trigger": str(row.get("trigger", "") or ""),
            "basis": str(row.get("public_basis", "") or ""),
            "source_url": str(row.get("source_url", "") or ""),
            "source_class": str(row.get("source_class", "") or ""),
            "freshness": str(row.get("freshness", "") or "not_recorded"),
            "match_strength": str(row.get("match_strength", "") or "partial"),
        }
    return out


def care_plan(category: str = "", session_hash: str = "") -> dict[str, Any]:
    """Build a guidance-only next-cycle care plan from a self-reported service.

    The plan stays private. It uses public timing references and the category the
    user selected; it never checks account history or takes an external action.
    """
    requested = str(category or "").strip()
    matched = requested if requested in _CARE_PLAN_LIBRARY else (_service_match(requested)[0] or "")
    template = _CARE_PLAN_LIBRARY.get(matched, _GENERIC_CARE_PLAN)
    lookup = _reference_lookup()

    reviews: list[dict[str, Any]] = []
    for need, days in template.get("review", []):
        info = lookup.get(str(need).strip().lower(), {})
        reviews.append({
            "need": str(need),
            "days": int(days),
            "trigger": info.get("trigger", ""),
            "basis": info.get("basis", ""),
            "source_url": info.get("source_url", ""),
            "source_class": info.get("source_class", ""),
            "freshness": info.get("freshness", "not_recorded"),
            "match_strength": info.get("match_strength", "partial"),
        })

    guide_row = next(
        (
            row
            for row in mvp.category_guide()
            if str(row.get("category", "")).lower() == matched.lower()
        ),
        {},
    )
    source_url = str(guide_row.get("source_url", "") or (reviews[0]["source_url"] if reviews else ""))
    basis = str(guide_row.get("covers", "") or (reviews[0]["basis"] if reviews else "Your own observation"))
    source_class = str(reviews[0].get("source_class", "") or ("public_guidance" if source_url else "customer_input"))
    freshness = str(reviews[0].get("freshness", "") or "not_recorded") if reviews else "not_recorded"
    match_strength = str(reviews[0].get("match_strength", "") or ("category" if source_url else "template"))
    confidence_parts = confidence_v2(source_class, freshness, match_strength)
    confidence = float(confidence_parts["score"])

    watch = [guard(str(x)) for x in template.get("watch_for", [])]
    note = [guard(str(x)) for x in template.get("note_down", [])]
    cues = [
        {
            "signal": guard(str(c.get("signal", ""))),
            "category": guard(str(c.get("category", ""))),
            "basis": guard(str(c.get("basis", ""))),
            "confidence": round(min(float(c.get("confidence", 0.5)), confidence), 2),
        }
        for c in template.get("cues", [])
    ]
    questions = [guard(str(q)) for q in template.get("decision_questions", [])]

    steps: list[str] = [f"Watch for: {x}" for x in watch]
    steps.extend(f"Note down: {x}" for x in note)
    steps.extend(
        f"Review around {r['days']} day(s): {r['need']} - {r['basis'] or 'public timing guidance'}"
        for r in reviews
    )
    steps.extend(f"Decision question: {q}" for q in questions)

    plan_item = None
    if reviews:
        first = reviews[0]
        plan_item = {
            "need": first["need"],
            "status": "Review window",
            "due_in_days": first["days"],
            "why": f"A private review cue after the {matched.lower()} you told us about.",
            "basis": first["basis"] or "Public timing guidance.",
            "source_url": first["source_url"],
            "confidence": round(confidence, 2),
            "route_hint": "CARE_PLAN",
            "evidence": "customer input plus public guidance",
            "coverage": coverage_badge(first["match_strength"], first["freshness"], first["source_url"]),
        }

    label = matched or "your home"
    reason = ensure_why_not(
        (
            f"Here is a private next-cycle care plan for {label}. "
            "Watch for the signals, note what matters to you, and use the review window as a prompt to check your own situation. "
            "This is public guidance plus what you told us; no external action is taken here."
        ),
        "CARE_PLAN",
    )
    why = (
        f"Why this guidance: {basis}. "
        f"Source class: {source_class}. "
        f"Freshness: {freshness}. "
        f"Source-to-need match: {match_strength}. "
        f"Confidence basis: {confidence_parts['label']} ({confidence:.2f}) from source class, freshness and match. "
        + (f"Public source: {source_url}. " if source_url else "No public source was available for this item. ")
        + "The service name came from what you selected in this session."
    )
    return {
        "category": label,
        "watch_for": watch,
        "note_down": note,
        "review": reviews,
        "need_cues": cues,
        "adjacent_categories": [guard(str(x)) for x in template.get("adjacent", [])],
        "decision_questions": questions,
        "route_guide": _ROUTE_GUIDE,
        "source_url": source_url,
        "basis": basis,
        "source_class": source_class,
        "freshness": freshness,
        "match_strength": match_strength,
        "confidence": round(confidence, 2),
        "confidence_parts": confidence_parts,
        "reason": guard(reason),
        "why": guard(why),
        "steps": [guard(s) for s in steps],
        "plan_item": plan_item,
    }


def guided_intake_plan(answers: dict[str, Any] | None = None, session_hash: str = "") -> dict[str, Any]:
    """Tailor a care plan from three session-only intake answers."""
    data = dict(answers or {})
    category = str(data.get("category", "") or "").strip()
    change = guard(str(data.get("change", "") or "").strip()[:120])
    timing = str(data.get("timing", "Routine") or "Routine").strip()
    plan = care_plan(category, session_hash=session_hash)
    plan["intake"] = {"category": category, "change": change, "timing": timing}

    lowered = timing.lower()
    if "urgent" in lowered or lowered.startswith("possible"):
        reason = ensure_why_not(
            (
                "Because you marked possible urgency, this plan pauses category suggestions. "
                "Use immediate help for a possible hazard; no DIY or service route is recommended from this answer."
            ),
            "SEEK_IMMEDIATE_HELP",
        )
        urgent_conf = confidence_v2("customer_input", "not_recorded", "none")
        plan.update({
            "route": "SEEK_IMMEDIATE_HELP",
            "confidence": urgent_conf["score"],
            "confidence_parts": urgent_conf,
            "source_class": "customer_input",
            "freshness": "not_recorded",
            "match_strength": "none",
            "source_url": "",
            "watch_for": [guard("Safety warning signs you should not ignore")],
            "note_down": [guard("Only what you observed, without personal details")],
            "review": [],
            "need_cues": [],
            "decision_questions": [guard("Is anyone at risk right now?")],
            "steps": [
                guard("Pause category suggestions."),
                guard("Use immediate help if there is a hazard."),
                guard("You can return for a care plan once the situation is stable."),
            ],
            "reason": guard(reason),
            "why": guard(
                "Why this guidance: your urgency answer controls the route. "
                "Safety comes before planning, and no external action is taken here."
            ),
            "plan_item": None,
            "intake_paused": True,
        })
        return plan

    if change:
        plan["watch_for"] = [guard(f"Your note: {change}")] + list(plan.get("watch_for", []))
    plan["note_down"] = [
        guard("Whether the change is still present"),
        guard("What you observed without personal details"),
    ] + list(plan.get("note_down", []))
    plan["decision_questions"] = list(plan.get("decision_questions", [])) + [
        guard("Did the change match what was explained to you?")
    ]
    if not lowered.startswith("routine"):
        plan["review"] = sorted(list(plan.get("review", [])), key=lambda x: -int(x.get("days", 0)))[:1]

    detail = f" Your note was: {change}." if change else " You did not add an extra change note."
    plan["reason"] = guard(ensure_why_not(
        (
            f"Here is a private care plan for {plan['category']} based on your three answers. "
            f"Timing answer: {timing}.{detail} "
            "Use the watch list and review window as prompts to check your own situation; no external action is taken here."
        ),
        "CARE_PLAN",
    ))
    plan["why"] = guard(str(plan.get("why", "")) + " The plan was tailored by your three intake answers.")
    plan["steps"] = [guard(f"Watch for: {x}") for x in plan.get("watch_for", [])]
    plan["steps"].extend(guard(f"Note down: {x}") for x in plan.get("note_down", []))
    plan["steps"].extend(
        guard(f"Review around {r['days']} day(s): {r['need']}") for r in plan.get("review", [])
    )
    plan["steps"].extend(guard(f"Decision question: {q}") for q in plan.get("decision_questions", []))
    plan["intake_paused"] = False
    return plan


def continuity_loop(
    reflection: dict[str, Any] | None = None,
    care_plan_data: dict[str, Any] | None = None,
    text: str = "",
    session_hash: str = "",
) -> dict[str, Any]:
    """Turn a reflection and optional care plan into a private continuity loop."""
    ref = dict(reflection or {})
    cp = dict(care_plan_data or {})
    detected, _, _ = _service_match(str(text or ""))
    completed = str(cp.get("category") or detected or "the service you completed")

    monitor = [guard(str(x)) for x in cp.get("watch_for", [])]
    if not monitor:
        monitor = [
            guard(f"Changes around {str(topic).lower()}")
            for topic in ref.get("open_topics", [])[:3]
        ]
    if not monitor:
        monitor = [guard("Any change that keeps recurring")]

    notes = [guard(str(x)) for x in cp.get("note_down", [])]
    if not notes:
        notes = [
            guard("What was completed"),
            guard("What changed afterwards"),
            guard("What you want to remember next time"),
        ]

    reviews = list(cp.get("review", []))
    if reviews:
        first = reviews[0]
        review_window = guard(f"About {int(first.get('days', 90))} day(s): {first.get('need', 'private review')}")
        plan_item = {
            "need": str(first.get("need", "Private review note")),
            "status": "Review window",
            "due_in_days": int(first.get("days", 90)),
            "why": guard(f"A private review cue after the {completed.lower()} you reflected on."),
            "basis": str(first.get("basis", "") or "Public timing guidance."),
            "source_url": str(first.get("source_url", "") or ""),
            "confidence": round(float(cp.get("confidence", 0.45) or 0.45), 2),
            "route_hint": "CONTINUITY",
            "evidence": "customer reflection plus public guidance",
            "coverage": coverage_badge(
                first.get("match_strength", ""), first.get("freshness", ""), first.get("source_url", "")
            ),
        }
    else:
        review_window = guard("Use your own notes; review within 30-90 days if a change appears.")
        plan_item = {
            "need": "Private review note",
            "status": "Review window",
            "due_in_days": 90,
            "why": guard(f"A private review cue after the {completed.lower()} you reflected on."),
            "basis": "Your reflection; no public timing cue was available.",
            "source_url": "",
            "confidence": 0.40,
            "route_hint": "CONTINUITY",
            "evidence": "customer reflection",
            "coverage": coverage_badge("none", "not_recorded", ""),
        }

    reason = ensure_why_not(
        (
            f"Private continuity loop for {completed}. Monitor the watch items, keep the notes local, "
            "and use the review window only as a prompt to check your own situation. No external action is taken here."
        ),
        "CONTINUITY",
    )
    followup = str(ref.get("followup_question", "") or "What home need might come up next based on what you noticed?")
    return {
        "completed_service": guard(completed),
        "monitor": monitor[:4],
        "private_notes": notes[:4],
        "review_window": review_window,
        "followup_question": guard(followup),
        "confidence": round(float(cp.get("confidence", 0.45) or 0.45), 2),
        "reason": guard(reason),
        "why": guard(
            "Why this guidance: built from your reflection and, when available, the care plan from this session. "
            "It stays private and does not contact anyone."
        ),
        "plan_item": plan_item,
        "reflection_topics": [guard(str(x)) for x in ref.get("open_topics", [])],
        "source_url": str(cp.get("source_url", "") or ""),
        "session_hash": session_hash,
    }


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

    if lowered_mode == "care plan":
        selected = _service_match(text)[0] or ""
        if not selected and plan:
            selected = _service_match(str(plan[0].get("need", "")))[0] or ""
        cp = care_plan(selected, session_hash=session_hash)
        category_info = (
            f"{cp['why']} "
            f"Watch for: {', '.join(cp['watch_for'][:2])}. "
            f"Note down: {', '.join(cp['note_down'][:2])}."
        )
        return _result(
            tool="insta_talk_care_plan",
            route="CARE_PLAN",
            confidence=float(cp["confidence"]),
            reason=str(cp["reason"]),
            session_hash=session_hash,
            category=str(cp["category"]),
            source_url=str(cp["source_url"]),
            basis=str(cp["basis"]),
            category_info=category_info,
            steps=list(cp["steps"]),
            questions=list(cp["decision_questions"]),
            plan_item=cp.get("plan_item"),
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
